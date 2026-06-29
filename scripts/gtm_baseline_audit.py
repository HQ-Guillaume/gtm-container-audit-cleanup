#!/usr/bin/env python3
"""Build deterministic GTM cleanup baseline findings.

This script is intentionally mechanical. It creates the protected cleanup
baseline that semantic review must consume, enrich, downgrade, or reconcile.
It does not decide business purpose.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from gtm_lib import (
    container_version,
    custom_template_id,
    is_system_trigger_reference,
    is_system_variable_reference,
    refs,
    system_reference_description,
    trigger_group_members,
)

COMMON_IGNORED = {"accountId", "containerId", "fingerprint", "path"}
TAG_ID_IGNORED = COMMON_IGNORED | {"tagId", "name"}
TAG_NORMALIZED_IGNORED = TAG_ID_IGNORED | {
    "firingTriggerId",
    "blockingTriggerId",
    "parentFolderId",
    "notes",
    "scheduleStartMs",
    "scheduleEndMs",
}
TRIGGER_ID_IGNORED = COMMON_IGNORED | {"triggerId", "name"}
VARIABLE_ID_IGNORED = COMMON_IGNORED | {"variableId", "name"}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def stable_payload(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def signature(value: Any) -> str:
    return hashlib.sha256(stable_payload(value).encode("utf-8")).hexdigest()[:16]


def comparable(obj: dict[str, Any], ignored: set[str]) -> dict[str, Any]:
    return {key: value for key, value in obj.items() if key not in ignored}


def param_value(obj: dict[str, Any], key: str) -> Any:
    for param in as_list(obj.get("parameter")):
        if param.get("key") != key:
            continue
        if "value" in param:
            return param.get("value")
        if "list" in param:
            return param.get("list")
        if "map" in param:
            return param.get("map")
    return None


def object_id(obj: dict[str, Any], layer: str) -> str:
    keys = {
        "tag": "tagId",
        "trigger": "triggerId",
        "variable": "variableId",
        "folder": "folderId",
        "customTemplate": "templateId",
        "builtInVariable": "name",
    }
    value = obj.get(keys[layer]) or obj.get("name")
    return "" if value is None else str(value)


def object_name(obj: dict[str, Any]) -> str:
    return str(obj.get("name") or "")


def object_summary(obj: dict[str, Any], layer: str) -> dict[str, str]:
    obj_type = str(obj.get("type") or ("customTemplate" if layer == "customTemplate" else ""))
    cfg_hash = signature(comparable(obj, COMMON_IGNORED))
    return {
        "object_type": layer,
        "object_id": object_id(obj, layer),
        "object_name": object_name(obj),
        "type": obj_type,
        "config_hash": cfg_hash,
        "object_identity": "|".join(
            [layer, object_id(obj, layer), object_name(obj), obj_type, cfg_hash]
        ),
    }


def code_value(obj: dict[str, Any]) -> str:
    value = param_value(obj, "html")
    if value is None:
        value = param_value(obj, "javascript")
    return "" if value is None else str(value)


def normalized_code(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


UA_PROPERTY_RE = re.compile(r"\bUA-\d+(?:-\d+)+\b", re.I)
UA_TAG_PARAMETER_RE = re.compile(
    r"\b(?:trackingId|trackType|gaSettings|enableEcommerce|"
    r"enableEnhancedEcommerce|enhancedEcommerce|ecommerceMacroData)\b",
    re.I,
)
UA_LABEL_RE = re.compile(r"\b(?:UA|Universal Analytics|Enhanced Ecommerce)\b", re.I)
UA_ECOMMERCE_PATH_RE = re.compile(
    r"\becommerce\.(?:"
    r"purchase(?:\.(?:actionField|products)[A-Za-z0-9_\.\[\]]*)?|"
    r"add(?:\.products[A-Za-z0-9_\.\[\]]*)?|"
    r"remove(?:\.products[A-Za-z0-9_\.\[\]]*)?|"
    r"detail(?:\.products[A-Za-z0-9_\.\[\]]*)?|"
    r"checkout(?:\.(?:actionField|products)[A-Za-z0-9_\.\[\]]*)?|"
    r"impressions[A-Za-z0-9_\.\[\]]*|"
    r"currencyCode"
    r")",
    re.I,
)
FIXED_PRODUCT_INDEX_RE = re.compile(
    r"\becommerce\.(?:purchase|add|remove|detail|checkout)\.products"
    r"(?:\[\d+\]|\.\d+)(?:[A-Za-z0-9_\.\[\]]*)",
    re.I,
)
UA_STYLE_EVENT_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    r"checkout_step(?:_\d+)?|checkoutOption|checkout_option|"
    r"productDetailImpression|purchaseImpression|productImpression|"
    r"productDetail|productClick|promotionClick|promotionView|"
    r"addToCart|removeFromCart"
    r")(?![A-Za-z0-9_])",
    re.I,
)

KNOWN_SCOPE_TOKENS = {
    "all",
    "eu",
    "fr",
    "de",
    "uk",
    "gb",
    "ch",
    "at",
    "be",
    "it",
    "nl",
    "us",
    "iggi",
    "aura",
    "smart",
    "boss",
    "brand",
    "branding",
}

KNOWN_EVENT_TOKENS = {
    "pageview",
    "page_view",
    "viewitem",
    "view_item",
    "viewcontent",
    "view_content",
    "viewitemlist",
    "view_item_list",
    "addtocart",
    "add_to_cart",
    "removefromcart",
    "remove_from_cart",
    "viewcart",
    "view_cart",
    "begincheckout",
    "begin_checkout",
    "checkout",
    "addshippinginfo",
    "add_shipping_info",
    "addpaymentinfo",
    "add_payment_info",
    "purchase",
    "login",
    "newsletter",
    "refer",
    "magazine",
    "contact",
    "formsubmit",
    "form_submit",
    "click",
    "linkclick",
    "link_click",
    "conversionlinker",
    "conversion_linker",
    "remarketing",
    "base",
    "insight",
    "popups",
}

VENDOR_ALIASES = {
    "google analytics 4": "GA4",
    "google ads": "GADS",
    "piano analytics": "PA",
    "tradedoubler": "TD",
    "the trade desk": "TTD",
    "display & video 360": "DV360",
    "display and video 360": "DV360",
    "facebook": "Meta",
    "meta": "Meta",
    "tiktok": "TikTok",
    "teads": "Teads",
    "amazon": "Amazon",
    "bing": "Bing",
    "linkedin": "LinkedIn",
    "pinterest": "Pinterest",
    "realytics": "Realytics",
    "poptin": "Poptin",
}

TRIGGER_PREFIX_BY_TYPE = {
    "CUSTOM_EVENT": "CE",
    "PAGEVIEW": "PV",
    "LINK_CLICK": "LC",
    "FORM_SUBMISSION": "FORM",
    "TRIGGER_GROUP": "TG",
}

VARIABLE_PREFIX_BY_TYPE = {
    "v": "DLV",
    "jsm": "cJS",
    "smm": "LT",
    "remm": "RT",
    "u": "URL",
    "c": "Const",
}


def short_matches(pattern: re.Pattern[str], text: str, limit: int = 8) -> list[str]:
    matches = sorted({match.group(0) for match in pattern.finditer(text)})
    return matches[:limit]


def name_parts(name: str) -> list[str]:
    return [part.strip() for part in name.split(" - ") if part.strip()]


def token(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "", value.lower().replace(" ", "_"))


def is_scope_token(value: str) -> bool:
    parts = re.split(r"[\s_/().-]+", value.lower())
    return any(part in KNOWN_SCOPE_TOKENS for part in parts if part)


def is_event_token(value: str) -> bool:
    compact = token(value).replace("_", "")
    normalized = token(value)
    return normalized in KNOWN_EVENT_TOKENS or compact in {
        item.replace("_", "") for item in KNOWN_EVENT_TOKENS
    }


def vendor_label(value: str) -> str:
    cleaned = re.sub(r"\s+", " ", value.strip())
    normalized = cleaned.lower()
    if normalized in VENDOR_ALIASES:
        return VENDOR_ALIASES[normalized]
    if re.fullmatch(r"[A-Z0-9&]{2,8}", cleaned):
        return cleaned
    return cleaned


def strip_known_prefix(name: str, prefixes: set[str]) -> str:
    for prefix in sorted(prefixes, key=len, reverse=True):
        marker = f"{prefix} - "
        if name.startswith(marker):
            return name[len(marker) :].strip()
    return name.strip()


def proposed_tag_name(name: str, tag_order: str, selected_policy: str) -> tuple[str, str]:
    parts = name_parts(name)
    target_local_scope_event = selected_policy == "local-normalized" and tag_order == "vendor_scope_event"
    if len(parts) < 3:
        return "", "Tag name does not contain enough vendor/event/scope tokens to propose a safe final name."
    vendor = vendor_label(parts[0])
    if target_local_scope_event:
        scope, event = parts[1], parts[2]
        proposed = f"{vendor} - {scope} - {event}"
        if not is_scope_token(scope) or not is_event_token(event):
            return proposed, "Existing tokens do not clearly prove local scope/event meaning."
        return proposed, ""
    event, scope = parts[1], parts[2]
    proposed = f"{vendor} - {event} - {scope}"
    if not is_event_token(event) or not is_scope_token(scope):
        return proposed, "Existing tokens do not clearly prove default event/scope meaning."
    return proposed, ""


def proposed_trigger_name(trigger: dict[str, Any], prefix: str) -> str:
    base = strip_known_prefix(object_name(trigger), set(TRIGGER_PREFIX_BY_TYPE.values()) | {"Block"})
    return f"{prefix} - {base}" if base else ""


def proposed_variable_name(variable: dict[str, Any], prefix: str) -> str:
    base = strip_known_prefix(object_name(variable), set(VARIABLE_PREFIX_BY_TYPE.values()) | {"Util"})
    return f"{prefix} - {base}" if base else ""


def proposed_folder_name(folder: dict[str, Any]) -> tuple[str, str]:
    parts = name_parts(object_name(folder))
    if not parts:
        return "", "Folder name has no usable area token."
    return parts[0], ""


def uniqueness_notes(candidates: dict[str, collections.Counter[str]], layer: str, name: str) -> str:
    if not name:
        return "No proposed final name."
    if candidates.get(layer, collections.Counter())[name] > 1:
        return "Proposed final name is not unique inside this GTM layer; add a scope token after owner confirmation."
    return ""


def infer_tag_order(tags: list[dict[str, Any]]) -> dict[str, Any]:
    counts: collections.Counter[str] = collections.Counter()
    examples: dict[str, list[str]] = collections.defaultdict(list)
    for tag in tags:
        parts = name_parts(object_name(tag))
        if len(parts) < 3:
            continue
        second_is_event = is_event_token(parts[1])
        third_is_event = is_event_token(parts[2])
        second_is_scope = is_scope_token(parts[1])
        third_is_scope = is_scope_token(parts[2])
        if second_is_event and third_is_scope:
            key = "vendor_event_scope"
        elif second_is_scope and third_is_event:
            key = "vendor_scope_event"
        else:
            key = "ambiguous"
        counts[key] += 1
        if len(examples[key]) < 5:
            examples[key].append(object_name(tag))

    total = sum(counts.values())
    if not total:
        return {
            "selected_policy": "default-standardized",
            "tag_order": "vendor_event_scope",
            "confidence": "low",
            "reason": "No dominant three-part tag naming pattern was detected.",
            "examples": {},
        }

    winner, winner_count = counts.most_common(1)[0]
    ratio = winner_count / total
    if winner in {"vendor_event_scope", "vendor_scope_event"} and ratio >= 0.6:
        return {
            "selected_policy": "local-normalized",
            "tag_order": winner,
            "confidence": "high" if ratio >= 0.75 else "medium",
            "reason": (
                f"{winner_count}/{total} parsable three-part tag names follow "
                f"{winner.replace('_', ' - ')} order."
            ),
            "examples": dict(examples),
        }
    return {
        "selected_policy": "default-standardized",
        "tag_order": "vendor_event_scope",
        "confidence": "medium" if ratio >= 0.45 else "low",
        "reason": "No reliable local tag naming order dominates the export.",
        "examples": dict(examples),
    }


def default_tag_issue(name: str, tag_order: str) -> str:
    parts = name_parts(name)
    if len(parts) < 3:
        return "tag name is not structured as Vendor - Event - Scope or a reliable local equivalent"
    if tag_order == "vendor_scope_event":
        if not is_scope_token(parts[1]) or not is_event_token(parts[2]):
            return "tag name does not match the detected local Vendor - Scope - Event order"
        return ""
    if not is_event_token(parts[1]) or not is_scope_token(parts[2]):
        return "tag name does not match the default Vendor - Event - Scope order"
    return ""


def trigger_required_prefix(trigger: dict[str, Any], blocking_trigger_ids: set[str]) -> str:
    trigger_id = str(trigger.get("triggerId") or "")
    if trigger_id in blocking_trigger_ids:
        return "Block"
    return TRIGGER_PREFIX_BY_TYPE.get(str(trigger.get("type") or ""), "")


def variable_required_prefix(variable: dict[str, Any]) -> str:
    return VARIABLE_PREFIX_BY_TYPE.get(str(variable.get("type") or ""), "")


def recognized_system_references(
    variable_consumers: dict[str, list[dict[str, str]]],
    trigger_consumers: dict[str, list[dict[str, str]]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        "variable_references": [
            {
                "reference": ref,
                "description": system_reference_description("variable", ref),
                "consumers": consumers,
            }
            for ref, consumers in sorted(variable_consumers.items())
            if is_system_variable_reference(ref)
        ],
        "trigger_references": [
            {
                "reference": ref,
                "description": system_reference_description("trigger", ref),
                "consumers": consumers,
            }
            for ref, consumers in sorted(trigger_consumers.items())
            if is_system_trigger_reference(ref)
        ],
    }


def ua_style_signals(layer: str, obj: dict[str, Any]) -> list[str]:
    text = stable_payload(obj)
    name = object_name(obj)
    signals: list[str] = []

    if layer == "tag" and str(obj.get("type") or "").lower() == "ua":
        signals.append("native Universal Analytics tag type")
    if layer == "tag" and UA_TAG_PARAMETER_RE.search(text):
        signals.append("Universal Analytics tag parameters")
    if UA_PROPERTY_RE.search(text):
        signals.append("UA property ID")
    if UA_LABEL_RE.search(name):
        signals.append("object name says UA, Universal Analytics, or Enhanced Ecommerce")

    old_paths = short_matches(UA_ECOMMERCE_PATH_RE, text)
    if old_paths:
        signals.append(
            "old Universal Analytics ecommerce path(s): " + ", ".join(old_paths)
        )

    fixed_indexes = short_matches(FIXED_PRODUCT_INDEX_RE, text)
    if fixed_indexes:
        signals.append(
            "fixed product position path(s): " + ", ".join(fixed_indexes)
        )

    legacy_events = short_matches(UA_STYLE_EVENT_RE, text)
    if legacy_events:
        signals.append(
            "legacy checkout/product event name(s): " + ", ".join(legacy_events)
        )

    return signals


def add_ua_styled_setup_findings(
    builder: BaselineBuilder,
    tags: list[dict[str, Any]],
    triggers: list[dict[str, Any]],
    variables: list[dict[str, Any]],
) -> None:
    module_name = "outdated_ua_styled_setup_objects"
    builder.add_module(module_name, len(tags) + len(triggers) + len(variables))
    for layer, items in (("tag", tags), ("trigger", triggers), ("variable", variables)):
        for item in items:
            signals = ua_style_signals(layer, item)
            if not signals:
                continue
            builder.add_finding(
                module_name,
                "outdated_ua_styled_setup_object",
                layer,
                [object_summary(item, layer)],
                f"{layer}:{object_id(item, layer)}",
                (
                    "This object has legacy Universal Analytics-style setup signals: "
                    + "; ".join(signals)
                    + "."
                ),
                (
                    "Confirm whether the object is still needed. If it feeds current "
                    "GA4 or vendor tracking, migrate it to the current event/item data "
                    "format or document a legacy exception with runtime proof."
                ),
            )


def deterministic_action_candidate(finding_type: str, default_action: str) -> str:
    text = f"{finding_type} {default_action}".lower()
    if "missing" in text or "resolve reference" in text or "triggerless" in text:
        return "fix_required"
    if "unused" in text or "delete candidate" in text:
        return "delete_candidate"
    if "duplicate" in text or "consolidate" in text or "canonical" in text:
        return "consolidate_candidate"
    if "name" in text or "rename" in text or "naming" in text:
        return "rename_candidate"
    if "universal analytics" in text or "legacy" in text or "ecommerce" in text:
        return "fix_required"
    return "owner_decision_needed"


class BaselineBuilder:
    def __init__(self) -> None:
        self.findings: list[dict[str, Any]] = []
        self.modules: dict[str, dict[str, Any]] = {}
        self.counters: collections.Counter[str] = collections.Counter()

    def _next_id(self, module_name: str) -> str:
        self.counters[module_name] += 1
        slug = re.sub(r"[^A-Z0-9]+", "_", module_name.upper()).strip("_")[:28]
        return f"BASE-{slug}-{self.counters[module_name]:03d}"

    def add_module(self, module_name: str, objects_scanned: int) -> None:
        self.modules[module_name] = {
            "module_name": module_name,
            "module_status": "pending",
            "objects_scanned": objects_scanned,
            "findings_count": 0,
        }

    def add_finding(
        self,
        module_name: str,
        finding_type: str,
        object_type: str,
        objects: list[dict[str, Any]],
        signature_key: str,
        deterministic_evidence: str,
        default_action: str,
        required_resolution: str = (
            "cleanup_operation | documented_exception | runtime_blocker | "
            "owner_decision_needed | not_applicable"
        ),
        extra: dict[str, Any] | None = None,
    ) -> None:
        module = self.modules[module_name]
        module["findings_count"] += 1
        module["module_status"] = "findings"
        row = {
            "module_name": module_name,
            "module_status": "findings",
            "objects_scanned": module["objects_scanned"],
            "finding_id": self._next_id(module_name),
            "finding_type": finding_type,
            "object_type": object_type,
            "object_ids": [obj.get("object_id", "") for obj in objects],
            "object_names": [obj.get("object_name", "") for obj in objects],
            "signature_key": signature_key,
            "deterministic_evidence": deterministic_evidence,
            "default_action": default_action,
            "source_lens": "deterministic",
            "deterministic_action_candidate": deterministic_action_candidate(
                finding_type, default_action
            ),
            "object_identities": [
                obj.get("object_identity", "") for obj in objects if obj.get("object_identity")
            ],
            "operation_packet_required": True,
            "required_resolution": required_resolution,
        }
        if extra:
            row.update(extra)
        self.findings.append(row)

    def close_zero_modules(self) -> None:
        for module_name, module in self.modules.items():
            if module["findings_count"]:
                continue
            module["module_status"] = "zero_findings"
            self.findings.append(
                {
                    "module_name": module_name,
                    "module_status": "zero_findings",
                    "objects_scanned": module["objects_scanned"],
                    "finding_id": f"BASE-{re.sub(r'[^A-Z0-9]+', '_', module_name.upper()).strip('_')[:28]}-000",
                    "finding_type": "zero_findings",
                    "object_type": "module",
                    "object_ids": [],
                    "object_names": [],
                    "signature_key": "",
                    "deterministic_evidence": (
                        f"No deterministic findings produced by module {module_name} "
                        f"after scanning {module['objects_scanned']} object(s)."
                    ),
                    "default_action": "No cleanup action from this module.",
                    "source_lens": "deterministic",
                    "deterministic_action_candidate": "not_applicable",
                    "object_identities": [],
                    "operation_packet_required": False,
                    "required_resolution": "not_applicable",
                }
            )


def group_by(items: list[dict[str, Any]], key_fn) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for item in items:
        key = key_fn(item)
        if key:
            groups[str(key)].append(item)
    return dict(groups)


def add_duplicate_name_findings(
    builder: BaselineBuilder, module_name: str, layer: str, items: list[dict[str, Any]]
) -> None:
    builder.add_module(module_name, len(items))
    for name, group in sorted(group_by(items, object_name).items()):
        if len(group) < 2:
            continue
        builder.add_finding(
            module_name,
            "duplicate_name",
            layer,
            [object_summary(obj, layer) for obj in group],
            f"name:{name}",
            f"{len(group)} {layer} objects share the exact name {name!r}.",
            "Resolve naming ambiguity or document why identical names are intentional.",
        )


def add_signature_findings(
    builder: BaselineBuilder,
    module_name: str,
    finding_type: str,
    layer: str,
    items: list[dict[str, Any]],
    ignored: set[str],
    default_action: str,
) -> None:
    builder.add_module(module_name, len(items))
    groups = group_by(items, lambda obj: signature(comparable(obj, ignored)))
    for sig, group in sorted(groups.items()):
        if len(group) < 2:
            continue
        builder.add_finding(
            module_name,
            finding_type,
            layer,
            [object_summary(obj, layer) for obj in group],
            sig,
            f"{len(group)} {layer} objects share deterministic signature {sig}.",
            default_action,
        )


def build_consumers(cv: dict[str, Any]) -> tuple[dict[str, list[dict[str, str]]], dict[str, list[dict[str, str]]]]:
    variable_consumers: dict[str, list[dict[str, str]]] = collections.defaultdict(list)
    trigger_consumers: dict[str, list[dict[str, str]]] = collections.defaultdict(list)

    for tag in as_list(cv.get("tag")):
        for ref in sorted(refs(tag)):
            variable_consumers[ref].append(object_summary(tag, "tag"))
        for trigger_id in as_list(tag.get("firingTriggerId")) + as_list(tag.get("blockingTriggerId")):
            trigger_consumers[str(trigger_id)].append(object_summary(tag, "tag"))

    for trigger in as_list(cv.get("trigger")):
        for ref in sorted(refs(trigger)):
            variable_consumers[ref].append(object_summary(trigger, "trigger"))
        for member_id in trigger_group_members(trigger):
            trigger_consumers[str(member_id)].append(object_summary(trigger, "trigger"))

    for variable in as_list(cv.get("variable")):
        for ref in sorted(refs(variable)):
            if ref == variable.get("name"):
                continue
            variable_consumers[ref].append(object_summary(variable, "variable"))

    return dict(variable_consumers), dict(trigger_consumers)


def add_missing_reference_findings(
    builder: BaselineBuilder,
    cv: dict[str, Any],
    variable_consumers: dict[str, list[dict[str, str]]],
    trigger_consumers: dict[str, list[dict[str, str]]],
) -> None:
    tags = as_list(cv.get("tag"))
    triggers = as_list(cv.get("trigger"))
    variables = as_list(cv.get("variable"))
    folders = as_list(cv.get("folder"))
    templates = as_list(cv.get("customTemplate"))
    builtins = as_list(cv.get("builtInVariable"))

    builder.add_module(
        "missing_references",
        len(tags) + len(triggers) + len(variables) + len(folders) + len(templates),
    )

    variable_names = {item.get("name") for item in variables} | {item.get("name") for item in builtins}
    for name in sorted(
        ref
        for ref in variable_consumers
        if ref not in variable_names and not is_system_variable_reference(ref)
    ):
        builder.add_finding(
            "missing_references",
            "undefined_variable_reference",
            "variable_reference",
            [{"object_id": name, "object_name": name}],
            f"var:{name}",
            f"Reference {{{{{name}}}}} is used but no variable or built-in with that name exists.",
            "Resolve reference before cleanup execution; use fresh readback or restore/create the missing source.",
            "runtime_blocker | cleanup_operation | documented_exception",
        )

    trigger_ids = {str(trigger.get("triggerId")) for trigger in triggers}
    for trigger_id in sorted(
        ref
        for ref in trigger_consumers
        if ref not in trigger_ids and not is_system_trigger_reference(ref)
    ):
        builder.add_finding(
            "missing_references",
            "missing_trigger_reference",
            "trigger_reference",
            [{"object_id": trigger_id, "object_name": trigger_id}],
            f"trigger:{trigger_id}",
            f"Trigger ID {trigger_id} is consumed but no trigger with that ID exists.",
            "Resolve reference before cleanup execution; use fresh readback or restore/create the missing trigger.",
            "runtime_blocker | cleanup_operation | documented_exception",
        )

    tag_names = {tag.get("name") for tag in tags}
    for tag in tags:
        for relation in ("setupTag", "teardownTag"):
            for ref in as_list(tag.get(relation)):
                tag_name = ref.get("tagName")
                if tag_name and tag_name not in tag_names:
                    builder.add_finding(
                        "missing_references",
                        f"missing_{relation}_reference",
                        "tag_reference",
                        [object_summary(tag, "tag"), {"object_id": tag_name, "object_name": tag_name}],
                        f"{relation}:{tag_name}",
                        f"Tag {tag.get('name')!r} references missing {relation} tag {tag_name!r}.",
                        "Resolve sequencing reference before cleanup execution.",
                        "runtime_blocker | cleanup_operation | documented_exception",
                    )

    folder_ids = {str(folder.get("folderId")) for folder in folders}
    for layer, items in (("tag", tags), ("trigger", triggers), ("variable", variables)):
        for item in items:
            folder_id = item.get("parentFolderId")
            if folder_id and str(folder_id) not in folder_ids:
                builder.add_finding(
                    "missing_references",
                    "missing_folder_reference",
                    layer,
                    [object_summary(item, layer), {"object_id": str(folder_id), "object_name": str(folder_id)}],
                    f"folder:{folder_id}",
                    f"{layer} {item.get('name')!r} references missing folder {folder_id}.",
                    "Restore folder reference or move object to an existing folder.",
                )

    template_ids = {str(template.get("templateId")) for template in templates}
    for layer, items in (("tag", tags), ("variable", variables)):
        for item in items:
            template_id = custom_template_id(item)
            if template_id and template_id not in template_ids:
                builder.add_finding(
                    "missing_references",
                    "missing_custom_template_reference",
                    layer,
                    [object_summary(item, layer), {"object_id": template_id, "object_name": template_id}],
                    f"template:{template_id}",
                    f"{layer} {item.get('name')!r} uses custom template {template_id}, but it is not in customTemplate.",
                    "Restore or include the required custom template before cleanup execution.",
                )


def add_unused_findings(
    builder: BaselineBuilder,
    cv: dict[str, Any],
    variable_consumers: dict[str, list[dict[str, str]]],
    trigger_consumers: dict[str, list[dict[str, str]]],
) -> None:
    triggers = as_list(cv.get("trigger"))
    variables = as_list(cv.get("variable"))
    folders = as_list(cv.get("folder"))
    templates = as_list(cv.get("customTemplate"))
    tags = as_list(cv.get("tag"))

    builder.add_module("unused_variables", len(variables))
    for variable in variables:
        if variable_consumers.get(variable.get("name")):
            continue
        builder.add_finding(
            "unused_variables",
            "unused_object",
            "variable",
            [object_summary(variable, "variable")],
            f"variable:{object_id(variable, 'variable')}",
            "No export-visible tag, trigger, variable, or custom-code placeholder references this variable.",
            "Delete candidate only after semantic review confirms no runtime-only dependency.",
        )

    builder.add_module("unused_triggers", len(triggers))
    for trigger in triggers:
        if trigger_consumers.get(str(trigger.get("triggerId"))):
            continue
        builder.add_finding(
            "unused_triggers",
            "unused_object",
            "trigger",
            [object_summary(trigger, "trigger")],
            f"trigger:{object_id(trigger, 'trigger')}",
            "No tag or trigger group consumes this trigger ID in the export.",
            "Delete candidate after semantic review confirms it is not a future/staged trigger.",
        )

    builder.add_module("tags_without_firing_triggers", len(tags))
    for tag in tags:
        if tag.get("firingTriggerId"):
            continue
        builder.add_finding(
            "tags_without_firing_triggers",
            "tag_without_firing_trigger",
            "tag",
            [object_summary(tag, "tag")],
            f"tag:{object_id(tag, 'tag')}",
            "Tag has no firingTriggerId in the export.",
            "Fix, pause/delete, or document why the tag is intentionally triggerless.",
        )

    builder.add_module("unused_custom_templates", len(templates))
    used_template_ids = {
        custom_template_id(item)
        for item in tags + variables
        if custom_template_id(item)
    }
    for template in templates:
        template_id = str(template.get("templateId"))
        if template_id in used_template_ids:
            continue
        builder.add_finding(
            "unused_custom_templates",
            "unused_object",
            "customTemplate",
            [object_summary(template, "customTemplate")],
            f"template:{template_id}",
            "No tag or variable uses this custom template ID in the export.",
            "Delete candidate only after confirming no workspace/template dependency remains.",
        )

    builder.add_module("unused_folders", len(folders))
    used_folder_ids = {
        str(item.get("parentFolderId"))
        for item in tags + triggers + variables
        if item.get("parentFolderId")
    }
    for folder in folders:
        folder_id = str(folder.get("folderId"))
        if folder_id in used_folder_ids:
            continue
        builder.add_finding(
            "unused_folders",
            "unused_object",
            "folder",
            [object_summary(folder, "folder")],
            f"folder:{folder_id}",
            "No tag, trigger, or variable references this folder.",
            "Delete or repurpose after owner confirms folder is not needed for organization.",
        )


def add_trigger_group_findings(builder: BaselineBuilder, triggers: list[dict[str, Any]]) -> None:
    builder.add_module("single_member_trigger_groups", len(triggers))
    trigger_by_id = {str(trigger.get("triggerId")): trigger for trigger in triggers}
    for trigger in triggers:
        members = trigger_group_members(trigger)
        if len(members) != 1:
            continue
        child = trigger_by_id.get(members[0])
        objects = [object_summary(trigger, "trigger")]
        if child:
            objects.append(object_summary(child, "trigger"))
        builder.add_finding(
            "single_member_trigger_groups",
            "single_member_trigger_group",
            "trigger",
            objects,
            f"trigger_group:{object_id(trigger, 'trigger')}->{members[0]}",
            f"Trigger group {trigger.get('name')!r} contains exactly one child trigger {members[0]}.",
            "Flatten consumers to the child trigger and delete the group when the selected cleanup route supports deletion.",
        )


def add_duplicate_code_findings(
    builder: BaselineBuilder, tags: list[dict[str, Any]], variables: list[dict[str, Any]]
) -> None:
    custom_objects: list[tuple[str, dict[str, Any], str]] = []
    for tag in tags:
        code = code_value(tag)
        if code:
            custom_objects.append(("tag", tag, code))
    for variable in variables:
        code = code_value(variable)
        if code:
            custom_objects.append(("variable", variable, code))

    builder.add_module("duplicate_custom_code", len(custom_objects))
    groups: dict[str, list[tuple[str, dict[str, Any], str]]] = collections.defaultdict(list)
    for layer, obj, code in custom_objects:
        normalized = normalized_code(code)
        if normalized:
            groups[signature(normalized)].append((layer, obj, normalized))

    for code_hash, group in sorted(groups.items()):
        if len(group) < 2:
            continue
        builder.add_finding(
            "duplicate_custom_code",
            "duplicate_custom_code",
            "custom_code",
            [object_summary(obj, layer) for layer, obj, _ in group],
            code_hash,
            f"{len(group)} custom-code objects share identical normalized code hash {code_hash}.",
            "Consolidate or document why identical code must remain separate.",
        )


def add_name_hygiene_findings(builder: BaselineBuilder, cv: dict[str, Any]) -> None:
    items: list[tuple[str, dict[str, Any]]] = []
    for layer in ("tag", "trigger", "variable", "folder", "customTemplate"):
        items.extend((layer, item) for item in as_list(cv.get(layer)))
    builder.add_module("name_hygiene", len(items))
    for layer, item in items:
        name = object_name(item)
        problems = []
        if not name:
            problems.append("blank name")
        if name != name.strip():
            problems.append("leading/trailing whitespace")
        if re.search(r"\s{2,}", name):
            problems.append("repeated whitespace")
        if re.search(r"\s+-\s+-\s+", name) or "--" in name:
            problems.append("duplicated separator")
        if not problems:
            continue
        builder.add_finding(
            "name_hygiene",
            "name_hygiene",
            layer,
            [object_summary(item, layer)],
            f"name:{object_id(item, layer)}",
            f"Name hygiene issue(s): {', '.join(problems)}.",
            "Fix naming as part of the naming standardization stage or document an exception.",
        )


def add_naming_architecture_findings(
    builder: BaselineBuilder, cv: dict[str, Any], naming_policy: dict[str, Any]
) -> None:
    tags = as_list(cv.get("tag"))
    triggers = as_list(cv.get("trigger"))
    variables = as_list(cv.get("variable"))
    folders = as_list(cv.get("folder"))
    templates = as_list(cv.get("customTemplate"))
    module_name = "naming_architecture_standardization"
    builder.add_module(module_name, len(tags) + len(triggers) + len(variables) + len(folders) + len(templates))

    tag_order = str(naming_policy.get("tag_order") or "vendor_event_scope")
    selected = str(naming_policy.get("selected_policy") or "default-standardized")
    blocking_trigger_ids = {
        str(trigger_id)
        for tag in tags
        for trigger_id in as_list(tag.get("blockingTriggerId"))
    }
    candidate_counts: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    for tag in tags:
        if default_tag_issue(object_name(tag), tag_order):
            proposed, _ = proposed_tag_name(object_name(tag), tag_order, selected)
            if proposed:
                candidate_counts["tag"][proposed] += 1
    for trigger in triggers:
        prefix = trigger_required_prefix(trigger, blocking_trigger_ids)
        if prefix and not object_name(trigger).startswith(f"{prefix} - "):
            proposed = proposed_trigger_name(trigger, prefix)
            if proposed:
                candidate_counts["trigger"][proposed] += 1
    for variable in variables:
        prefix = variable_required_prefix(variable)
        if prefix and not object_name(variable).startswith(f"{prefix} - "):
            proposed = proposed_variable_name(variable, prefix)
            if proposed:
                candidate_counts["variable"][proposed] += 1
    for folder in folders:
        if " - " in object_name(folder):
            proposed, _ = proposed_folder_name(folder)
            if proposed:
                candidate_counts["folder"][proposed] += 1

    for tag in tags:
        name = object_name(tag)
        issue = default_tag_issue(name, tag_order)
        if not issue:
            continue
        proposed, rename_blocker = proposed_tag_name(name, tag_order, selected)
        uniqueness_blocker = uniqueness_notes(candidate_counts, "tag", proposed)
        blocker = "; ".join(item for item in (rename_blocker, uniqueness_blocker) if item)
        pattern = (
            "Vendor - Scope - Event"
            if selected == "local-normalized" and tag_order == "vendor_scope_event"
            else "Vendor - Event - Scope"
        )
        builder.add_finding(
            module_name,
            "naming_architecture_mismatch",
            "tag",
            [object_summary(tag, "tag")],
            f"tag_name:{object_id(tag, 'tag')}",
            (
                f"{issue}. Selected naming policy is {selected}; target tag "
                f"pattern is {pattern}."
            ),
            (
                "Rename after behavior, scope, and destination are confirmed. "
                "Use the selected naming policy and keep every final tag name unique."
            ),
            extra={
                "selected_naming_policy": selected,
                "target_naming_pattern": pattern,
                "proposed_final_name": proposed,
                "rename_blocker": blocker,
                "rename_candidate_unique": not bool(uniqueness_blocker),
            },
        )

    for trigger in triggers:
        prefix = trigger_required_prefix(trigger, blocking_trigger_ids)
        if not prefix:
            continue
        name = object_name(trigger)
        if name.startswith(f"{prefix} - "):
            continue
        proposed = proposed_trigger_name(trigger, prefix)
        uniqueness_blocker = uniqueness_notes(candidate_counts, "trigger", proposed)
        builder.add_finding(
            module_name,
            "naming_architecture_mismatch",
            "trigger",
            [object_summary(trigger, "trigger")],
            f"trigger_name:{object_id(trigger, 'trigger')}",
            (
                f"Trigger type {trigger.get('type')!r} should use prefix "
                f"{prefix!r} under the selected trigger architecture."
            ),
            (
                "Rename trigger after confirming event, condition, blocking role, "
                "and trigger-group consumers."
            ),
            extra={
                "selected_naming_policy": selected,
                "target_naming_pattern": f"{prefix} - event_or_condition",
                "proposed_final_name": proposed,
                "rename_blocker": uniqueness_blocker,
                "rename_candidate_unique": not bool(uniqueness_blocker),
            },
        )

    for variable in variables:
        prefix = variable_required_prefix(variable)
        if not prefix:
            continue
        name = object_name(variable)
        if name.startswith(f"{prefix} - "):
            continue
        proposed = proposed_variable_name(variable, prefix)
        uniqueness_blocker = uniqueness_notes(candidate_counts, "variable", proposed)
        builder.add_finding(
            module_name,
            "naming_architecture_mismatch",
            "variable",
            [object_summary(variable, "variable")],
            f"variable_name:{object_id(variable, 'variable')}",
            (
                f"Variable type {variable.get('type')!r} should use prefix "
                f"{prefix!r} under the selected variable naming policy."
            ),
            (
                "Rename variable after dependency sweep across tags, triggers, "
                "variables, templates, Custom HTML, and Custom JavaScript."
            ),
            extra={
                "selected_naming_policy": selected,
                "target_naming_pattern": f"{prefix} - name_or_source",
                "proposed_final_name": proposed,
                "rename_blocker": uniqueness_blocker,
                "rename_candidate_unique": not bool(uniqueness_blocker),
            },
        )

    for folder in folders:
        name = object_name(folder)
        if " - " not in name:
            continue
        proposed, rename_blocker = proposed_folder_name(folder)
        uniqueness_blocker = uniqueness_notes(candidate_counts, "folder", proposed)
        blocker = "; ".join(item for item in (rename_blocker, uniqueness_blocker) if item)
        builder.add_finding(
            module_name,
            "folder_naming_review",
            "folder",
            [object_summary(folder, "folder")],
            f"folder_name:{object_id(folder, 'folder')}",
            (
                "Folder name contains a scope separator. Default folder policy "
                "starts with area-only folders unless object volume requires deeper ranging."
            ),
            "Keep or simplify folder naming after counting objects per area.",
            "owner_decision_needed | cleanup_operation | not_applicable",
            extra={
                "selected_naming_policy": selected,
                "target_naming_pattern": "Area",
                "proposed_final_name": proposed,
                "rename_blocker": blocker,
                "rename_candidate_unique": not bool(uniqueness_blocker),
            },
        )


def audit_export(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cv = container_version(data)
    tags = as_list(cv.get("tag"))
    triggers = as_list(cv.get("trigger"))
    variables = as_list(cv.get("variable"))
    folders = as_list(cv.get("folder"))
    templates = as_list(cv.get("customTemplate"))
    builtins = as_list(cv.get("builtInVariable"))

    builder = BaselineBuilder()
    variable_consumers, trigger_consumers = build_consumers(cv)
    system_refs = recognized_system_references(variable_consumers, trigger_consumers)
    naming_policy = infer_tag_order(tags)

    builder.add_module("inventory", len(tags) + len(triggers) + len(variables) + len(folders) + len(templates) + len(builtins))
    builder.add_module(
        "recognized_system_references",
        sum(len(values) for values in system_refs.values()),
    )
    add_missing_reference_findings(builder, cv, variable_consumers, trigger_consumers)
    add_duplicate_name_findings(builder, "duplicate_tag_names", "tag", tags)
    add_duplicate_name_findings(builder, "duplicate_trigger_names", "trigger", triggers)
    add_duplicate_name_findings(builder, "duplicate_variable_names", "variable", variables)
    add_duplicate_name_findings(builder, "duplicate_folder_names", "folder", folders)
    add_signature_findings(
        builder,
        "duplicate_tag_configurations",
        "duplicate_configuration",
        "tag",
        tags,
        TAG_ID_IGNORED,
        "Review duplicate tag configurations; consolidate or document why each copy has a distinct purpose.",
    )
    add_signature_findings(
        builder,
        "normalized_duplicate_tag_signatures",
        "normalized_duplicate_tag_signature",
        "tag",
        tags,
        TAG_NORMALIZED_IGNORED,
        "Compare trigger/route differences; consolidate only if semantic intent and route behavior are equivalent.",
    )
    add_signature_findings(
        builder,
        "duplicate_trigger_logic",
        "duplicate_configuration",
        "trigger",
        triggers,
        TRIGGER_ID_IGNORED,
        "Consolidate duplicate trigger logic after consumer and route QA.",
    )
    add_signature_findings(
        builder,
        "duplicate_variable_logic",
        "duplicate_configuration",
        "variable",
        variables,
        VARIABLE_ID_IGNORED,
        "Consolidate duplicate variable logic after consumer value QA.",
    )

    builder.add_module("duplicate_variable_paths", len(variables))
    path_groups = group_by(
        [variable for variable in variables if param_value(variable, "name")],
        lambda variable: param_value(variable, "name"),
    )
    for path_value, group in sorted(path_groups.items()):
        if len(group) < 2:
            continue
        builder.add_finding(
            "duplicate_variable_paths",
            "duplicate_variable_path",
            "variable",
            [object_summary(variable, "variable") for variable in group],
            f"path:{path_value}",
            f"{len(group)} variables read the same source path {path_value!r}.",
            "Pick a canonical variable or document why separate variables are required.",
        )

    add_ua_styled_setup_findings(builder, tags, triggers, variables)
    add_unused_findings(builder, cv, variable_consumers, trigger_consumers)
    add_trigger_group_findings(builder, triggers)
    add_duplicate_code_findings(builder, tags, variables)
    add_name_hygiene_findings(builder, cv)
    add_naming_architecture_findings(builder, cv, naming_policy)
    builder.close_zero_modules()

    return {
        "artifact": str(path),
        "kind": "gtm_deterministic_baseline",
        "counts": {
            "tags": len(tags),
            "triggers": len(triggers),
            "variables": len(variables),
            "folders": len(folders),
            "customTemplates": len(templates),
            "builtInVariables": len(builtins),
        },
        "recognized_system_references": system_refs,
        "naming_policy": naming_policy,
        "modules": list(builder.modules.values()),
        "findings": builder.findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Path to a GTM container export JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    result = audit_export(args.export)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
