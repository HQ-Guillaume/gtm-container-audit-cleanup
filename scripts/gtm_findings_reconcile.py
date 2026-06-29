#!/usr/bin/env python3
"""Validate that deterministic baseline findings are reconciled."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any

from gtm_workbook import load_xlsx_workbook, normalize_header

ACCEPTED_RESOLUTIONS = {
    "cleanup_operation",
    "documented_exception",
    "runtime_blocker",
    "owner_decision_needed",
    "not_applicable",
}

RESOLUTION_ALIASES = {
    "cleanup": "cleanup_operation",
    "operation": "cleanup_operation",
    "cleanup operation": "cleanup_operation",
    "documented exception": "documented_exception",
    "exception": "documented_exception",
    "runtime blocker": "runtime_blocker",
    "blocker": "runtime_blocker",
    "owner decision": "owner_decision_needed",
    "owner decision needed": "owner_decision_needed",
    "decision needed": "owner_decision_needed",
    "not applicable": "not_applicable",
    "n/a": "not_applicable",
    "na": "not_applicable",
}

FINDING_ID_FIELDS = {
    "finding_id",
    "source_finding_id",
    "source_finding_ids",
    "baseline_finding_id",
    "baseline_finding_ids",
    "linked_finding_id",
    "linked_finding_ids",
}

RESOLUTION_FIELDS = {
    "resolution",
    "resolution_status",
    "finding_resolution",
    "status",
    "decision",
}

OPERATION_PACKET_REQUIRED_FIELDS = {
    "operation_id",
    "affected_objects",
    "object_identity",
    "source_lenses",
    "current_behavior",
    "problem",
    "why_it_matters",
    "expected_clean_state",
    "exact_proposed_action",
    "preconditions",
    "qa_steps",
    "rollback",
    "confidence",
    "blocker",
    "priority",
    "resolution_status",
    "source_finding_ids",
}

OPERATION_PACKET_NONBLANK_FIELDS = {
    "operation_id",
    "affected_objects",
    "object_identity",
    "source_lenses",
    "current_behavior",
    "problem",
    "why_it_matters",
    "expected_clean_state",
    "exact_proposed_action",
    "qa_steps",
    "rollback",
    "confidence",
    "priority",
    "resolution_status",
    "source_finding_ids",
}

TECHNICAL_PACKET_DETAIL_FIELDS = {
    "technical_exact_proposed_action",
    "technical_preconditions",
    "technical_qa_steps",
    "technical_rollback_note",
    "technical_handoff_packet",
}

TECHNICAL_PACKET_HANDOFF_FIELDS = {
    "technical_handoff_packet",
    "handoff_packet",
    "handoff_evidence",
}

SOURCE_ID_FIELDS = FINDING_ID_FIELDS | {
    "source_finding_id",
    "source_finding_ids",
    "semantic_finding_id",
    "semantic_finding_ids",
    "technical_finding_id",
    "technical_finding_ids",
    "deterministic_finding_id",
    "deterministic_finding_ids",
}

VAGUE_ACTION_PATTERNS = [
    re.compile(r"^\s*(?:review|check|validate|investigate)\b", re.I),
    re.compile(r"^\s*(?:simplify|consolidate|harden|fix)\s*(?:custom\s+code|code|logic|where\s+possible)?\s*$", re.I),
    re.compile(r"\breview\s+custom\s+code\b", re.I),
    re.compile(r"\bvalidate\s+trigger\s+logic\b", re.I),
    re.compile(r"\bcheck\s+(?:the\s+)?variables?\b", re.I),
]


def normalize_resolution(value: Any) -> str:
    text = re.sub(r"[^a-z0-9]+", " ", str(value or "").strip().lower()).strip()
    if text in RESOLUTION_ALIASES:
        return RESOLUTION_ALIASES[text]
    return text.replace(" ", "_")


def split_ids(value: Any) -> list[str]:
    return [
        part.strip()
        for part in re.split(r"[;,\n]+", str(value or ""))
        if part.strip()
    ]


def load_resolution_rows(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        if isinstance(data, dict):
            if isinstance(data.get("rows"), list):
                data = data["rows"]
            elif isinstance(data.get("findings"), list):
                data = data["findings"]
        if not isinstance(data, list):
            raise ValueError("resolution JSON must be a row list or contain rows/findings")
        return [{normalize_header(k): v for k, v in row.items()} for row in data]

    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return [
                {normalize_header(k): v for k, v in row.items()}
                for row in csv.DictReader(handle)
            ]

    if suffix == ".xlsx":
        rows = []
        workbook = load_xlsx_workbook(path)
        for sheet_name, sheet_rows in workbook.items():
            normalized_sheet = re.sub(r"[^a-z0-9]+", " ", sheet_name.lower()).strip()
            if "baseline" in normalized_sheet and "finding" in normalized_sheet:
                continue
            for row in sheet_rows:
                normalized = {normalize_header(k): v for k, v in row.items()}
                normalized["_sheet"] = sheet_name
                rows.append(normalized)
        return rows

    raise ValueError("resolution input must be .json, .csv, or .xlsx")


def baseline_findings(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    findings = data.get("findings")
    if not isinstance(findings, list):
        raise ValueError("baseline JSON must contain a findings list")
    return [
        finding
        for finding in findings
        if finding.get("finding_type") != "zero_findings"
    ]


def row_finding_ids(row: dict[str, Any]) -> list[str]:
    ids = []
    for field in FINDING_ID_FIELDS:
        if field in row:
            ids.extend(split_ids(row.get(field)))
    return ids


def row_source_ids(row: dict[str, Any]) -> list[str]:
    ids = []
    for field in SOURCE_ID_FIELDS:
        if field in row:
            ids.extend(split_ids(row.get(field)))
    return ids


def row_resolution(row: dict[str, Any]) -> str:
    for field in RESOLUTION_FIELDS:
        if field in row and str(row.get(field) or "").strip():
            return normalize_resolution(row.get(field))
    return ""


def validate(baseline_path: Path, resolution_path: Path) -> tuple[list[str], list[str]]:
    findings = baseline_findings(baseline_path)
    expected_ids = {str(finding["finding_id"]) for finding in findings}
    rows = load_resolution_rows(resolution_path)
    resolved: dict[str, str] = {}
    warnings: list[str] = []
    errors: list[str] = []

    for index, row in enumerate(rows, start=2):
        ids = row_finding_ids(row)
        if not ids:
            continue
        resolution = row_resolution(row)
        if not resolution:
            errors.append(
                f"row {index}: finding ID(s) {', '.join(ids)} lack a resolution/status field"
            )
            continue
        if resolution not in ACCEPTED_RESOLUTIONS:
            errors.append(
                f"row {index}: resolution {resolution!r} is not one of "
                f"{', '.join(sorted(ACCEPTED_RESOLUTIONS))}"
            )
            continue
        for finding_id in ids:
            if finding_id not in expected_ids:
                warnings.append(f"row {index}: unknown finding_id {finding_id}")
                continue
            resolved[finding_id] = resolution

    missing = sorted(expected_ids - set(resolved))
    for finding_id in missing:
        finding = next(item for item in findings if item["finding_id"] == finding_id)
        errors.append(
            f"{finding_id}: unreconciled {finding.get('finding_type')} "
            f"for {finding.get('object_type')} {finding.get('object_names')}"
        )
    return errors, warnings


def source_rows_from_artifact(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(data, dict):
        for key in ("rows", "findings"):
            if isinstance(data.get(key), list):
                data = data[key]
                break
    if not isinstance(data, list):
        raise ValueError(f"{path} must contain rows or findings")
    return [{normalize_header(k): v for k, v in row.items()} for row in data]


def required_source_ids_from_rows(
    rows: list[dict[str, Any]], id_fields: tuple[str, ...], action_fields: tuple[str, ...]
) -> set[str]:
    required: set[str] = set()
    for row in rows:
        packet_required = str(row.get("operation_packet_required", "")).strip().lower()
        action_text = " ".join(str(row.get(field, "")) for field in action_fields).lower()
        if packet_required in {"false", "0", "no", "n"} or action_text == "keep":
            continue
        if "keep" in action_text and not any(
            token in action_text
            for token in ("fix", "delete", "consolidate", "harden", "rebuild", "block")
        ):
            continue
        for field in id_fields:
            for item in split_ids(row.get(field)):
                required.add(item)
    return required


def any_nonblank(row: dict[str, Any], fields: set[str]) -> bool:
    return any(str(row.get(field) or "").strip() for field in fields)


def validate_operation_packets(
    baseline_path: Path,
    packet_path: Path,
    semantic_path: Path | None = None,
    technical_path: Path | None = None,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    rows = load_resolution_rows(packet_path)
    if not rows:
        return ["operation packets: no rows found"], warnings

    expected_ids = {str(finding["finding_id"]) for finding in baseline_findings(baseline_path)}
    if semantic_path:
        semantic_rows = source_rows_from_artifact(semantic_path)
        expected_ids.update(
            required_source_ids_from_rows(
                semantic_rows,
                ("semantic_finding_id",),
                ("semantic_action_candidate", "semantic_cleanup_implication"),
            )
        )
    if technical_path:
        technical_rows = source_rows_from_artifact(technical_path)
        for index, row in enumerate(technical_rows, start=2):
            action_text = str(row.get("technical_action_candidate") or "").strip().lower()
            packet_required = str(row.get("operation_packet_required", "")).strip().lower()
            if action_text != "keep" and packet_required not in {"false", "0", "no", "n"}:
                blank = sorted(
                    field
                    for field in TECHNICAL_PACKET_DETAIL_FIELDS
                    if not str(row.get(field) or "").strip()
                )
                if blank:
                    errors.append(
                        f"technical source row {index}: missing technical packet detail "
                        f"field(s): {', '.join(blank)}"
                    )
        expected_ids.update(
            required_source_ids_from_rows(
                technical_rows,
                ("technical_finding_id",),
                ("technical_action_candidate", "technical_cleanup_implication"),
            )
        )

    resolved_ids: set[str] = set()
    operation_ids: set[str] = set()
    technical_expected_ids = {
        str(row.get("technical_finding_id") or "").strip()
        for row in source_rows_from_artifact(technical_path)
    } if technical_path else set()
    technical_expected_ids.discard("")
    for index, row in enumerate(rows, start=2):
        missing = sorted(field for field in OPERATION_PACKET_REQUIRED_FIELDS if field not in row)
        if missing:
            errors.append(
                f"operation packet row {index}: missing required fields: {', '.join(missing)}"
            )
            continue

        blank = [
            field
            for field in sorted(OPERATION_PACKET_NONBLANK_FIELDS)
            if not str(row.get(field) or "").strip()
        ]
        if blank:
            errors.append(f"operation packet row {index}: blank fields: {', '.join(blank)}")

        operation_id = str(row.get("operation_id") or "").strip()
        if operation_id:
            if operation_id in operation_ids:
                errors.append(f"operation packet row {index}: duplicate operation_id {operation_id}")
            operation_ids.add(operation_id)

        resolution = normalize_resolution(row.get("resolution_status"))
        if resolution not in ACCEPTED_RESOLUTIONS:
            errors.append(
                f"operation packet row {index}: resolution_status {resolution!r} is not one of "
                f"{', '.join(sorted(ACCEPTED_RESOLUTIONS))}"
            )
        if resolution in {"runtime_blocker", "owner_decision_needed"} and not str(
            row.get("blocker") or ""
        ).strip():
            errors.append(
                f"operation packet row {index}: blocker is required for {resolution}"
            )

        action_text = str(row.get("exact_proposed_action") or "")
        for pattern in VAGUE_ACTION_PATTERNS:
            if pattern.search(action_text):
                errors.append(
                    f"operation packet row {index}: exact_proposed_action is vague: "
                    f"{action_text!r}"
                )
                break

        source_ids = set(row_source_ids(row))
        if not source_ids:
            errors.append(f"operation packet row {index}: no source_finding_ids")
        resolved_ids.update(source_ids)

        if source_ids.intersection(technical_expected_ids):
            if "technical" not in str(row.get("source_lenses") or "").lower():
                errors.append(
                    f"operation packet row {index}: technical source finding is linked "
                    "but source_lenses does not include technical"
                )
            if not any_nonblank(row, TECHNICAL_PACKET_HANDOFF_FIELDS):
                errors.append(
                    f"operation packet row {index}: technical source finding requires "
                    "technical_handoff_packet, handoff_packet, or handoff_evidence"
                )

        source_lenses = str(row.get("source_lenses") or "").lower()
        if "deterministic" not in source_lenses and "semantic" not in source_lenses and "technical" not in source_lenses:
            errors.append(
                f"operation packet row {index}: source_lenses must name at least one cleanup lens"
            )

    missing_source_ids = sorted(expected_ids - resolved_ids)
    for source_id in missing_source_ids:
        errors.append(f"operation packets: source finding {source_id} is not reconciled")

    unknown_source_ids = sorted(resolved_ids - expected_ids)
    for source_id in unknown_source_ids:
        warnings.append(f"operation packets: source finding {source_id} was not found in supplied scan artifacts")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path, help="deterministic baseline JSON")
    parser.add_argument(
        "resolution",
        type=Path,
        help="CSV, JSON, or XLSX rows containing source finding IDs and resolution status",
    )
    parser.add_argument(
        "--operation-packets",
        action="store_true",
        help="Validate reconciled operation packets instead of simple baseline resolutions.",
    )
    parser.add_argument(
        "--semantic",
        type=Path,
        help="Optional semantic_findings.json to require semantic source rows in packet reconciliation.",
    )
    parser.add_argument(
        "--technical",
        type=Path,
        help="Optional technical_code_findings.json to require technical code rows in packet reconciliation.",
    )
    args = parser.parse_args()

    try:
        if args.operation_packets:
            errors, warnings = validate_operation_packets(
                args.baseline, args.resolution, args.semantic, args.technical
            )
        else:
            errors, warnings = validate(args.baseline, args.resolution)
    except Exception as exc:  # noqa: BLE001 - CLI should report load/parse errors.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Finding reconciliation: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1

    print(f"Finding reconciliation: PASS ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
