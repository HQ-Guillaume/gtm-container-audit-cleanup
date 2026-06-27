#!/usr/bin/env python3
"""Validate that a GTM audit workbook covers a source export.

This checker is intentionally mechanical. It does not decide whether the audit
judgments are correct; it catches execution failures such as missing semantic
rows for high-impact objects, missing custom-code export review, missing
reconciliation rows, and placeholder operations that defer audit work.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from gtm_audit_gate_check import (
    CUSTOM_CODE_SUMMARY_FIELDS,
    D3_REQUIRED_FIELDS,
    SEMANTIC_SUMMARY_FIELDS,
    depth_tokens,
    generic_or_blank,
    validate_semantic_depth_rows,
    validate_placeholder_language,
    validate_rows,
    validate_summary_quality,
)
from gtm_lib import container_version, custom_template_id
from gtm_taxonomy import is_high_impact, object_text
from gtm_workbook import find_sheet, load_xlsx_workbook


def object_name(obj: dict[str, Any]) -> str:
    return str(obj.get("name") or "")


def object_id(obj: dict[str, Any], id_key: str) -> str:
    value = obj.get(id_key) or obj.get("name") or ""
    return str(value)


def has_parameter(obj: dict[str, Any], key: str) -> bool:
    return any(param.get("key") == key for param in obj.get("parameter", []) or [])


def active_tag(tag: dict[str, Any]) -> bool:
    return str(tag.get("paused", "")).lower() != "true" and tag.get("paused") is not True


def is_custom_html_tag(tag: dict[str, Any]) -> bool:
    return str(tag.get("type", "")).lower() == "html" or has_parameter(tag, "html")


def is_custom_js_variable(variable: dict[str, Any]) -> bool:
    return str(variable.get("type", "")).lower() == "jsm" or has_parameter(variable, "javascript")


def normalize_layer(value: Any) -> str:
    text = str(value or "").strip().lower()
    if "tag" in text:
        return "tag"
    if "trigger" in text:
        return "trigger"
    if "variable" in text:
        return "variable"
    if "template" in text:
        return "template"
    return text


def row_matches(row: dict[str, Any], layer: str, source_id: str, source_name: str) -> bool:
    row_layer = normalize_layer(row.get("layer"))
    if row_layer and layer != row_layer:
        return False
    row_id = str(row.get("object_id") or row.get("object_path") or "").strip()
    row_name = str(row.get("object_name") or row.get("before_name") or "").strip()
    return bool((source_id and row_id == source_id) or (source_name and row_name == source_name))


def covered(rows: Iterable[dict[str, Any]], layer: str, source_id: str, source_name: str) -> bool:
    return any(row_matches(row, layer, source_id, source_name) for row in rows)


def semantic_decision_complete(row: dict[str, Any]) -> bool:
    required = (
        "inferred_business_role",
        "decision_outcome",
        "conversion_hierarchy",
        "platform_role",
        "expected_data_contract",
        "semantic_status",
        "depth_completed",
        "trigger_context_status",
        "configuration_logic_status",
        "source_or_code_logic_status",
        "evidence_level",
    )
    if not all(str(row.get(field) or "").strip() for field in required):
        return False
    required_depths = depth_tokens(row.get("depth_required"))
    completed_depths = depth_tokens(row.get("depth_completed"))
    if required_depths.intersection({"D1", "D2", "D3"}) - completed_depths:
        return False
    if "D3" in required_depths:
        if "D3" not in completed_depths:
            return False
        for field in D3_REQUIRED_FIELDS:
            if field not in row or generic_or_blank(row.get(field)):
                return False
    return True


def semantic_row_complete(
    rows: Iterable[dict[str, Any]], layer: str, source_id: str, source_name: str
) -> bool:
    return any(
        row_matches(row, layer, source_id, source_name) and semantic_decision_complete(row)
        for row in rows
    )


def export_review_done(row: dict[str, Any]) -> bool:
    value = str(row.get("export_review_completed") or "").strip().lower()
    return value in {"yes", "not applicable", "n/a"}


SCHEMA_REQUIRED_DUPLICATE_COLUMN_PAIRS = {
    "18 completion ledger": {
        frozenset(
            {
                "overall_status",
                "inventory_phase_status",
                "dependency_phase_status",
                "measurement_diagnosis_phase_status",
                "semantic_validation_phase_status",
                "cleanup_decision_phase_status",
                "report_reconciliation_phase_status",
            }
        )
    },
    "18b workstream reconciliation": {
        frozenset(
            {
                "total_source_count",
                "inventoried_count",
                "dependency_mapped_count",
                "measurement_diagnosed_count",
                "cleanup_decision_count",
            }
        ),
        frozenset({"deferred_count", "user_excluded_count", "unresolved_count"}),
        frozenset(
            {
                "inventory_phase_status",
                "dependency_phase_status",
                "measurement_diagnosis_phase_status",
                "semantic_validation_phase_status",
                "cleanup_decision_phase_status",
                "report_reconciliation_phase_status",
            }
        ),
    },
}


def schema_duplicate_allowed(sheet_name: str, left: str, right: str) -> bool:
    normalized_sheet = sheet_name.lower()
    pair = {left, right}
    for sheet_key, groups in SCHEMA_REQUIRED_DUPLICATE_COLUMN_PAIRS.items():
        if sheet_key not in normalized_sheet:
            continue
        return any(pair.issubset(group) for group in groups)
    return False


def duplicate_column_warnings(workbook: dict[str, list[dict[str, Any]]]) -> list[str]:
    warnings: list[str] = []
    for sheet_name, rows in workbook.items():
        if not rows:
            continue

        headers = list(rows[0].keys())
        columns: dict[str, tuple[str, ...]] = {}
        for header in headers:
            values = tuple(str(row.get(header, "") or "").strip() for row in rows)
            if any(values):
                columns[header] = values

        for index, left in enumerate(headers):
            left_values = columns.get(left)
            if not left_values:
                continue
            for right in headers[index + 1 :]:
                right_values = columns.get(right)
                if not right_values or left_values != right_values:
                    continue
                if schema_duplicate_allowed(sheet_name, left, right):
                    continue
                warnings.append(
                    f"{sheet_name}: exact duplicate column contents in "
                    f"{left!r} and {right!r}; consolidate or make each field distinct"
                )
    return warnings


def custom_templates_in_scope(cv: dict[str, Any]) -> list[dict[str, Any]]:
    templates = {str(t.get("templateId")): t for t in cv.get("customTemplate", []) or []}
    used_ids = set()
    for layer in ("tag", "variable"):
        for obj in cv.get(layer, []) or []:
            template_id = custom_template_id(obj)
            if template_id:
                used_ids.add(str(template_id))
    return [templates[template_id] for template_id in sorted(used_ids) if template_id in templates]


def source_objects(cv: dict[str, Any]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    high_impact: list[dict[str, str]] = []
    custom_code: list[dict[str, str]] = []

    for tag in cv.get("tag", []) or []:
        if not active_tag(tag):
            continue
        row = {
            "layer": "tag",
            "id": object_id(tag, "tagId"),
            "name": object_name(tag),
            "type": str(tag.get("type") or ""),
        }
        if is_high_impact(tag):
            high_impact.append(row)
        if is_custom_html_tag(tag):
            custom_code.append(row)

    for variable in cv.get("variable", []) or []:
        row = {
            "layer": "variable",
            "id": object_id(variable, "variableId"),
            "name": object_name(variable),
            "type": str(variable.get("type") or ""),
        }
        if is_high_impact(variable):
            high_impact.append(row)
        if is_custom_js_variable(variable):
            custom_code.append(row)

    for template in custom_templates_in_scope(cv):
        custom_code.append(
            {
                "layer": "template",
                "id": object_id(template, "templateId"),
                "name": object_name(template),
                "type": "customTemplate",
            }
        )

    return high_impact, custom_code


def validate_semantic_sheet(name: str | None, rows: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    if not name:
        errors.append("missing Semantic Object Matrix sheet")
    elif rows:
        errors.extend(validate_semantic_depth_rows(rows, name))
        errors.extend(
            validate_summary_quality(
                rows,
                SEMANTIC_SUMMARY_FIELDS,
                name,
            )
        )
    return errors


def validate_reconciliation(
    name: str | None, rows: list[dict[str, Any]], limited: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    if not limited and not name:
        errors.append("missing Workstream Reconciliation sheet")
    elif name:
        rec_errors, rec_warnings = validate_rows(rows)
        errors.extend(f"{name}: {err}" for err in rec_errors)
        warnings.extend(f"{name}: {warn}" for warn in rec_warnings)
    return errors, warnings


def validate_high_impact_coverage(
    high_impact: list[dict[str, str]], semantic_rows: list[dict[str, Any]], limited: bool
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for obj in high_impact:
        if not semantic_row_complete(semantic_rows, obj["layer"], obj["id"], obj["name"]):
            message = (
                f"missing complete semantic row for high-impact {obj['layer']} "
                f"{obj['id']} {obj['name']!r}"
            )
            if limited:
                warnings.append(message)
            else:
                errors.append(message)
    return errors, warnings


def validate_custom_code_coverage(
    custom_code: list[dict[str, str]], custom_name: str | None, custom_rows: list[dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    if custom_code and not custom_name:
        errors.append(
            f"missing Custom Code Semantic Review sheet for {len(custom_code)} custom-code object(s)"
        )
        custom_rows = []

    for obj in custom_code:
        matching_rows = [
            row for row in custom_rows if row_matches(row, obj["layer"], obj["id"], obj["name"])
        ]
        if not matching_rows:
            errors.append(
                f"missing custom-code review row for {obj['layer']} {obj['id']} {obj['name']!r}"
            )
            continue
        if not any(export_review_done(row) for row in matching_rows):
            errors.append(
                f"custom-code row lacks completed export review for "
                f"{obj['layer']} {obj['id']} {obj['name']!r}"
            )

    if custom_rows:
        errors.extend(
            validate_summary_quality(
                custom_rows,
                CUSTOM_CODE_SUMMARY_FIELDS,
                custom_name or "Custom Code Semantic Review",
            )
        )
    return errors


def validate_package(export_path: Path, workbook_path: Path, limited: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    cv = container_version(json.loads(export_path.read_text(encoding="utf-8")))
    workbook = load_xlsx_workbook(workbook_path)
    high_impact, custom_code = source_objects(cv)

    semantic_name, semantic_rows = find_sheet(workbook, ["semantic", "matrix"])
    custom_name, custom_rows = find_sheet(workbook, ["custom", "code"])
    reconciliation_name, reconciliation_rows = find_sheet(workbook, ["reconciliation"])

    errors.extend(validate_semantic_sheet(semantic_name, semantic_rows))
    rec_errors, rec_warnings = validate_reconciliation(
        reconciliation_name, reconciliation_rows, limited
    )
    errors.extend(rec_errors)
    warnings.extend(rec_warnings)

    coverage_errors, coverage_warnings = validate_high_impact_coverage(
        high_impact, semantic_rows, limited
    )
    errors.extend(coverage_errors)
    warnings.extend(coverage_warnings)
    errors.extend(validate_custom_code_coverage(custom_code, custom_name, custom_rows))

    errors.extend(validate_placeholder_language(workbook))
    warnings.append(
        "source summary: "
        f"{len(high_impact)} high-impact active tag/variable object(s), "
        f"{len(custom_code)} custom-code/template object(s)"
    )
    warnings.extend(duplicate_column_warnings(workbook))
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Source GTM container export JSON")
    parser.add_argument("workbook", type=Path, help="Audit/cleanup workbook XLSX")
    parser.add_argument(
        "--limited",
        action="store_true",
        help="Treat high-impact coverage misses as warnings for explicitly limited audits.",
    )
    args = parser.parse_args()

    try:
        errors, warnings = validate_package(args.export, args.workbook, args.limited)
    except Exception as exc:  # noqa: BLE001 - command should report all load/parse failures.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Package gate: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1

    print(f"Package gate: PASS ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
