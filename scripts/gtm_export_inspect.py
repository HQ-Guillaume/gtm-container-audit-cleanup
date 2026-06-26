#!/usr/bin/env python3
"""Inspect a GTM container export and emit scalable audit hints as JSON."""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import re
from pathlib import Path
from typing import Any


REF_RE = re.compile(r"\{\{([^{}]+)\}\}")
CUSTOM_TEMPLATE_RE = re.compile(r"^cvt_\d+_(\d+)$")
ECOM_RE = re.compile(
    r"ecommerce|revenue|value|price|quantity|qty|currency|tax|shipping|"
    r"transaction|product|item|sku|category|coupon",
    re.I,
)
LEGACY_UA_ECOM_RE = re.compile(
    r"ecommerce\.(purchase\.actionField|purchase\.products|add\.products|"
    r"detail\.products|checkout\.products|checkout\.actionField|"
    r"remove\.products|impressions|currencyCode)",
    re.I,
)
VENDOR_PATTERNS = [
    ("GA4 / Google tag", re.compile(r"\bga4\b|google analytics|measurement id|G-[A-Z0-9]+", re.I)),
    ("Google Ads", re.compile(r"google ads|adwords|aw-|conversion linker", re.I)),
    ("Floodlight", re.compile(r"floodlight|doubleclick|dc-[0-9]|activity", re.I)),
    ("Meta", re.compile(r"\bmeta\b|facebook|fbq|pixel id|content_ids|contents", re.I)),
    ("TikTok", re.compile(r"tiktok|ttq|tik tok", re.I)),
    ("Snapchat", re.compile(r"snapchat|snap pixel|snaptr", re.I)),
    ("Pinterest", re.compile(r"pinterest|pintrk", re.I)),
    ("Microsoft Ads", re.compile(r"microsoft ads|bing|uet", re.I)),
    ("LinkedIn", re.compile(r"linkedin|insight tag|lintrk", re.I)),
    ("Criteo", re.compile(r"criteo|onetag", re.I)),
    ("Awin", re.compile(r"\bawin\b|zanox", re.I)),
    ("Effinity", re.compile(r"effinity|effiliation", re.I)),
    ("Didomi", re.compile(r"didomi", re.I)),
]
ECOM_ROLE_PATTERNS = [
    ("purchase", re.compile(r"purchase|order|transaction|confirmation|sale", re.I)),
    ("add_to_cart", re.compile(r"add.?to.?cart|ajout.?panier", re.I)),
    ("remove_from_cart", re.compile(r"remove.?from.?cart|retrait.?panier", re.I)),
    ("begin_checkout", re.compile(r"checkout|basket|panier", re.I)),
    ("view_item", re.compile(r"product.?detail|fiche.?produit|view.?item", re.I)),
    ("view_item_list", re.compile(r"list|category|page.?liste|view.?item.?list", re.I)),
    ("page_view", re.compile(r"page.?view|all.?pages|homepage|home.?page", re.I)),
]


