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

from gtm_lib import container_version, custom_template_id, refs, trigger_group_members
from gtm_taxonomy import (
    ECOM_RE,
    LEGACY_UA_ECOM_RE,
    detect_ecommerce_role,
    detect_vendor,
)


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
            for ref in sorted(refs(item)):
                if layer == "variable" and ref == item.get("name"):
                    continue
                consumers[ref].append(
                    {"layer": layer, "id": item.get(id_key), "name": item.get("name")}
                )
    return dict(sorted(consumers.items()))


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


def layer_items(cv: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    return {
        "tags": cv.get("tag", []) or [],
        "triggers": cv.get("trigger", []) or [],
        "variables": cv.get("variable", []) or [],
        "folders": cv.get("folder", []) or [],
        "templates": cv.get("customTemplate", []) or [],
        "builtins": cv.get("builtInVariable", []) or [],
    }


def collect_custom_template_refs(
    tags: list[dict[str, Any]], variables: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    references = []
    for layer, id_key, items in (("tag", "tagId", tags), ("variable", "variableId", variables)):
        for item in items:
            template_id = custom_template_id(item)
            if template_id:
                references.append(
                    {
                        "layer": layer,
                        "id": item.get(id_key),
                        "name": item.get("name"),
                        "templateId": template_id,
                        "type": item.get("type"),
                    }
                )
    return references


def collect_parent_folder_refs(
    tags: list[dict[str, Any]],
    triggers: list[dict[str, Any]],
    variables: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    references = []
    for layer, id_key, items in (
        ("tag", "tagId", tags),
        ("trigger", "triggerId", triggers),
        ("variable", "variableId", variables),
    ):
        for item in items:
            if item.get("parentFolderId"):
                references.append(
                    {
                        "layer": layer,
                        "id": item.get(id_key),
                        "name": item.get("name"),
                        "folderId": item.get("parentFolderId"),
                    }
                )
    return references


def collect_tag_references(
    tags: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    setup_tag_refs = []
    teardown_tag_refs = []
    for tag in tags:
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
    return setup_tag_refs, teardown_tag_refs


def collect_trigger_usage(
    tags: list[dict[str, Any]], triggers: list[dict[str, Any]]
) -> tuple[set[str], dict[str, list[dict[str, str | None]]]]:
    trigger_consumers: dict[str, list[dict[str, str | None]]] = collections.defaultdict(list)
    used_trigger_ids: set[str] = set()
    for tag in tags:
        for key in ("firingTriggerId", "blockingTriggerId"):
            for trigger_id in tag.get(key, []) or []:
                used_trigger_ids.add(trigger_id)
                trigger_consumers[trigger_id].append(
                    {"layer": "tag", "id": tag.get("tagId"), "name": tag.get("name")}
                )
    for trigger in triggers:
        for member_id in trigger_group_members(trigger):
            used_trigger_ids.add(member_id)
    return used_trigger_ids, trigger_consumers


def ecommerce_variable_hints(
    variables: list[dict[str, Any]],
    variable_consumers: dict[str, list[dict[str, str | None]]],
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]], list[dict[str, Any]]]:
    variable_path_groups: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    ecommerce_variables = []
    legacy_ua_ecommerce_variables = []
    for variable in variables:
        dl_path = param_value(variable, "name")
        js = param_value(variable, "javascript")
        text = " ".join(str(part or "") for part in (variable.get("name"), dl_path, js))
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
    return variable_path_groups, ecommerce_variables, legacy_ua_ecommerce_variables


def build_tag_semantics(
    tags: list[dict[str, Any]]
) -> tuple[dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
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
                "referencedVariables": sorted(refs(tag)),
                "customTemplateId": custom_template_id(tag),
                "customCodeRisks": custom_code_risks(tag),
                "hasConsentSettings": bool(tag.get("consentSettings")),
                "firingTriggerCount": len(tag.get("firingTriggerId", []) or []),
                "blockingTriggerCount": len(tag.get("blockingTriggerId", []) or []),
            }
        )
    return vendor_groups, tag_semantics


def build_variable_semantics(
    variables: list[dict[str, Any]],
    variable_consumers: dict[str, list[dict[str, str | None]]],
) -> list[dict[str, Any]]:
    rows = []
    for variable in variables:
        source_text = " ".join(
            str(part or "")
            for part in (
                variable.get("name"),
                param_value(variable, "name"),
                param_value(variable, "javascript"),
            )
        )
        rows.append(
            {
                **summary(variable),
                "vendorFamily": detect_vendor(variable),
                "ecommerceRole": detect_ecommerce_role(variable),
                "dataLayerPath": param_value(variable, "name"),
                "referencedVariables": sorted(refs(variable)),
                "consumerCount": len(variable_consumers.get(variable.get("name"), [])),
                "customTemplateId": custom_template_id(variable),
                "customCodeRisks": custom_code_risks(variable),
                "legacyUaEcommercePath": bool(LEGACY_UA_ECOM_RE.search(source_text)),
            }
        )
    return rows


def build_risk_signals(
    undefined_refs: list[str],
    missing_triggers: list[str],
    triggers: list[dict[str, Any]],
    tags: list[dict[str, Any]],
    legacy_ua_ecommerce_variables: list[dict[str, Any]],
    tag_semantics: list[dict[str, Any]],
    variable_semantics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    risk_signals = []
    if undefined_refs:
        risk_signals.append(
            {"risk": "undefined_variable_references", "severity": "High", "count": len(undefined_refs), "details": undefined_refs[:25]}
        )
    if missing_triggers:
        risk_signals.append(
            {"risk": "missing_trigger_references", "severity": "High", "count": len(missing_triggers), "details": missing_triggers}
        )

    single_member_groups = [
        trigger
        for trigger in triggers
        if trigger.get("type") == "TRIGGER_GROUP" and len(trigger_group_members(trigger)) == 1
    ]
    if single_member_groups:
        risk_signals.append(
            {"risk": "single_member_trigger_groups", "severity": "Medium", "count": len(single_member_groups), "details": [summary(trigger) for trigger in single_member_groups[:25]]}
        )

    tags_without_triggers = [tag for tag in tags if not (tag.get("firingTriggerId") or [])]
    if tags_without_triggers:
        risk_signals.append(
            {"risk": "tags_without_firing_triggers", "severity": "High", "count": len(tags_without_triggers), "details": [summary(tag) for tag in tags_without_triggers[:25]]}
        )
    if legacy_ua_ecommerce_variables:
        risk_signals.append(
            {"risk": "legacy_ua_ecommerce_paths", "severity": "High", "count": len(legacy_ua_ecommerce_variables), "details": legacy_ua_ecommerce_variables[:25]}
        )

    risky_custom_code = [item for item in tag_semantics + variable_semantics if item.get("customCodeRisks")]
    if risky_custom_code:
        risk_signals.append(
            {"risk": "custom_code_static_risks", "severity": "Medium", "count": len(risky_custom_code), "details": risky_custom_code[:25]}
        )
    return risk_signals


def route_hints() -> dict[str, list[str]]:
    return {
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


def duplicate_sections(
    tags: list[dict[str, Any]],
    triggers: list[dict[str, Any]],
    variables: list[dict[str, Any]],
    folders: list[dict[str, Any]],
    variable_path_groups: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    return {
        "duplicateNames": {
            "tags": duplicate_groups(tags, "name"),
            "triggers": duplicate_groups(triggers, "name"),
            "variables": duplicate_groups(variables, "name"),
            "folders": duplicate_groups(folders, "name"),
        },
        "duplicateConfigurations": {
            "tags": signature_groups(tags, {"accountId", "containerId", "tagId", "name", "fingerprint", "path"}),
            "triggers": signature_groups(triggers, {"accountId", "containerId", "triggerId", "name", "fingerprint", "path"}),
            "variables": signature_groups(variables, {"accountId", "containerId", "variableId", "name", "fingerprint", "path"}),
        },
        "variablePathDuplicates": [
            {"path": path, "variables": [summary(variable) for variable in group]}
            for path, group in sorted(variable_path_groups.items())
            if len(group) > 1
        ],
    }


def unused_section(
    triggers: list[dict[str, Any]],
    variables: list[dict[str, Any]],
    tags: list[dict[str, Any]],
    used_trigger_ids: set[str],
    variable_consumers: dict[str, list[dict[str, str | None]]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        "triggers": [summary(trigger) for trigger in triggers if trigger.get("triggerId") not in used_trigger_ids],
        "variables": [summary(variable) for variable in variables if not variable_consumers.get(variable.get("name"))],
        "tagsWithoutFiringTriggers": [summary(tag) for tag in tags if not (tag.get("firingTriggerId") or [])],
    }


def trigger_group_section(
    triggers: list[dict[str, Any]],
    trigger_by_id: dict[str, dict[str, Any]],
    trigger_consumers: dict[str, list[dict[str, str | None]]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        "singleMemberTriggerGroups": [
            {
                **summary(trigger),
                "memberTriggerId": trigger_group_members(trigger)[0],
                "memberTriggerName": (trigger_by_id.get(trigger_group_members(trigger)[0]) or {}).get("name"),
                "consumerCount": len(trigger_consumers.get(trigger.get("triggerId"), [])),
                "consumers": trigger_consumers.get(trigger.get("triggerId"), []),
            }
            for trigger in triggers
            if trigger.get("type") == "TRIGGER_GROUP" and len(trigger_group_members(trigger)) == 1
        ]
    }


def reference_section(
    undefined_refs: list[str],
    missing_triggers: list[str],
    setup_tag_refs: list[dict[str, Any]],
    teardown_tag_refs: list[dict[str, Any]],
    parent_folder_refs: list[dict[str, Any]],
    custom_template_refs: list[dict[str, Any]],
    tag_names: set[str],
    folder_ids: set[str],
    custom_template_ids: set[str],
) -> dict[str, Any]:
    return {
        "undefinedVariableReferences": undefined_refs,
        "missingTriggerReferences": missing_triggers,
        "missingSetupTagReferences": sorted({ref["tagName"] for ref in setup_tag_refs if ref["tagName"] not in tag_names}),
        "missingTeardownTagReferences": sorted({ref["tagName"] for ref in teardown_tag_refs if ref["tagName"] not in tag_names}),
        "missingFolderReferences": sorted({ref["folderId"] for ref in parent_folder_refs if ref["folderId"] not in folder_ids}),
        "missingCustomTemplateReferences": sorted({ref["templateId"] for ref in custom_template_refs if ref["templateId"] not in custom_template_ids}),
        "setupTagReferences": setup_tag_refs,
        "teardownTagReferences": teardown_tag_refs,
        "parentFolderReferences": parent_folder_refs,
        "customTemplateReferences": custom_template_refs,
    }


def metadata_sections(path: Path, data: dict[str, Any], cv: dict[str, Any], layers: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    tags = layers["tags"]
    triggers = layers["triggers"]
    variables = layers["variables"]
    return {
        "source": str(path),
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
            "folders": len(layers["folders"]),
            "customTemplates": len(layers["templates"]),
            "builtInVariables": len(layers["builtins"]),
        },
        "tagTypes": dict(collections.Counter(tag.get("type") for tag in tags)),
        "triggerTypes": dict(collections.Counter(trigger.get("type") for trigger in triggers)),
        "variableTypes": dict(collections.Counter(variable.get("type") for variable in variables)),
    }


def semantic_hints_section(
    vendor_groups: dict[str, list[dict[str, Any]]],
    tag_semantics: list[dict[str, Any]],
    variable_semantics: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "vendorFamilies": {vendor: objects for vendor, objects in sorted(vendor_groups.items())},
        "tagSemantics": tag_semantics,
        "variableSemantics": variable_semantics,
        "routeHints": route_hints(),
    }


def inspect_export(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cv = container_version(data)
    layers = layer_items(cv)
    tags = layers["tags"]
    triggers = layers["triggers"]
    variables = layers["variables"]
    folders = layers["folders"]
    templates = layers["templates"]
    builtins = layers["builtins"]

    variable_consumers = consumers_by_variable(cv)
    all_variable_names = {v.get("name") for v in variables} | {b.get("name") for b in builtins}
    undefined_refs = [ref for ref in sorted(refs(cv)) if ref not in all_variable_names]

    tag_names = {tag.get("name") for tag in tags if tag.get("name")}
    trigger_ids = {trigger.get("triggerId") for trigger in triggers}
    trigger_by_id = {trigger.get("triggerId"): trigger for trigger in triggers}
    folder_ids = {folder.get("folderId") for folder in folders}
    custom_template_ids = {template.get("templateId") for template in templates}

    setup_tag_refs, teardown_tag_refs = collect_tag_references(tags)
    parent_folder_refs = collect_parent_folder_refs(tags, triggers, variables)
    custom_template_refs = collect_custom_template_refs(tags, variables)
    used_trigger_ids, trigger_consumers = collect_trigger_usage(tags, triggers)
    missing_triggers = sorted(trigger_id for trigger_id in used_trigger_ids if trigger_id not in trigger_ids)

    variable_path_groups, ecommerce_variables, legacy_ua_ecommerce_variables = ecommerce_variable_hints(
        variables, variable_consumers
    )
    vendor_groups, tag_semantics = build_tag_semantics(tags)
    variable_semantics = build_variable_semantics(variables, variable_consumers)
    risk_signals = build_risk_signals(
        undefined_refs,
        missing_triggers,
        triggers,
        tags,
        legacy_ua_ecommerce_variables,
        tag_semantics,
        variable_semantics,
    )

    result: dict[str, Any] = {
        **metadata_sections(path, data, cv, layers),
        **duplicate_sections(tags, triggers, variables, folders, variable_path_groups),
        "unusedCandidates": unused_section(
            triggers, variables, tags, used_trigger_ids, variable_consumers
        ),
        "triggerGroupCandidates": trigger_group_section(
            triggers, trigger_by_id, trigger_consumers
        ),
        "semanticHints": semantic_hints_section(vendor_groups, tag_semantics, variable_semantics),
        "riskSignals": risk_signals,
        "references": reference_section(
            undefined_refs,
            missing_triggers,
            setup_tag_refs,
            teardown_tag_refs,
            parent_folder_refs,
            custom_template_refs,
            tag_names,
            folder_ids,
            custom_template_ids,
        ),
        "ecommerceVariableCandidates": ecommerce_variables,
        "legacyUaEcommercePathCandidates": legacy_ua_ecommerce_variables,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Path to a GTM container export JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    result = inspect_export(args.export)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
