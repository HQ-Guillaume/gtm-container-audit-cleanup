#!/usr/bin/env python3
"""Validate GTM exports or generated import JSON against cleanup guardrails."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


ID_KEYS = {
    "tag": "tagId",
    "trigger": "triggerId",
    "variable": "variableId",
    "folder": "folderId",
    "customTemplate": "templateId",
    "builtInVariable": "name",
}
PATCH_MODES = {"same-container-view", "same-container-final"}

REF_RE = re.compile(r"\{\{([^{}]+)\}\}")
CUSTOM_TEMPLATE_RE = re.compile(r"^cvt_\d+_(\d+)$")


def container_version(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("containerVersion", data)


def load_cv(path: Path) -> dict[str, Any]:
    return container_version(json.loads(path.read_text(encoding="utf-8")))


def object_id(obj: dict[str, Any], key: str) -> str:
    value = obj.get(key) or obj.get("name")
    return "" if value is None else str(value)


def apply_patch(original_cv: dict[str, Any], patch_cv: dict[str, Any]) -> dict[str, Any]:
    merged = json.loads(json.dumps(original_cv))
    for layer, key in ID_KEYS.items():
        replacements = patch_cv.get(layer)
        if not replacements:
            continue
        by_id = {
            object_id(obj, key): obj
            for obj in replacements
            if object_id(obj, key)
        }
        seen = set()
        next_objects = []
        for obj in merged.get(layer, []) or []:
            oid = object_id(obj, key)
            if oid in by_id:
                next_objects.append(by_id[oid])
                seen.add(oid)
            else:
                next_objects.append(obj)
        for oid, obj in by_id.items():
            if oid not in seen:
                next_objects.append(obj)
        merged[layer] = next_objects
    return merged


def refs(obj: Any) -> set[str]:
    return set(REF_RE.findall(json.dumps(obj, ensure_ascii=False)))


def trigger_group_members(trigger: dict[str, Any]) -> list[str]:
    members = []
    for parameter in trigger.get("parameter", []) or []:
        if parameter.get("key") == "triggerIds":
            members.extend(
                item.get("value")
                for item in parameter.get("list", []) or []
                if item.get("value")
            )
    return members


def custom_template_id(obj: dict[str, Any]) -> str | None:
    match = CUSTOM_TEMPLATE_RE.match(str(obj.get("type", "")))
    return match.group(1) if match else None


def duplicate_ids(cv: dict[str, Any]) -> dict[str, list[str]]:
    result = {}
    for layer, key in ID_KEYS.items():
        seen = set()
        dupes = set()
        for obj in cv.get(layer, []) or []:
            oid = object_id(obj, key)
            if not oid:
                continue
            if oid in seen:
                dupes.add(oid)
            seen.add(oid)
        if dupes:
            result[layer] = sorted(dupes)
    return result


def missing_references(cv: dict[str, Any]) -> dict[str, Any]:
    tags = cv.get("tag", []) or []
    triggers = cv.get("trigger", []) or []
    variables = cv.get("variable", []) or []
    folders = cv.get("folder", []) or []
    templates = cv.get("customTemplate", []) or []
    builtins = cv.get("builtInVariable", []) or []

    variable_names = {v.get("name") for v in variables if v.get("name")}
    builtin_names = {b.get("name") for b in builtins if b.get("name")}
    all_variable_names = variable_names | builtin_names
    all_refs = refs(cv)

    tag_names = {tag.get("name") for tag in tags if tag.get("name")}
    trigger_ids = {trigger.get("triggerId") for trigger in triggers}
    folder_ids = {folder.get("folderId") for folder in folders}
    template_ids = {template.get("templateId") for template in templates}

    used_trigger_ids = set()
    setup_tag_refs = set()
    teardown_tag_refs = set()
    folder_refs = set()
    template_refs = set()

    for tag in tags:
        used_trigger_ids.update(tag.get("firingTriggerId", []) or [])
        used_trigger_ids.update(tag.get("blockingTriggerId", []) or [])
        for ref in tag.get("setupTag", []) or []:
            if ref.get("tagName"):
                setup_tag_refs.add(ref["tagName"])
        for ref in tag.get("teardownTag", []) or []:
            if ref.get("tagName"):
                teardown_tag_refs.add(ref["tagName"])

    for trigger in triggers:
        used_trigger_ids.update(trigger_group_members(trigger))

    for layer in ("tag", "trigger", "variable"):
        for obj in cv.get(layer, []) or []:
            if obj.get("parentFolderId"):
                folder_refs.add(obj["parentFolderId"])

    for layer in ("tag", "variable"):
        for obj in cv.get(layer, []) or []:
            template_id = custom_template_id(obj)
            if template_id:
                template_refs.add(template_id)

    return {
        "undefinedVariableReferences": sorted(ref for ref in all_refs if ref not in all_variable_names),
        "missingTriggerReferences": sorted(tid for tid in used_trigger_ids if tid not in trigger_ids),
        "missingSetupTagReferences": sorted(name for name in setup_tag_refs if name not in tag_names),
        "missingTeardownTagReferences": sorted(name for name in teardown_tag_refs if name not in tag_names),
        "missingFolderReferences": sorted(folder for folder in folder_refs if folder not in folder_ids),
        "missingCustomTemplateReferences": sorted(template for template in template_refs if template not in template_ids),
        "referencedCustomTemplateIds": sorted(template_refs),
    }


def name_churn(original_cv: dict[str, Any], cv: dict[str, Any]) -> dict[str, Any]:
    churn = {}
    for layer in ("tag", "trigger", "variable", "folder", "customTemplate"):
        key = ID_KEYS[layer]
        original = {
            object_id(obj, key): obj
            for obj in original_cv.get(layer, []) or []
            if object_id(obj, key)
        }
        current = {
            object_id(obj, key): obj
            for obj in cv.get(layer, []) or []
            if object_id(obj, key)
        }
        renamed = [
            {
                "id": oid,
                "before": original[oid].get("name"),
                "after": current[oid].get("name"),
            }
            for oid in sorted(set(original) & set(current), key=lambda value: (not value.isdigit(), value))
            if original[oid].get("name") != current[oid].get("name")
        ]
        new_ids = sorted(set(current) - set(original), key=lambda value: (not value.isdigit(), value))
        omitted_ids = sorted(set(original) - set(current), key=lambda value: (not value.isdigit(), value))
        churn[layer] = {
            "renamedExistingCount": len(renamed),
            "renamedExisting": renamed[:25],
            "newIdsCount": len(new_ids),
            "newIds": new_ids[:25],
            "omittedOriginalIdsCount": len(omitted_ids),
            "omittedOriginalIds": omitted_ids[:25],
        }
    return churn


def single_member_groups(cv: dict[str, Any]) -> list[dict[str, Any]]:
    groups = []
    for trigger in cv.get("trigger", []) or []:
        members = trigger_group_members(trigger)
        if trigger.get("type") == "TRIGGER_GROUP" and len(members) == 1:
            groups.append(
                {
                    "triggerId": trigger.get("triggerId"),
                    "name": trigger.get("name"),
                    "memberTriggerId": members[0],
                }
            )
    return groups


def validate(path: Path, original: Path | None, mode: str) -> dict[str, Any]:
    artifact_cv = load_cv(path)
    original_cv = load_cv(original) if original else None
    effective_cv = (
        apply_patch(original_cv, artifact_cv)
        if original_cv and mode in PATCH_MODES
        else artifact_cv
    )
    missing = missing_references(effective_cv)
    original_missing = missing_references(original_cv) if original_cv else None
    errors = []
    warnings = []

    dupes = duplicate_ids(effective_cv)
    if dupes:
        errors.append({"check": "unique_ids", "details": dupes})

    missing_blockers = {}
    for key, value in missing.items():
        if key == "referencedCustomTemplateIds" or not value:
            continue
        if original_missing:
            baseline = set(original_missing.get(key, []) or [])
            new_values = sorted(set(value) - baseline)
            if new_values:
                missing_blockers[key] = new_values
        else:
            missing_blockers[key] = value
    if missing_blockers:
        errors.append({"check": "missing_references", "details": missing_blockers})

    patch_missing = missing_references(artifact_cv)
    if patch_missing["referencedCustomTemplateIds"] and not (artifact_cv.get("customTemplate") or []):
        errors.append({"check": "custom_template_layer_missing", "details": missing["referencedCustomTemplateIds"]})

    if patch_missing["referencedCustomTemplateIds"]:
        all_templates = artifact_cv.get("customTemplate", []) or []
        if mode in PATCH_MODES and len(all_templates) < len(patch_missing["referencedCustomTemplateIds"]):
            errors.append({"check": "partial_custom_template_layer", "details": "customTemplate layer is smaller than referenced template set"})
        if original_cv and mode in PATCH_MODES:
            original_template_ids = {
                template.get("templateId")
                for template in original_cv.get("customTemplate", []) or []
                if template.get("templateId")
            }
            artifact_template_ids = {
                template.get("templateId")
                for template in all_templates
                if template.get("templateId")
            }
            missing_original_templates = sorted(original_template_ids - artifact_template_ids)
            if missing_original_templates:
                errors.append(
                    {
                        "check": "incomplete_same_container_custom_template_layer",
                        "details": missing_original_templates,
                    }
                )

    if original_cv and (original_cv.get("builtInVariable") or []) and "builtInVariable" not in artifact_cv:
        errors.append({"check": "built_in_variables_omitted", "details": "Source export has enabled built-ins but artifact omits builtInVariable."})

    groups = single_member_groups(effective_cv)
    if groups and mode in {"direct-readback", "overwrite", "new-container"}:
        errors.append({"check": "single_member_trigger_groups", "details": groups})
    elif groups:
        warnings.append({"check": "single_member_trigger_groups_route_limited", "details": groups})

    churn = name_churn(original_cv, artifact_cv) if original_cv else {}
    if mode == "same-container-view" and churn:
        rename_count = sum(layer["renamedExistingCount"] for layer in churn.values())
        new_count = sum(layer["newIdsCount"] for layer in churn.values())
        if rename_count or new_count:
            errors.append(
                {
                    "check": "view_changes_churn",
                    "details": {"renamedExisting": rename_count, "newIds": new_count},
                }
            )

    return {
        "artifact": str(path),
        "mode": mode,
        "status": "pass" if not errors else "fail",
        "artifactCounts": {layer: len(artifact_cv.get(layer, []) or []) for layer in ID_KEYS},
        "effectiveCounts": {layer: len(effective_cv.get(layer, []) or []) for layer in ID_KEYS},
        "errors": errors,
        "warnings": warnings,
        "missingReferences": missing,
        "newMissingReferences": missing_blockers,
        "nameChurn": churn,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", type=Path, help="GTM export or import JSON to validate")
    parser.add_argument("--original", type=Path, help="Original export for route-specific comparison")
    parser.add_argument(
        "--mode",
        choices=("audit", "direct-readback", "same-container-view", "same-container-final", "overwrite", "new-container"),
        default="audit",
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    result = validate(args.artifact, args.original, args.mode)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 1 if result["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