def container_version(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("containerVersion", data)


def param_value(obj: dict[str, Any], key: str) -> Any:
    for param in obj.get("parameter", []) or []:
        if param.get("key") == key:
            if "value" in param:
                return param["value"]
            if "list" in param:
                return param["list"]
            if "map" in param:
                return param["map"]
    return None


def references(obj: Any) -> list[str]:
    return sorted(set(REF_RE.findall(json.dumps(obj, ensure_ascii=False))))


def stable_signature(obj: dict[str, Any], ignored: set[str]) -> str:
    clean = {k: v for k, v in obj.items() if k not in ignored}
    payload = json.dumps(clean, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def duplicate_groups(items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for item in items:
        value = item.get(key)
        if value:
            groups[str(value)].append(item)
    return [
        {"value": value, "objects": [summary(o) for o in group]}
        for value, group in sorted(groups.items())
        if len(group) > 1
    ]


def summary(obj: dict[str, Any]) -> dict[str, Any]:
    for id_key in ("tagId", "triggerId", "variableId", "folderId"):
        if id_key in obj:
            return {"id": obj.get(id_key), "name": obj.get("name"), "type": obj.get("type")}
    return {"name": obj.get("name"), "type": obj.get("type")}


def signature_groups(
    items: list[dict[str, Any]],
    ignored: set[str],
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for item in items:
        groups[stable_signature(item, ignored)].append(item)
    return [
        {"signature": sig, "objects": [summary(o) for o in group]}
        for sig, group in sorted(groups.items())
        if len(group) > 1
    ]


def consumers_by_variable(cv: dict[str, Any]) -> dict[str, list[dict[str, str | None]]]:
    consumers: dict[str, list[dict[str, str | None]]] = collections.defaultdict(list)
    layers = (
        ("tag", "tagId", cv.get("tag", []) or []),
        ("trigger", "triggerId", cv.get("trigger", []) or []),
        ("variable", "variableId", cv.get("variable", []) or []),
    )
    for layer, id_key, items in layers:
        for item in items:
            for ref in references(item):
                if layer == "variable" and ref == item.get("name"):
                    continue
                consumers[ref].append(
                    {"layer": layer, "id": item.get(id_key), "name": item.get("name")}
                )
    return dict(sorted(consumers.items()))


def trigger_group_members(trigger: dict[str, Any]) -> list[str]:
    members = []
    for group in trigger.get("parameter", []) or []:
        if group.get("key") == "triggerIds":
            for item in group.get("list", []) or []:
                if item.get("value"):
                    members.append(item["value"])
    return members


def custom_template_id(obj: dict[str, Any]) -> str | None:
    match = CUSTOM_TEMPLATE_RE.match(str(obj.get("type", "")))
    return match.group(1) if match else None


def text_blob(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def detect_vendor(obj: dict[str, Any]) -> str:
    text = " ".join(str(part or "") for part in (obj.get("name"), obj.get("type"), text_blob(obj)))
    for vendor, pattern in VENDOR_PATTERNS:
        if pattern.search(text):
            return vendor
    return "Unclassified"


def detect_ecommerce_role(obj: dict[str, Any]) -> str | None:
    text = " ".join(str(part or "") for part in (obj.get("name"), obj.get("type"), text_blob(obj)))
    for role, pattern in ECOM_ROLE_PATTERNS:
        if pattern.search(text):
            return role
    return None


def likely_event_name(tag: dict[str, Any]) -> str | None:
    for key in ("eventName", "event_name", "name", "trackingId"):
        value = param_value(tag, key)
        if isinstance(value, str) and value:
            return value
    role = detect_ecommerce_role(tag)
    return role


def custom_code_risks(obj: dict[str, Any]) -> list[str]:
    js = param_value(obj, "javascript") or param_value(obj, "html")
    if not js:
        return []
    text = str(js)
    risks = []
    if re.search(r"\[[0-9]+\]", text):
        risks.append("fixed_index")
    if "dataLayer" in text and re.search(r"for\s*\(|while\s*\(|\.filter|\.map|\.reduce", text) is None:
        risks.append("possible_stale_or_single_push_read")
    if re.search(r"parseFloat|parseInt|Number\(", text) and not re.search(r"isNaN|Number\.isNaN|isFinite", text):
        risks.append("numeric_parse_without_nan_guard")
    if re.search(r"document\.querySelector|getElementById|getElementsBy", text) and "null" not in text:
        risks.append("dom_lookup_without_null_guard")
    if re.search(r"function\s+\w+\s*\(", text) and not re.search(r"\w+\s*\(", text.split("function", 1)[-1]):
        risks.append("function_definition_may_be_noop")
    return sorted(set(risks))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Path to a GTM container export JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    data = json.loads(args.export.read_text(encoding="utf-8"))
    cv = container_version(data)

    tags = cv.get("tag", []) or []
    triggers = cv.get("trigger", []) or []
    variables = cv.get("variable", []) or []
    folders = cv.get("folder", []) or []
    templates = cv.get("customTemplate", []) or []
    builtins = cv.get("builtInVariable", []) or []

    variable_consumers = consumers_by_variable(cv)
    variable_names = {v.get("name") for v in variables}
    builtin_names = {b.get("name") for b in builtins}
    all_variable_names = variable_names | builtin_names

    all_refs = sorted(set(REF_RE.findall(json.dumps(cv, ensure_ascii=False))))
    undefined_refs = [ref for ref in all_refs if ref not in all_variable_names]

    tag_names = {t.get("name") for t in tags if t.get("name")}
    setup_tag_refs = []
    teardown_tag_refs = []
    folder_ids = {f.get("folderId") for f in folders}
    custom_template_ids = {t.get("templateId") for t in templates}
    parent_folder_refs = []
    custom_template_refs = []
    for layer, id_key, items in (
        ("tag", "tagId", tags),
        ("variable", "variableId", variables),
    ):
        for item in items:
            template_id = custom_template_id(item)
            if template_id:
                custom_template_refs.append(
                    {
                        "layer": layer,
                        "id": item.get(id_key),
                        "name": item.get("name"),
                        "templateId": template_id,
                        "type": item.get("type"),
                    }
                )

    for layer, id_key, items in (
        ("tag", "tagId", tags),
        ("trigger", "triggerId", triggers),
        ("variable", "variableId", variables),
    ):
        for item in items:
            if item.get("parentFolderId"):
                parent_folder_refs.append(
                    {
                        "layer": layer,
                        "id": item.get(id_key),
                        "name": item.get("name"),
                        "folderId": item.get("parentFolderId"),
                    }
                )
    trigger_ids = {t.get("triggerId") for t in triggers}
    trigger_by_id = {t.get("triggerId"): t for t in triggers}
    trigger_consumers: dict[str, list[dict[str, str | None]]] = collections.defaultdict(list)
    used_trigger_ids = set()
    for tag in tags:
        for tid in tag.get("firingTriggerId", []) or []:
            used_trigger_ids.add(tid)
            trigger_consumers[tid].append(
                {"layer": "tag", "id": tag.get("tagId"), "name": tag.get("name")}
            )
        for tid in tag.get("blockingTriggerId", []) or []:
            used_trigger_ids.add(tid)
            trigger_consumers[tid].append(
                {"layer": "tag", "id": tag.get("tagId"), "name": tag.get("name")}
            )
        for ref in tag.get("setupTag", []) or []:
            if ref.get("tagName"):
                setup_tag_refs.append(
                    {
                        "sourceTagId": tag.get("tagId"),
                        "sourceTagName": tag.get("name"),
                        "tagName": ref.get("tagName"),
                    }
                )
        for ref in tag.get("teardownTag", []) or []:
            if ref.get("tagName"):
                teardown_tag_refs.append(
                    {
                        "sourceTagId": tag.get("tagId"),
                        "sourceTagName": tag.get("name"),
                        "tagName": ref.get("tagName"),
                    }
                )
    for trigger in triggers:
        for member_id in trigger_group_members(trigger):
            used_trigger_ids.add(member_id)

    variable_path_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    ecommerce_variables = []
    legacy_ua_ecommerce_variables = []
    for variable in variables:
        dl_path = param_value(variable, "name")
        js = param_value(variable, "javascript")
        text = " ".join(
            str(part or "") for part in (variable.get("name"), dl_path, js)
        )
        legacy_ua_path = bool(LEGACY_UA_ECOM_RE.search(text))
        if dl_path:
            variable_path_groups[str(dl_path)].append(variable)
        if ECOM_RE.search(text):
            ecommerce_variables.append(
                {
                    **summary(variable),
                    "dataLayerPath": dl_path,
                    "hasCustomJavascript": bool(js),
                    "legacyUaEcommercePath": legacy_ua_path,
                    "consumerCount": len(variable_consumers.get(variable.get("name"), [])),
                }
            )
        if legacy_ua_path:
            legacy_ua_ecommerce_variables.append(
                {
                    **summary(variable),
                    "dataLayerPath": dl_path,
                    "hasCustomJavascript": bool(js),
                    "consumerCount": len(variable_consumers.get(variable.get("name"), [])),
                }
            )

    vendor_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    tag_semantics = []
    for tag in tags:
        vendor = detect_vendor(tag)
        role = detect_ecommerce_role(tag) or "unknown"
        vendor_groups[vendor].append(summary(tag))
        tag_semantics.append(
            {
                **summary(tag),
                "vendorFamily": vendor,
                "likelyEventOrRole": likely_event_name(tag) or role,
                "referencedVariables": references(tag),
                "customTemplateId": custom_template_id(tag),
                "customCodeRisks": custom_code_risks(tag),
                "hasConsentSettings": bool(tag.get("consentSettings")),
                "firingTriggerCount": len(tag.get("firingTriggerId", []) or []),
                "blockingTriggerCount": len(tag.get("blockingTriggerId", []) or []),
            }
        )

    variable_semantics = []
    for variable in variables:
        variable_semantics.append(
            {
                **summary(variable),
                "vendorFamily": detect_vendor(variable),
                "ecommerceRole": detect_ecommerce_role(variable),
                "dataLayerPath": param_value(variable, "name"),
                "referencedVariables": references(variable),
                "consumerCount": len(variable_consumers.get(variable.get("name"), [])),
                "customTemplateId": custom_template_id(variable),
                "customCodeRisks": custom_code_risks(variable),
                "legacyUaEcommercePath": bool(
                    LEGACY_UA_ECOM_RE.search(
                        " ".join(
                            str(part or "")
                            for part in (
                                variable.get("name"),
                                param_value(variable, "name"),
                                param_value(variable, "javascript"),
                            )
                        )
                    )
                ),
            }
        )

    risk_signals = []
    if undefined_refs:
        risk_signals.append(
            {
                "risk": "undefined_variable_references",
                "severity": "High",
                "count": len(undefined_refs),
                "details": undefined_refs[:25],
            }
        )
    missing_triggers = sorted(tid for tid in used_trigger_ids if tid not in trigger_ids)
    if missing_triggers:
        risk_signals.append(
            {
                "risk": "missing_trigger_references",
                "severity": "High",
                "count": len(missing_triggers),
                "details": missing_triggers,
            }
        )
    single_member_groups = [
        trigger
        for trigger in triggers
        if trigger.get("type") == "TRIGGER_GROUP"
        and len(trigger_group_members(trigger)) == 1
    ]
    if single_member_groups:
        risk_signals.append(
            {
                "risk": "single_member_trigger_groups",
                "severity": "Medium",
                "count": len(single_member_groups),
                "details": [summary(trigger) for trigger in single_member_groups[:25]],
            }
        )
    tags_without_triggers = [t for t in tags if not (t.get("firingTriggerId") or [])]
    if tags_without_triggers:
        risk_signals.append(
            {
                "risk": "tags_without_firing_triggers",
                "severity": "High",
                "count": len(tags_without_triggers),
                "details": [summary(tag) for tag in tags_without_triggers[:25]],
            }
        )
    if legacy_ua_ecommerce_variables:
        risk_signals.append(
            {
                "risk": "legacy_ua_ecommerce_paths",
                "severity": "High",
                "count": len(legacy_ua_ecommerce_variables),
                "details": legacy_ua_ecommerce_variables[:25],
            }
        )
    risky_custom_code = [
        item
        for item in tag_semantics + variable_semantics
        if item.get("customCodeRisks")
    ]
    if risky_custom_code:
        risk_signals.append(
            {
                "risk": "custom_code_static_risks",
                "severity": "Medium",
                "count": len(risky_custom_code),
                "details": risky_custom_code[:25],
            }
        )

    route_hints = {
        "directGtmMcpApiPreferredFor": [
            "in-place naming standardization",
            "deleting obsolete objects",
            "readable GTM View Changes",
            "single-member trigger-group deletion",
            "broad consolidation",
        ],
        "jsonRouteWarnings": [
            "same-container merge conflicts are name-based",
            "same-container merge cannot reliably delete omitted existing objects",
            "View Changes JSON should preserve existing names",
            "builtInVariable and customTemplate schema layers need special handling",
        ],
    }

    result = {
        "source": str(args.export),
        "exportTime": data.get("exportTime") or cv.get("exportTime"),
        "container": {
            "accountId": cv.get("accountId"),
            "containerId": cv.get("containerId"),
            "publicId": (cv.get("container") or {}).get("publicId"),
            "name": (cv.get("container") or {}).get("name"),
        },
        "counts": {
            "tags": len(tags),
            "triggers": len(triggers),
            "variables": len(variables),
            "folders": len(folders),
            "customTemplates": len(templates),
            "builtInVariables": len(builtins),
        },
        "tagTypes": dict(collections.Counter(t.get("type") for t in tags)),
        "triggerTypes": dict(collections.Counter(t.get("type") for t in triggers)),
        "variableTypes": dict(collections.Counter(v.get("type") for v in variables)),
        "duplicateNames": {
            "tags": duplicate_groups(tags, "name"),
            "triggers": duplicate_groups(triggers, "name"),
            "variables": duplicate_groups(variables, "name"),
            "folders": duplicate_groups(folders, "name"),
        },
        "duplicateConfigurations": {
            "tags": signature_groups(
                tags,
                {"accountId", "containerId", "tagId", "name", "fingerprint", "path"},
            ),
            "triggers": signature_groups(
                triggers,
                {"accountId", "containerId", "triggerId", "name", "fingerprint", "path"},
            ),
            "variables": signature_groups(
                variables,
                {"accountId", "containerId", "variableId", "name", "fingerprint", "path"},
            ),
        },
        "variablePathDuplicates": [
            {"path": path, "variables": [summary(v) for v in group]}
            for path, group in sorted(variable_path_groups.items())
            if len(group) > 1
        ],
        "unusedCandidates": {
            "triggers": [
                summary(t)
                for t in triggers
                if t.get("triggerId") not in used_trigger_ids
            ],
            "variables": [
                summary(v)
                for v in variables
                if not variable_consumers.get(v.get("name"))
            ],
            "tagsWithoutFiringTriggers": [
                summary(t) for t in tags if not (t.get("firingTriggerId") or [])
            ],
        },
        "triggerGroupCandidates": {
            "singleMemberTriggerGroups": [
                {
                    **summary(trigger),
                    "memberTriggerId": trigger_group_members(trigger)[0],
                    "memberTriggerName": (
                        trigger_by_id.get(trigger_group_members(trigger)[0]) or {}
                    ).get("name"),
                    "consumerCount": len(trigger_consumers.get(trigger.get("triggerId"), [])),
                    "consumers": trigger_consumers.get(trigger.get("triggerId"), []),
                }
                for trigger in triggers
                if trigger.get("type") == "TRIGGER_GROUP"
                and len(trigger_group_members(trigger)) == 1
            ],
        },
        "semanticHints": {
            "vendorFamilies": {
                vendor: objects
                for vendor, objects in sorted(vendor_groups.items())
            },
            "tagSemantics": tag_semantics,
            "variableSemantics": variable_semantics,
            "routeHints": route_hints,
        },
        "riskSignals": risk_signals,
        "references": {
            "undefinedVariableReferences": undefined_refs,
            "missingTriggerReferences": sorted(
                tid for tid in used_trigger_ids if tid not in trigger_ids
            ),
            "missingSetupTagReferences": sorted(
                {
                    ref["tagName"]
                    for ref in setup_tag_refs
                    if ref["tagName"] not in tag_names
                }
            ),
            "missingTeardownTagReferences": sorted(
                {
                    ref["tagName"]
                    for ref in teardown_tag_refs
                    if ref["tagName"] not in tag_names
                }
            ),
            "missingFolderReferences": sorted(
                {
                    ref["folderId"]
                    for ref in parent_folder_refs
                    if ref["folderId"] not in folder_ids
                }
            ),
            "missingCustomTemplateReferences": sorted(
                {
                    ref["templateId"]
                    for ref in custom_template_refs
                    if ref["templateId"] not in custom_template_ids
                }
            ),
            "setupTagReferences": setup_tag_refs,
            "teardownTagReferences": teardown_tag_refs,
            "parentFolderReferences": parent_folder_refs,
            "customTemplateReferences": custom_template_refs,
        },
        "ecommerceVariableCandidates": ecommerce_variables,
        "legacyUaEcommercePathCandidates": legacy_ua_ecommerce_variables,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
