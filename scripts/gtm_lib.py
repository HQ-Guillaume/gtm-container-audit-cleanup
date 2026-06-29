#!/usr/bin/env python3
"""Shared dependency-free helpers for GTM cleanup scripts."""

from __future__ import annotations

import copy
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

IGNORED_FIELDS = {"path", "fingerprint"}
REF_RE = re.compile(r"\{\{([^{}]+)\}\}")
CUSTOM_TEMPLATE_RE = re.compile(r"^cvt_\d+_(\d+)$")
SYSTEM_TRIGGER_RE = re.compile(r"^2147479\d{3}$")

SYSTEM_VARIABLE_REFERENCES = {
    "_event": "GTM internal current event name used by Custom Event trigger filters",
}

KNOWN_SYSTEM_TRIGGER_REFERENCES = {
    "2147479553": "GTM system trigger reference, commonly exported for all-pages/pageview routes",
    "2147479573": "GTM system trigger reference, commonly exported for initialization or Google tag routes",
}


def container_version(data: dict[str, Any]) -> dict[str, Any]:
    return data.get("containerVersion", data)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_container_version(path: Path) -> dict[str, Any]:
    return container_version(load_json(path))


def object_id(obj: dict[str, Any], id_key: str) -> str:
    value = obj.get(id_key) or obj.get("name")
    return "" if value is None else str(value)


def optional_object_id(obj: dict[str, Any], id_key: str) -> str | None:
    value = obj.get(id_key) or obj.get("name")
    return str(value) if value is not None else None


def comparable(obj: dict[str, Any], ignored: set[str] | None = None) -> dict[str, Any]:
    ignored = IGNORED_FIELDS if ignored is None else ignored
    return {key: value for key, value in obj.items() if key not in ignored}


def comparable_container(cv: dict[str, Any], ignored: set[str] | None = None) -> dict[str, Any]:
    clean: dict[str, Any] = {}
    ignored = IGNORED_FIELDS if ignored is None else ignored
    for key, value in cv.items():
        if isinstance(value, list):
            clean[key] = [
                comparable(obj, ignored) if isinstance(obj, dict) else obj
                for obj in value
            ]
        elif key not in ignored:
            clean[key] = value
    return clean


def apply_patch(original_cv: dict[str, Any], patch_cv: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(original_cv)
    for layer, id_key in ID_KEYS.items():
        replacements = patch_cv.get(layer)
        if not replacements:
            continue
        by_id = {
            object_id(obj, id_key): obj
            for obj in replacements
            if object_id(obj, id_key)
        }
        seen: set[str] = set()
        next_objects = []
        for obj in merged.get(layer, []) or []:
            oid = object_id(obj, id_key)
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


def custom_template_id(obj: dict[str, Any]) -> str | None:
    match = CUSTOM_TEMPLATE_RE.match(str(obj.get("type", "")))
    return match.group(1) if match else None


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


def is_system_variable_reference(name: str) -> bool:
    return name in SYSTEM_VARIABLE_REFERENCES


def is_system_trigger_reference(trigger_id: str) -> bool:
    return trigger_id in KNOWN_SYSTEM_TRIGGER_REFERENCES or bool(SYSTEM_TRIGGER_RE.match(trigger_id))


def system_reference_description(kind: str, value: str) -> str:
    if kind == "variable":
        return SYSTEM_VARIABLE_REFERENCES.get(value, "GTM internal/system variable reference")
    if kind == "trigger":
        return KNOWN_SYSTEM_TRIGGER_REFERENCES.get(value, "GTM internal/system trigger reference")
    return "GTM internal/system reference"


def sort_ids(values: set[str]) -> list[str]:
    return sorted(values, key=lambda value: (not value.isdigit(), value))
