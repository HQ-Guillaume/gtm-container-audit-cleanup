#!/usr/bin/env python3
"""Create a minimal same-container GTM merge patch from a cleanup export."""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


ID_KEYS = {
    "tag": "tagId",
    "trigger": "triggerId",
    "variable": "variableId",
    "folder": "folderId",
    "builtInVariable": "name",
    "customTemplate": "templateId",
}

IGNORED_FOR_CHANGE = {"path", "fingerprint"}
FOLDER_REFERENCING_LAYERS = ("tag", "trigger", "variable")
CUSTOM_TEMPLATE_RE = re.compile(r"^cvt_\d+_(\d+)$")


def container_version(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("containerVersion", data)


def object_id(obj: dict[str, Any], id_key: str) -> str | None:
    value = obj.get(id_key) or obj.get("name")
    return str(value) if value is not None else None


def comparable(obj: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in obj.items() if k not in IGNORED_FOR_CHANGE}


def custom_template_id(obj: dict[str, Any]) -> str | None:
    match = CUSTOM_TEMPLATE_RE.match(str(obj.get("type", "")))
    return match.group(1) if match else None


def merge_patch(original_cv: dict[str, Any], optimized_cv: dict[str, Any]) -> dict[str, Any]:
    patch_cv = {k: v for k, v in optimized_cv.items() if not isinstance(v, list)}

    for layer, id_key in ID_KEYS.items():
        original_objects = original_cv.get(layer, []) or []
        optimized_objects = optimized_cv.get(layer, []) or []
        original_by_id = {
            object_id(obj, id_key): obj
            for obj in original_objects
            if object_id(obj, id_key) is not None
        }

        changed = []
        for obj in optimized_objects:
            oid = object_id(obj, id_key)
            before = original_by_id.get(oid)
            if before is None or comparable(obj) != comparable(before):
                changed.append(obj)

        if changed:
            patch_cv[layer] = changed

    if "builtInVariable" in original_cv or "builtInVariable" in optimized_cv:
        patch_cv["builtInVariable"] = optimized_cv.get("builtInVariable", []) or []

    referenced_folder_ids = {
        str(obj["parentFolderId"])
        for layer in FOLDER_REFERENCING_LAYERS
        for obj in patch_cv.get(layer, []) or []
        if obj.get("parentFolderId")
    }
    if referenced_folder_ids:
        folders = [
            folder
            for folder in optimized_cv.get("folder", []) or []
            if str(folder.get("folderId")) in referenced_folder_ids
        ]
        found_folder_ids = {str(folder.get("folderId")) for folder in folders}
        missing_folder_ids = sorted(referenced_folder_ids - found_folder_ids)
        if missing_folder_ids:
            raise ValueError(
                "Changed objects reference folders missing from cleanup export: "
                + ", ".join(missing_folder_ids)
            )
        patch_cv["folder"] = folders

    referenced_template_ids = {
        template_id
        for layer in ("tag", "variable")
        for obj in patch_cv.get(layer, []) or []
        for template_id in [custom_template_id(obj)]
        if template_id
    }
    if referenced_template_ids:
        templates = optimized_cv.get("customTemplate", []) or []
        found_template_ids = {str(template.get("templateId")) for template in templates}
        missing_template_ids = sorted(referenced_template_ids - found_template_ids)
        if missing_template_ids:
            raise ValueError(
                "Changed objects reference custom templates missing from cleanup export: "
                + ", ".join(missing_template_ids)
            )
        patch_cv["customTemplate"] = templates

    return patch_cv


def reconstruct(original_cv: dict[str, Any], patch_cv: dict[str, Any]) -> dict[str, Any]:
    merged = deepcopy(original_cv)
    for layer, id_key in ID_KEYS.items():
        replacements = patch_cv.get(layer)
        if not replacements:
            continue

        by_id = {
            object_id(obj, id_key): obj
            for obj in replacements
            if object_id(obj, id_key) is not None
        }
        seen: set[str] = set()
        next_objects = []
        for obj in merged.get(layer, []) or []:
            oid = object_id(obj, id_key)
            if oid in by_id:
                next_objects.append(by_id[oid])
                seen.add(str(oid))
            else:
                next_objects.append(obj)

        for oid, obj in by_id.items():
            if oid not in seen:
                next_objects.append(obj)

        merged[layer] = next_objects

    return merged


def comparable_container(cv: dict[str, Any]) -> dict[str, Any]:
    clean = {}
    for key, value in cv.items():
        if isinstance(value, list):
            clean[key] = [comparable(obj) if isinstance(obj, dict) else obj for obj in value]
        elif key not in IGNORED_FOR_CHANGE:
            clean[key] = value
    return clean


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Original GTM export JSON")
    parser.add_argument("optimized", type=Path, help="Full cleanup GTM export JSON")
    parser.add_argument("output", type=Path, help="Output minimal merge patch JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    original_data = json.loads(args.original.read_text(encoding="utf-8"))
    optimized_data = json.loads(args.optimized.read_text(encoding="utf-8"))
    original_cv = container_version(original_data)
    optimized_cv = container_version(optimized_data)

    patch_cv = merge_patch(original_cv, optimized_cv)
    patch_data = {
        "exportFormatVersion": optimized_data.get(
            "exportFormatVersion", original_data.get("exportFormatVersion", 2)
        ),
        "exportTime": optimized_data.get("exportTime"),
        "containerVersion": patch_cv,
    }

    reconstructed = reconstruct(original_cv, patch_cv)
    if comparable_container(reconstructed) != comparable_container(optimized_cv):
        raise SystemExit("Patch validation failed: original + patch does not match cleanup export")

    args.output.write_text(
        json.dumps(patch_data, ensure_ascii=False, indent=2 if args.pretty else None) + "\n",
        encoding="utf-8",
    )

    summary = {
        layer: len(patch_cv.get(layer, []) or [])
        for layer in ID_KEYS
        if patch_cv.get(layer)
    }
    print(json.dumps({"output": str(args.output), "includedObjectCounts": summary}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
