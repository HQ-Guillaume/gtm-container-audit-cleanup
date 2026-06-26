#!/usr/bin/env python3
"""Create a GTM import JSON prepared for same-container View Changes.

Google Tag Manager merge conflicts are name-based. This script preserves
existing object names and rewrites variable/setup/teardown references back to
those names so GTM can show modified objects instead of delete/add churn.
Naming standardization must be applied through direct GTM/API cleanup or a
separate final-state artifact.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from gtm_make_merge_patch import (
    ID_KEYS,
    comparable_container,
    container_version,
    custom_template_id,
    merge_patch,
    object_id,
    reconstruct,
)


NAME_PRESERVE_LAYERS = ("tag", "trigger", "variable", "folder", "customTemplate")


def objects_by_id(cv: dict[str, Any], layer: str) -> dict[str, dict[str, Any]]:
    id_key = ID_KEYS[layer]
    return {
        object_id(obj, id_key): obj
        for obj in cv.get(layer, []) or []
        if object_id(obj, id_key) is not None
    }


def name_maps(
    original_cv: dict[str, Any], optimized_cv: dict[str, Any]
) -> tuple[dict[str, str], dict[str, str], dict[str, dict[str, str]]]:
    variable_names: dict[str, str] = {}
    tag_names: dict[str, str] = {}
    layer_id_to_name: dict[str, dict[str, str]] = {}

    for layer in NAME_PRESERVE_LAYERS:
        original_by_id = objects_by_id(original_cv, layer)
        optimized_by_id = objects_by_id(optimized_cv, layer)
        id_to_old_name: dict[str, str] = {}
        for oid, optimized_obj in optimized_by_id.items():
            original_obj = original_by_id.get(oid)
            if not original_obj:
                continue
            old_name = original_obj.get("name")
            new_name = optimized_obj.get("name")
            if old_name:
                id_to_old_name[str(oid)] = old_name
            if old_name and new_name and old_name != new_name:
                if layer == "variable":
                    variable_names[new_name] = old_name
                elif layer == "tag":
                    tag_names[new_name] = old_name
        layer_id_to_name[layer] = id_to_old_name

    return variable_names, tag_names, layer_id_to_name


def restore_references(value: Any, variable_names: dict[str, str], tag_names: dict[str, str]) -> Any:
    if isinstance(value, list):
        return [restore_references(item, variable_names, tag_names) for item in value]
    if isinstance(value, dict):
        restored = {}
        for key, item in value.items():
            if key == "tagName" and isinstance(item, str) and item in tag_names:
                restored[key] = tag_names[item]
            else:
                restored[key] = restore_references(item, variable_names, tag_names)
        return restored
    if isinstance(value, str):
        restored = value
        for new_name, old_name in sorted(variable_names.items(), key=lambda item: len(item[0]), reverse=True):
            restored = restored.replace("{{" + new_name + "}}", "{{" + old_name + "}}")
        return restored
    return value


def name_preserving_target(original_cv: dict[str, Any], optimized_cv: dict[str, Any]) -> dict[str, Any]:
    target = deepcopy(optimized_cv)
    variable_names, tag_names, layer_id_to_name = name_maps(original_cv, optimized_cv)
    target = restore_references(target, variable_names, tag_names)

    for layer in NAME_PRESERVE_LAYERS:
        id_key = ID_KEYS[layer]
        old_names_by_id = layer_id_to_name.get(layer, {})
        for obj in target.get(layer, []) or []:
            oid = object_id(obj, id_key)
            if oid in old_names_by_id:
                obj["name"] = old_names_by_id[oid]

    return target


def ensure_full_schema_layers(patch_cv: dict[str, Any], target_cv: dict[str, Any]) -> None:
    if "builtInVariable" in target_cv:
        patch_cv["builtInVariable"] = target_cv.get("builtInVariable", []) or []

    referenced_template_ids = {
        template_id
        for layer in ("tag", "variable")
        for obj in patch_cv.get(layer, []) or []
        for template_id in [custom_template_id(obj)]
        if template_id
    }
    if referenced_template_ids:
        templates = target_cv.get("customTemplate", []) or []
        found_template_ids = {str(template.get("templateId")) for template in templates}
        missing_template_ids = sorted(referenced_template_ids - found_template_ids)
        if missing_template_ids:
            raise ValueError(
                "Changed objects reference custom templates missing from cleanup export: "
                + ", ".join(missing_template_ids)
            )
        patch_cv["customTemplate"] = templates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="Original GTM export JSON")
    parser.add_argument("optimized", type=Path, help="Full cleanup GTM export JSON")
    parser.add_argument("output", type=Path, help="Output name-preserving review JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    original_data = json.loads(args.original.read_text(encoding="utf-8"))
    optimized_data = json.loads(args.optimized.read_text(encoding="utf-8"))
    original_cv = container_version(original_data)
    optimized_cv = container_version(optimized_data)
    target_cv = name_preserving_target(original_cv, optimized_cv)

    patch_cv = merge_patch(original_cv, target_cv)
    ensure_full_schema_layers(patch_cv, target_cv)
    reconstructed = reconstruct(original_cv, patch_cv)
    if comparable_container(reconstructed) != comparable_container(target_cv):
        raise SystemExit("Patch validation failed: original + review patch does not match target")

    output_data = {
        "exportFormatVersion": optimized_data.get(
            "exportFormatVersion", original_data.get("exportFormatVersion", 2)
        ),
        "exportTime": optimized_data.get("exportTime"),
        "containerVersion": patch_cv,
    }
    args.output.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2 if args.pretty else None) + "\n",
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
