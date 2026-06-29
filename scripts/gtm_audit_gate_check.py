#!/usr/bin/env python3
"""Validate GTM audit completion-gate reconciliation rows.

Input may be:
- CSV exported from the Workstream Reconciliation tab.
- JSON list of row objects, or {"rows": [...]}.
- XLSX workbook with a sheet named "18b Workstream Reconciliation" or any
  sheet whose name contains "Reconciliation".

Use --strict-evidence with XLSX workbooks that claim full audit or cleanup-plan
completion. Strict mode also checks Semantic Object Matrix and Custom Code
Semantic Review evidence and rejects cleanup-operation placeholders that defer
audit work into execution.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from xml.etree import ElementTree

from gtm_workbook import (
    column_index,
    find_sheet,
    load_xlsx_workbook,
    normalize_header,
    normalize_sheet_name,
    workbook_target_path,
    xml_text,
)

COUNT_FIELDS = [
    "total_source_count",
    "inventoried_count",
    "dependency_mapped_count",
    "measurement_diagnosed_count",
    "semantically_validated_count",
    "cleanup_decision_count",
    "deferred_count",
    "not_applicable_count",
    "user_excluded_count",
    "unresolved_count",
]

REQUIRED_FIELDS = ["workstream", "object_family"] + COUNT_FIELDS

SEMANTIC_MATRIX_REQUIRED_FIELDS = [
    "object_id",
    "object_name",
    "layer",
    "vendor_or_family",
    "inferred_business_role",
    "decision_outcome",
    "conversion_hierarchy",
    "platform_role",
    "expected_data_contract",
    "depth_required",
    "depth_completed",
    "trigger_context_status",
    "configuration_logic_status",
    "source_or_code_logic_status",
    "consent_or_server_status",
    "evidence_level",
    "semantic_status",
    "confidence",
    "runtime_qa_required",
    "blocker_or_next_evidence",
]

CUSTOM_CODE_REQUIRED_FIELDS = [
    "layer",
    "object_id",
    "object_name",
    "type",
    "role_category",
    "purpose",
    "export_review_completed",
    "trigger_or_consumer_context",
    "consent_assumption",
    "external_urls_storage_cookie_dom_datalayer_side_effects",
    "variable_references",
    "expected_output_or_side_effect",
    "runtime_risks",
    "semantic_status",
    "cleanup_recommendation",
    "qa_method",
    "blocker",
]

OPERATION_PACKET_REQUIRED_FIELDS = [
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
]

OPERATION_PACKET_NONBLANK_FIELDS = [
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
]

TECHNICAL_PACKET_HANDOFF_FIELDS = [
    "technical_handoff_packet",
    "handoff_packet",
    "handoff_evidence",
]

BASELINE_REQUIRED_FIELDS = [
    "module_name",
    "module_status",
    "objects_scanned",
    "finding_id",
    "finding_type",
    "object_type",
    "object_ids",
    "object_names",
    "signature_key",
    "deterministic_evidence",
    "default_action",
    "required_resolution",
]

PROTECTED_BASELINE_MODULES = {
    "inventory",
    "recognized_system_references",
    "missing_references",
    "duplicate_tag_names",
    "duplicate_trigger_names",
    "duplicate_variable_names",
    "duplicate_folder_names",
    "duplicate_tag_configurations",
    "normalized_duplicate_tag_signatures",
    "duplicate_trigger_logic",
    "duplicate_variable_logic",
    "duplicate_variable_paths",
    "outdated_ua_styled_setup_objects",
    "unused_variables",
    "unused_triggers",
    "tags_without_firing_triggers",
    "unused_custom_templates",
    "unused_folders",
    "single_member_trigger_groups",
    "duplicate_custom_code",
    "name_hygiene",
    "naming_architecture_standardization",
}

D3_REQUIRED_FIELDS = [
    "d3_inputs_or_sources",
    "d3_logic_summary",
    "d3_output_or_side_effect",
    "d3_consumer_expectation",
    "d3_correctness_decision",
]

COMPACT_D3_FIELDS = [
    "literal_behavior",
    "consumer_context",
    "analyst_judgment",
    "cleanup_implication",
    "evidence_or_qa_blocker",
]

SEMANTIC_SUMMARY_FIELDS = [
    "configuration_logic_status",
    "source_or_code_logic_status",
    "d3_logic_summary",
    "d3_output_or_side_effect",
    "d3_correctness_decision",
    "literal_behavior",
    "consumer_context",
    "analyst_judgment",
    "cleanup_implication",
    "evidence_or_qa_blocker",
]

CUSTOM_CODE_SUMMARY_FIELDS = [
    "purpose",
    "external_urls_storage_cookie_dom_datalayer_side_effects",
    "expected_output_or_side_effect",
    "runtime_risks",
    "cleanup_recommendation",
]

CLEANUP_PLAN_TAXONOMY_FIELDS = [
    "area_problem_type",
    "area",
    "problem_type",
]

CLEANUP_PLAN_PROBLEM_FIELDS = [
    "problem_evidence",
    "issue_evidence",
    "issue_or_evidence",
    "problem",
]

CLEANUP_PLAN_ACTION_FIELDS = [
    "action_priority_qa",
    "recommended_action",
    "action_qa_status",
    "qa_status",
]

PLACEHOLDER_PATTERNS = [
    re.compile(r"\bperform\s+line[- ]level(?:\s+custom[- ]code)?\s+review\b", re.I),
    re.compile(r"\breview\s+custom\s+code\b", re.I),
    re.compile(r"\bcheck\s+(?:the\s+)?variables?\b", re.I),
    re.compile(r"\bvalidate\s+trigger\s+logic\b", re.I),
]

VAGUE_ACTION_PATTERNS = [
    re.compile(r"^\s*(?:review|check|validate|investigate)\b", re.I),
    re.compile(r"^\s*(?:simplify|consolidate|harden|fix)\s*(?:custom\s+code|code|logic|where\s+possible)?\s*$", re.I),
    re.compile(r"\bsimplify\s+custom\s+code\b", re.I),
    re.compile(r"\bconsolidate\s+where\s+possible\b", re.I),
    re.compile(r"\bharden\s+risky\s+code\b", re.I),
]

INCOMPLETE_DEPTH_PATTERNS = [
    re.compile(r"\bd3\s*/\s*d4\s+blocked\b", re.I),
    re.compile(r"\bd3\s+(?:required|needed)\b", re.I),
    re.compile(r"\bstatic\s+scan\s+only\b", re.I),
    re.compile(r"\b(?:full\s+)?code\s+walkthrough\s+(?:required|needed)\b", re.I),
    re.compile(r"\breview\s+later\b", re.I),
]

GENERIC_SUMMARY_PATTERNS = [
    re.compile(r"\bcustom\s+code\s+inspected\b", re.I),
    re.compile(r"\bconfiguration\s+reviewed\b", re.I),
    re.compile(r"\bcode\s+scanned\b", re.I),
    re.compile(r"\bexternal\s+url\s+found\b", re.I),
    re.compile(r"\bno\s+external\s+urls?\s+detected\b", re.I),
    re.compile(r"\bdatalayer\s+push\s+detected\b", re.I),
    re.compile(r"\bno\s+obvious\s+browser\s+side\s+effect\b", re.I),
    re.compile(r"\bno\s+issue\s+found\b", re.I),
    re.compile(r"\bsee\s+(?:the\s+)?config\b", re.I),
    re.compile(r"\bsee\s+(?:the\s+)?export\b", re.I),
    re.compile(r"\bstatic\s+scan\s+completed\b", re.I),
    re.compile(r"\breviewed\s+manually\b", re.I),
    re.compile(r"\breturns?\s+(?:a\s+)?computed\s+values?\b", re.I),
    re.compile(r"\bcomputed\s+scalar\s*/\s*object\b", re.I),
    re.compile(r"\bbrowser\s+side\s+effects?\b", re.I),
    re.compile(r"\bpayload\s+transformer\b", re.I),
    re.compile(r"\bvendor\s+loader\b", re.I),
    re.compile(r"\baccording\s+to\s+(?:its\s+)?configured\s+type\b", re.I),
    re.compile(r"\bobject\s+configuration,\s*GTM\s+event,\s*browser,\s*DOM,\s*storage,\s*or\s*template\s+fields\b", re.I),
    re.compile(r"\bloads,\s*writes,\s*pushes,\s*or\s*mutates\s+browser\s+state\b", re.I),
    re.compile(r"\btags\s+and\s+downstream\s+reports\s+need\s+event\s+context\b", re.I),
    re.compile(r"^\s*semantic\s+(?:issue|problem)\s*$", re.I),
    re.compile(r"^\s*media\s+(?:issue|problem)\s*$", re.I),
    re.compile(r"^\s*configuration\s+(?:issue|problem)\s*$", re.I),
    re.compile(r"^\s*tracking\s+(?:issue|problem)\s*$", re.I),
    re.compile(r"^\s*tag\s+(?:issue|problem)\s*$", re.I),
    re.compile(r"^\s*trigger\s+(?:issue|problem)\s*$", re.I),
    re.compile(r"^\s*variable\s+(?:issue|problem)\s*$", re.I),
    re.compile(r"^\s*custom[- ]code\s+(?:issue|problem)\s*$", re.I),
]

GENERIC_D3_VALUES = {
    "",
    "n/a",
    "na",
    "not applicable",
    "see export",
    "see config",
    "static scan",
    "static scan completed",
    "runtime required",
    "runtime qa required",
    "more info needed",
    "blocked",
    "pending",
}

SOURCE_SIGNAL_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in (
        r"\breads?\b",
        r"\buses?\b",
        r"\bsource\b",
        r"\bfrom\b",
        r"\bdatalayer\b",
        r"\bdl[v ]?\b",
        r"\{\{",
        r"\bcookies?\b",
        r"\bstorage\b",
        r"\burl\b",
        r"\bdom\b",
        r"\bcmp\b",
        r"\btemplate\b",
        r"\bfields?\b",
        r"\bparameters?\b",
        r"\btriggers?\b",
        r"\bevents?\b",
    )
]

LOGIC_ACTION_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in (
        r"\breads?\b",
        r"\bmaps?\b",
        r"\breturns?\b",
        r"\bbuilds?\b",
        r"\blistens?\b",
        r"\bpush(?:es)?\b",
        r"\bloads?\b",
        r"\bsets?\b",
        r"\bextracts?\b",
        r"\bjoins?\b",
        r"\bcalculat(?:es|ing)\b",
        r"\bforwards?\b",
        r"\bsends?\b",
        r"\btriggers?\b",
        r"\bfilters?\b",
        r"\bmatches?\b",
        r"\bchecks?\b",
        r"\bcalls?\b",
        r"\bwrites?\b",
        r"\bnormaliz(?:es|ing)\b",
        r"\bparses?\b",
        r"\bstores?\b",
        r"\bupdates?\b",
        r"\bblocks?\b",
        r"\bfires?\b",
        r"\bevaluates?\b",
    )
]

OUTPUT_SIGNAL_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in (
        r"\breturns?\b",
        r"\boutputs?\b",
        r"\bproduces?\b",
        r"\bpush(?:es)?\b",
        r"\bloads?\b",
        r"\bsends?\b",
        r"\bfires?\b",
        r"\bblocks?\b",
        r"\bsets?\b",
        r"\bwrites?\b",
        r"\bmutates?\b",
        r"\bside[- ]effects?\b",
        r"\bpayload\b",
        r"\bevents?\b",
        r"\bvalues?\b",
        r"\barrays?\b",
        r"\bobjects?\b",
        r"\bbooleans?\b",
        r"\bstrings?\b",
        r"\bnumbers?\b",
        r"\bcookies?\b",
        r"\bstorage\b",
        r"\bdatalayer\b",
        r"\brequests?\b",
        r"\bnetwork\b",
    )
]

CONSUMER_SIGNAL_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in (
        r"\bconsumed\s+by\b",
        r"\bused\s+by\b",
        r"\bexpected\s+by\b",
        r"\bfeeds?\b",
        r"\bconsumers?\b",
        r"\bdestinations?\b",
        r"\btags?\b",
        r"\btriggers?\b",
        r"\bvariables?\b",
        r"\bvendors?\b",
        r"\bplatforms?\b",
        r"\bga4\b",
        r"\bgoogle\b",
        r"\bpiano\b",
        r"\bmeta\b",
        r"\bpixels?\b",
        r"\bconsent\b",
        r"\bservers?\b",
    )
]

DECISION_SIGNAL_PATTERNS = [
    re.compile(pattern, re.I)
    for pattern in (
        r"\bcoherent\b",
        r"\bissues?\b",
        r"\blikely\s+issue\b",
        r"\bmismatch\b",
        r"\bcorrect\b",
        r"\bincorrect\b",
        r"\bfix\b",
        r"\bkeep\b",
        r"\bconsolidate\b",
        r"\bdelete\s+candidate\b",
        r"\bruntime\s+qa\b",
        r"\bowner\b",
        r"\bblockers?\b",
        r"\bdeferred\b",
        r"\bneeds?\b",
        r"\bsafe\b",
        r"\brisky\b",
        r"\bunclear\b",
        r"\bfunctional\b",
        r"\bnot\s+functional\b",
    )
]


def to_int(row: Dict[str, Any], field: str) -> Tuple[int, str | None]:
    raw = row.get(field, "")
    if raw is None or raw == "":
        return 0, f"missing count '{field}'"
    try:
        return int(float(str(raw).strip())), None
    except ValueError:
        return 0, f"invalid count '{field}'={raw!r}"


def load_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for raw in reader:
            rows.append({normalize_header(k): v for k, v in raw.items()})
        return rows


def load_json(path: Path) -> List[Dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        data = data["rows"]
    if not isinstance(data, list):
        raise ValueError("JSON input must be a list of rows or {'rows': [...]}")
    return [{normalize_header(k): v for k, v in row.items()} for row in data]


def load_xlsx_stdlib(path: Path) -> List[Dict[str, Any]]:
    ns = {
        "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
        "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "pkgrel": "http://schemas.openxmlformats.org/package/2006/relationships",
    }

    with zipfile.ZipFile(path) as archive:
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))

        rel_targets = {
            rel.attrib["Id"]: rel.attrib["Target"]
            for rel in rels.findall("pkgrel:Relationship", ns)
        }

        sheet_target = None
        for sheet in workbook.findall("main:sheets/main:sheet", ns):
            name = sheet.attrib.get("name", "")
            rel_id = sheet.attrib.get(f"{{{ns['rel']}}}id")
            if name == "18b Workstream Reconciliation" or "reconciliation" in name.lower():
                target = rel_targets.get(rel_id or "")
                if not target:
                    continue
                sheet_target = workbook_target_path(target)
                break
        if not sheet_target:
            raise ValueError("No reconciliation sheet found")

        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall("main:si", ns):
                shared_strings.append(xml_text(item))

        sheet_root = ElementTree.fromstring(archive.read(sheet_target))
        parsed_rows: List[List[str]] = []
        for row in sheet_root.findall("main:sheetData/main:row", ns):
            values: List[str] = []
            for cell in row.findall("main:c", ns):
                ref = cell.attrib.get("r", "")
                index = column_index(ref) if ref else len(values)
                while len(values) <= index:
                    values.append("")
                cell_type = cell.attrib.get("t", "")
                if cell_type == "s":
                    raw = xml_text(cell.find("main:v", ns))
                    values[index] = shared_strings[int(raw)] if raw else ""
                elif cell_type == "inlineStr":
                    values[index] = xml_text(cell.find("main:is", ns))
                else:
                    values[index] = xml_text(cell.find("main:v", ns))
            if any(value != "" for value in values):
                parsed_rows.append(values)

    if not parsed_rows:
        return []
    headers = [normalize_header(value) for value in parsed_rows[0]]
    rows = []
    for values in parsed_rows[1:]:
        rows.append({headers[i]: values[i] for i in range(min(len(headers), len(values)))})
    return rows


def load_xlsx_openpyxl(path: Path) -> List[Dict[str, Any]]:
    try:
        import openpyxl  # type: ignore
    except ImportError as exc:
        raise RuntimeError("openpyxl is unavailable") from exc

    workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sheet_name = None
    if "18b Workstream Reconciliation" in workbook.sheetnames:
        sheet_name = "18b Workstream Reconciliation"
    else:
        for candidate in workbook.sheetnames:
            if "reconciliation" in candidate.lower():
                sheet_name = candidate
                break
    if not sheet_name:
        raise ValueError("No reconciliation sheet found")

    sheet = workbook[sheet_name]
    rows_iter = sheet.iter_rows(values_only=True)
    headers = [normalize_header(v) for v in next(rows_iter, [])]
    rows = []
    for values in rows_iter:
        if not values or all(v in (None, "") for v in values):
            continue
        rows.append({headers[i]: values[i] for i in range(min(len(headers), len(values)))})
    return rows


def load_xlsx(path: Path) -> List[Dict[str, Any]]:
    try:
        return load_xlsx_openpyxl(path)
    except Exception as first_exc:  # noqa: BLE001 - fallback should cover missing optional deps.
        try:
            return load_xlsx_stdlib(path)
        except Exception as second_exc:  # noqa: BLE001 - preserve both failure reasons.
            raise RuntimeError(
                f"Unable to read XLSX with openpyxl or stdlib fallback. "
                f"openpyxl error: {first_exc}; fallback error: {second_exc}"
            ) from second_exc


def load_rows(path: Path) -> List[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_csv(path)
    if suffix == ".json":
        return load_json(path)
    if suffix == ".xlsx":
        return load_xlsx(path)
    raise ValueError("Unsupported file type. Use .csv, .json, or .xlsx")


def validate_rows(rows: Iterable[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    row_list = list(rows)
    if not row_list:
        return ["no reconciliation rows found"], warnings

    for index, row in enumerate(row_list, start=2):
        label = f"row {index}"
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            errors.append(f"{label}: missing required fields: {', '.join(missing)}")
            continue

        counts: Dict[str, int] = {}
        for field in COUNT_FIELDS:
            value, problem = to_int(row, field)
            counts[field] = value
            if problem:
                errors.append(f"{label}: {problem}")

        semantic_total = (
            counts["semantically_validated_count"]
            + counts["deferred_count"]
            + counts["not_applicable_count"]
            + counts["user_excluded_count"]
        )
        if counts["total_source_count"] != semantic_total:
            errors.append(
                f"{label}: semantic coverage mismatch: total_source_count="
                f"{counts['total_source_count']} but semantically_validated + deferred "
                f"+ not_applicable + user_excluded = {semantic_total}"
            )
        if counts["unresolved_count"] != 0:
            errors.append(f"{label}: unresolved_count is {counts['unresolved_count']}")
        if counts["inventoried_count"] < counts["total_source_count"]:
            warnings.append(f"{label}: inventoried_count is below total_source_count")
        if counts["dependency_mapped_count"] < counts["semantically_validated_count"]:
            warnings.append(f"{label}: dependency_mapped_count is below semantically_validated_count")
        if counts["measurement_diagnosed_count"] < counts["semantically_validated_count"]:
            errors.append(
                f"{label}: measurement_diagnosed_count is below semantically_validated_count"
            )
        if counts["cleanup_decision_count"] < counts["semantically_validated_count"]:
            warnings.append(f"{label}: cleanup_decision_count is below semantically_validated_count")

    return errors, warnings


def field_is_blank(value: Any) -> bool:
    return value is None or str(value).strip() == ""


def validate_required_table(
    rows: List[Dict[str, Any]], required_fields: List[str], label: str
) -> List[str]:
    errors: List[str] = []
    if not rows:
        return [f"{label}: no data rows found"]

    available = set(rows[0])
    missing = [field for field in required_fields if field not in available]
    if missing:
        errors.append(f"{label}: missing required fields: {', '.join(missing)}")
        return errors

    key_fields = [
        field
        for field in ("object_id", "object_name", "layer", "semantic_status")
        if field in required_fields
    ]
    key_fields.extend(
        field
        for field in (
            "inferred_business_role",
            "decision_outcome",
            "conversion_hierarchy",
            "platform_role",
            "expected_data_contract",
        )
        if field in required_fields
    )
    for index, row in enumerate(rows, start=2):
        for field in key_fields:
            if field_is_blank(row.get(field)):
                errors.append(f"{label} row {index}: blank {field}")
    return errors


def depth_tokens(value: Any) -> set[str]:
    return {match.group(0).upper() for match in re.finditer(r"\bD[1-4]\b", str(value or ""), re.I)}


def generic_or_blank(value: Any) -> bool:
    text = str(value or "").strip().lower()
    return text in GENERIC_D3_VALUES


def compact_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def has_signal(value: Any, patterns: List[re.Pattern[str]]) -> bool:
    text = str(value or "")
    return any(pattern.search(text) for pattern in patterns)


def word_count(value: Any) -> int:
    return len(re.findall(r"\b[\w{}.-]+\b", str(value or "")))


def d3_proof_errors(row: Dict[str, Any], label: str, index: int) -> List[str]:
    errors: List[str] = []
    available = set(row)
    if any(field in available for field in COMPACT_D3_FIELDS):
        missing = [field for field in COMPACT_D3_FIELDS if field not in available]
        if missing:
            return [
                f"{label} row {index}: compact D3 proof is missing columns: "
                f"{', '.join(missing)}"
            ]
        return compact_d3_proof_errors(row, label, index)

    field_values = {field: str(row.get(field) or "").strip() for field in D3_REQUIRED_FIELDS}

    for field, text in field_values.items():
        if generic_or_blank(text):
            errors.append(f"{label} row {index}: D3 field {field} is blank or generic")
        elif word_count(text) < 5:
            errors.append(
                f"{label} row {index}: D3 field {field} is too short to prove "
                "source, logic, output, consumer expectation, or judgment"
            )

    normalized_to_fields: Dict[str, List[str]] = {}
    for field, text in field_values.items():
        normalized = compact_text(text)
        if normalized:
            normalized_to_fields.setdefault(normalized, []).append(field)
    for fields in normalized_to_fields.values():
        if len(fields) > 1:
            errors.append(
                f"{label} row {index}: D3 fields repeat the same content: "
                f"{', '.join(fields)}"
            )

    signal_checks = [
        ("d3_inputs_or_sources", SOURCE_SIGNAL_PATTERNS, "a concrete source/input"),
        ("d3_logic_summary", LOGIC_ACTION_PATTERNS, "a logic/action verb"),
        ("d3_output_or_side_effect", OUTPUT_SIGNAL_PATTERNS, "an output or side-effect signal"),
        ("d3_consumer_expectation", CONSUMER_SIGNAL_PATTERNS, "a consumer/destination signal"),
        ("d3_correctness_decision", DECISION_SIGNAL_PATTERNS, "a correctness judgment"),
    ]
    for field, patterns, requirement in signal_checks:
        if field in field_values and not has_signal(field_values[field], patterns):
            errors.append(f"{label} row {index}: D3 field {field} lacks {requirement}")
    return errors


def d3_proof_complete(row: Dict[str, Any]) -> bool:
    return not d3_proof_errors(row, "semantic row", 0)


def compact_d3_proof_errors(row: Dict[str, Any], label: str, index: int) -> List[str]:
    errors: List[str] = []
    values = {field: str(row.get(field) or "").strip() for field in COMPACT_D3_FIELDS}
    for field, text in values.items():
        if generic_or_blank(text):
            errors.append(f"{label} row {index}: compact D3 field {field} is blank or generic")
        elif word_count(text) < 5:
            errors.append(
                f"{label} row {index}: compact D3 field {field} is too short to prove "
                "literal behavior, consumer context, judgment, or cleanup implication"
            )
        for pattern in GENERIC_SUMMARY_PATTERNS:
            if pattern.search(text):
                errors.append(
                    f"{label} row {index} field {field}: generic or fake-precision "
                    f"phrase {pattern.pattern!r}"
                )

    normalized_to_fields: Dict[str, List[str]] = {}
    for field, text in values.items():
        normalized = compact_text(text)
        if normalized:
            normalized_to_fields.setdefault(normalized, []).append(field)
    for fields in normalized_to_fields.values():
        if len(fields) > 1:
            errors.append(
                f"{label} row {index}: compact D3 fields repeat the same content: "
                f"{', '.join(fields)}"
            )

    checks = [
        ("literal_behavior", LOGIC_ACTION_PATTERNS, "literal object behavior"),
        ("consumer_context", CONSUMER_SIGNAL_PATTERNS, "actual consumer/context"),
        ("analyst_judgment", DECISION_SIGNAL_PATTERNS, "analyst judgment"),
        ("cleanup_implication", DECISION_SIGNAL_PATTERNS + LOGIC_ACTION_PATTERNS, "cleanup implication"),
        ("evidence_or_qa_blocker", SOURCE_SIGNAL_PATTERNS + DECISION_SIGNAL_PATTERNS, "evidence or QA blocker"),
    ]
    for field, patterns, requirement in checks:
        if not has_signal(values[field], patterns):
            errors.append(f"{label} row {index}: compact D3 field {field} lacks {requirement}")
    return errors


def validate_semantic_depth_rows(rows: List[Dict[str, Any]], label: str) -> List[str]:
    errors: List[str] = []
    available = set(rows[0]) if rows else set()
    missing_d3_columns = [field for field in D3_REQUIRED_FIELDS if field not in available]
    missing_compact_d3_columns = [field for field in COMPACT_D3_FIELDS if field not in available]

    for index, row in enumerate(rows, start=2):
        required = depth_tokens(row.get("depth_required"))
        completed = depth_tokens(row.get("depth_completed"))
        missing_depths = sorted(required.intersection({"D1", "D2", "D3"}) - completed)
        if missing_depths:
            errors.append(
                f"{label} row {index}: depth_required includes "
                f"{', '.join(missing_depths)} but depth_completed does not"
            )

        depth_completed_text = str(row.get("depth_completed") or "")
        source_logic_text = str(row.get("source_or_code_logic_status") or "")
        for pattern in INCOMPLETE_DEPTH_PATTERNS:
            if pattern.search(depth_completed_text) or pattern.search(source_logic_text):
                errors.append(
                    f"{label} row {index}: incomplete-depth wording found: {pattern.pattern!r}"
                )

        if "D3" in required:
            if missing_d3_columns and missing_compact_d3_columns:
                errors.append(
                    f"{label} row {index}: D3 required but matrix is missing both "
                    "legacy and compact D3 proof columns"
                )
                continue
            if "D3" not in completed:
                continue
            errors.extend(d3_proof_errors(row, label, index))
    return errors


def validate_summary_quality(
    rows: List[Dict[str, Any]], fields: List[str], label: str
) -> List[str]:
    errors: List[str] = []
    if not rows:
        return errors

    available = set(rows[0])
    target_fields = [field for field in fields if field in available]
    for index, row in enumerate(rows, start=2):
        for field in target_fields:
            text = str(row.get(field) or "")
            for pattern in GENERIC_SUMMARY_PATTERNS:
                if pattern.search(text):
                    errors.append(
                        f"{label} row {index} field {field}: generic summary phrase "
                        f"{pattern.pattern!r}; explain category, source/input, "
                        "logic/action, output or side effect, and judgment"
                    )
    return errors


def custom_code_required(reconciliation_rows: Iterable[Dict[str, Any]]) -> bool:
    for row in reconciliation_rows:
        label = f"{row.get('workstream', '')} {row.get('object_family', '')}".lower()
        if "custom" not in label:
            continue
        total, problem = to_int(row, "total_source_count")
        if problem:
            continue
        not_applicable, _ = to_int(row, "not_applicable_count")
        user_excluded, _ = to_int(row, "user_excluded_count")
        if total > not_applicable + user_excluded:
            return True
    return False


def validate_full_audit_object_family_rows(rows: Iterable[Dict[str, Any]]) -> List[str]:
    errors: List[str] = []
    row_list = list(rows)
    required_families = {
        "tags": ("tag", "tags"),
        "triggers": ("trigger", "triggers"),
        "variables": ("variable", "variables"),
    }
    for label, terms in required_families.items():
        matching = [
            row
            for row in row_list
            if any(term in str(row.get("object_family", "")).lower() for term in terms)
        ]
        if not matching:
            errors.append(
                f"strict evidence: missing reconciliation/object-family row for {label}; "
                "full audits must reconcile tags, triggers, and variables separately"
            )
            continue
        if not any((to_int(row, "total_source_count")[0] > 0) for row in matching):
            errors.append(
                f"strict evidence: reconciliation rows for {label} have zero total_source_count"
            )
    return errors


def validate_custom_code_rows(rows: List[Dict[str, Any]], label: str) -> List[str]:
    errors = validate_required_table(rows, CUSTOM_CODE_REQUIRED_FIELDS, label)
    if errors:
        return errors

    for index, row in enumerate(rows, start=2):
        review_status = str(row.get("export_review_completed", "")).strip().lower()
        semantic_status = str(row.get("semantic_status", "")).strip().lower()
        if review_status not in {"yes", "not applicable", "n/a"}:
            errors.append(
                f"{label} row {index}: export_review_completed must be Yes or Not applicable"
            )
        if semantic_status in {"", "review later", "pending", "pending review"}:
            errors.append(f"{label} row {index}: semantic_status is not a decision")
        if review_status == "yes" and semantic_status not in {"not applicable", "n/a"}:
            output_text = row.get("expected_output_or_side_effect", "")
            if word_count(output_text) < 5 or not has_signal(output_text, OUTPUT_SIGNAL_PATTERNS):
                errors.append(
                    f"{label} row {index}: expected_output_or_side_effect must describe "
                    "what the code returns, pushes, loads, writes, calls, or mutates"
                )
    errors.extend(validate_summary_quality(rows, CUSTOM_CODE_SUMMARY_FIELDS, label))
    return errors


def validate_baseline_rows(rows: List[Dict[str, Any]], label: str) -> List[str]:
    errors = validate_required_table(rows, BASELINE_REQUIRED_FIELDS, label)
    if errors:
        return errors
    seen_modules = set()
    for index, row in enumerate(rows, start=2):
        module_name = str(row.get("module_name") or "").strip()
        module_status = str(row.get("module_status") or "").strip().lower()
        finding_type = str(row.get("finding_type") or "").strip().lower()
        if module_name:
            seen_modules.add(module_name)
        if module_status not in {"findings", "zero_findings"}:
            errors.append(
                f"{label} row {index}: module_status must be findings or zero_findings"
            )
        if finding_type != "zero_findings" and not str(row.get("default_action") or "").strip():
            errors.append(f"{label} row {index}: finding lacks default_action")
        if finding_type != "zero_findings" and not str(row.get("required_resolution") or "").strip():
            errors.append(f"{label} row {index}: finding lacks required_resolution")
    if not seen_modules:
        errors.append(f"{label}: no baseline modules found")
    else:
        missing_modules = sorted(PROTECTED_BASELINE_MODULES - seen_modules)
        if missing_modules:
            errors.append(
                f"{label}: missing protected deterministic baseline module(s): "
                + ", ".join(missing_modules)
            )
    return errors


def validate_operation_packet_rows(rows: List[Dict[str, Any]], label: str) -> List[str]:
    errors = validate_required_table(rows, OPERATION_PACKET_REQUIRED_FIELDS, label)
    if errors:
        return errors

    seen_ids: set[str] = set()
    for index, row in enumerate(rows, start=2):
        for field in OPERATION_PACKET_NONBLANK_FIELDS:
            if field_is_blank(row.get(field)):
                errors.append(f"{label} row {index}: blank {field}")

        operation_id = str(row.get("operation_id") or "").strip()
        if operation_id:
            if operation_id in seen_ids:
                errors.append(f"{label} row {index}: duplicate operation_id {operation_id}")
            seen_ids.add(operation_id)

        resolution = compact_text(row.get("resolution_status")).replace(" ", "_")
        accepted = {
            "cleanup_operation",
            "documented_exception",
            "runtime_blocker",
            "owner_decision_needed",
            "not_applicable",
        }
        if resolution not in accepted:
            errors.append(
                f"{label} row {index}: resolution_status must be one of "
                f"{', '.join(sorted(accepted))}"
            )
        if resolution in {"runtime_blocker", "owner_decision_needed"} and field_is_blank(
            row.get("blocker")
        ):
            errors.append(f"{label} row {index}: blocker is required for {resolution}")

        if "technical" in str(row.get("source_lenses") or "").lower() and not any(
            not field_is_blank(row.get(field)) for field in TECHNICAL_PACKET_HANDOFF_FIELDS
        ):
            errors.append(
                f"{label} row {index}: technical source lens requires "
                "technical_handoff_packet, handoff_packet, or handoff_evidence"
            )

        action_text = str(row.get("exact_proposed_action") or "")
        for pattern in VAGUE_ACTION_PATTERNS:
            if pattern.search(action_text):
                errors.append(
                    f"{label} row {index}: exact_proposed_action is vague: {action_text!r}"
                )
                break
    return errors


def validate_cleanup_rows_backed_by_packets(
    workbook_rows: Dict[str, List[Dict[str, Any]]], packet_rows: List[Dict[str, Any]]
) -> List[str]:
    errors: List[str] = []
    packet_ids = {
        str(row.get("operation_id") or "").strip()
        for row in packet_rows
        if str(row.get("operation_id") or "").strip()
    }
    for sheet_name, rows in workbook_rows.items():
        normalized = normalize_sheet_name(sheet_name)
        if "cleanup" not in normalized or "plan" not in normalized:
            continue
        if not rows:
            continue
        headers = {normalize_header(header): header for header in rows[0]}
        level_key = headers.get("level")
        id_key = headers.get("operation_id") or headers.get("id")
        if not id_key:
            errors.append(
                f"{sheet_name}: cleanup plan needs ID or operation_id values that link to operation packets"
            )
            continue
        for index, row in enumerate(rows, start=2):
            level = str(row.get(level_key) or "").strip().lower() if level_key else "single"
            if level == "summary":
                continue
            row_id = str(row.get(id_key) or "").strip()
            if not row_id:
                errors.append(f"{sheet_name} row {index}: cleanup row lacks operation packet ID")
                continue
            if row_id not in packet_ids:
                errors.append(
                    f"{sheet_name} row {index}: cleanup row ID {row_id!r} has no matching operation packet"
                )
    return errors


def validate_placeholder_language(
    workbook_rows: Dict[str, List[Dict[str, Any]]]
) -> List[str]:
    errors: List[str] = []
    target_sheet_terms = ("finding", "operation", "roadmap", "cleanup", "plan")
    for sheet_name, rows in workbook_rows.items():
        normalized = normalize_sheet_name(sheet_name)
        if not any(term in normalized for term in target_sheet_terms):
            continue
        for row_index, row in enumerate(rows, start=2):
            for field, value in row.items():
                text = str(value or "")
                for pattern in PLACEHOLDER_PATTERNS:
                    if pattern.search(text):
                        errors.append(
                            f"{sheet_name} row {row_index} field {field}: "
                            f"deferred audit-work placeholder {pattern.pattern!r}"
                        )
                for pattern in VAGUE_ACTION_PATTERNS:
                    if pattern.search(text):
                        errors.append(
                            f"{sheet_name} row {row_index} field {field}: "
                            f"vague cleanup action {pattern.pattern!r}; state exact "
                            "object state or blocker"
                        )
    return errors


def validate_cleanup_plan_parent_detail(
    workbook_rows: Dict[str, List[Dict[str, Any]]]
) -> List[str]:
    errors: List[str] = []
    for sheet_name, rows in workbook_rows.items():
        normalized = normalize_sheet_name(sheet_name)
        if "cleanup" not in normalized or "plan" not in normalized:
            continue
        if not rows:
            continue
        headers = {normalize_header(header): header for header in rows[0]}
        if "level" not in headers:
            errors.append(
                f"{sheet_name}: compact cleanup plan is missing Level column "
                "(Summary, Detail, or Single)"
            )
            continue
        level_key = headers["level"]
        id_key = headers.get("id")
        previous_summary_id = ""
        previous_summary_row = 0
        summary_has_detail = False
        for index, row in enumerate(rows, start=2):
            level = str(row.get(level_key) or "").strip().lower()
            row_id = str(row.get(id_key) or "").strip() if id_key else ""
            if level not in {"summary", "detail", "single"}:
                errors.append(
                    f"{sheet_name} row {index}: Level must be Summary, Detail, or Single"
                )
                continue
            if level == "summary":
                if previous_summary_id and not summary_has_detail:
                    errors.append(
                        f"{sheet_name} row {previous_summary_row}: Summary row has no "
                        "immediate Detail rows; use Single for generic hygiene buckets"
                    )
                previous_summary_id = row_id
                previous_summary_row = index
                summary_has_detail = False
            elif level == "detail":
                if not previous_summary_id:
                    errors.append(
                        f"{sheet_name} row {index}: Detail row has no preceding Summary row"
                    )
                else:
                    summary_has_detail = True
                    if row_id and previous_summary_id and not row_id.startswith(f"{previous_summary_id}."):
                        errors.append(
                            f"{sheet_name} row {index}: Detail ID {row_id!r} should "
                            f"start with parent Summary ID {previous_summary_id!r}."
                        )
            elif level == "single":
                if previous_summary_id and not summary_has_detail:
                    errors.append(
                        f"{sheet_name} row {previous_summary_row}: Summary row has no "
                        "Detail rows before the next Single row"
                    )
                previous_summary_id = ""
                previous_summary_row = 0
                summary_has_detail = False
        if previous_summary_id and not summary_has_detail:
            errors.append(
                f"{sheet_name} row {previous_summary_row}: Summary row has no "
                "Detail rows before the sheet ends"
            )
    return errors


def first_present(headers: Dict[str, str], candidates: List[str]) -> str:
    for candidate in candidates:
        if candidate in headers:
            return headers[candidate]
    return ""


def validate_cleanup_plan_human_taxonomy(
    workbook_rows: Dict[str, List[Dict[str, Any]]]
) -> List[str]:
    errors: List[str] = []
    for sheet_name, rows in workbook_rows.items():
        normalized = normalize_sheet_name(sheet_name)
        if "cleanup" not in normalized or "plan" not in normalized:
            continue
        if not rows:
            continue
        headers = {normalize_header(header): header for header in rows[0]}
        level_key = headers.get("level")
        taxonomy_key = first_present(headers, CLEANUP_PLAN_TAXONOMY_FIELDS)
        problem_key = first_present(headers, CLEANUP_PLAN_PROBLEM_FIELDS)
        action_key = first_present(headers, CLEANUP_PLAN_ACTION_FIELDS)
        if not taxonomy_key:
            errors.append(
                f"{sheet_name}: cleanup plan needs an Area / problem type column "
                "so rows use human problem taxonomy instead of internal scan labels"
            )
        if not problem_key:
            errors.append(
                f"{sheet_name}: cleanup plan needs a Problem / evidence column "
                "with a concrete user-facing issue and evidence example"
            )
        if not action_key:
            errors.append(
                f"{sheet_name}: cleanup plan needs an Action / priority / QA column "
                "with the proposed action, priority/confidence, and QA or blocker"
            )
        if not taxonomy_key or not problem_key or not action_key:
            continue

        for index, row in enumerate(rows, start=2):
            level = str(row.get(level_key) or "").strip().lower() if level_key else "single"
            if level == "summary":
                continue
            taxonomy = str(row.get(taxonomy_key) or "").strip()
            problem = str(row.get(problem_key) or "").strip()
            action = str(row.get(action_key) or "").strip()
            if generic_or_blank(taxonomy) or word_count(taxonomy) < 3:
                errors.append(
                    f"{sheet_name} row {index}: Area / problem type is missing "
                    "a human area plus second-level problem"
                )
            if generic_or_blank(problem) or word_count(problem) < 7:
                errors.append(
                    f"{sheet_name} row {index}: Problem / evidence is too short "
                    "to explain the visible issue and evidence"
                )
            if generic_or_blank(action) or word_count(action) < 5:
                errors.append(
                    f"{sheet_name} row {index}: Action / priority / QA is too "
                    "short to guide action, QA, priority, or blocker"
                )
            for field, text in (
                (taxonomy_key, taxonomy),
                (problem_key, problem),
                (action_key, action),
            ):
                for pattern in GENERIC_SUMMARY_PATTERNS:
                    if pattern.search(text):
                        errors.append(
                            f"{sheet_name} row {index} field {field}: generic "
                            f"internal label {pattern.pattern!r}; translate it "
                            "into a concrete human problem"
                        )
    return errors


def workbook_architecture_warnings(workbook_rows: Dict[str, List[Dict[str, Any]]]) -> List[str]:
    warnings: List[str] = []
    if len(workbook_rows) > 8:
        warnings.append(
            f"workbook architecture: {len(workbook_rows)} tabs found; compact "
            "stakeholder outputs should normally stay at 7-8 tabs or fewer"
        )
    for sheet_name, rows in workbook_rows.items():
        if not rows:
            continue
        column_count = len(rows[0])
        if column_count > 8:
            warnings.append(
                f"workbook architecture: sheet {sheet_name!r} has {column_count} "
                "columns; compact stakeholder/proof tabs should normally stay "
                "around 5-6 useful columns unless this is a technical appendix"
            )
    return warnings


def validate_strict_evidence(path: Path, reconciliation_rows: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    if path.suffix.lower() != ".xlsx":
        return ["--strict-evidence requires an XLSX workbook"], warnings

    workbook_rows = load_xlsx_workbook(path)
    errors.extend(validate_full_audit_object_family_rows(reconciliation_rows))

    semantic_name, semantic_rows = find_sheet(workbook_rows, ["semantic", "matrix"])
    baseline_name, baseline_rows = find_sheet(workbook_rows, ["baseline"])
    packet_name, packet_rows = find_sheet(workbook_rows, ["reconciled", "operations"])
    if not packet_name:
        packet_name, packet_rows = find_sheet(workbook_rows, ["operation", "packet"])
    if not packet_name:
        errors.append("strict evidence: missing Reconciled Operations / Operation Packets sheet")
    else:
        errors.extend(validate_operation_packet_rows(packet_rows, f"{packet_name}"))
        errors.extend(validate_cleanup_rows_backed_by_packets(workbook_rows, packet_rows))

    if not semantic_name:
        errors.append("strict evidence: missing Semantic Object Matrix sheet")
    else:
        errors.extend(
            validate_required_table(
                semantic_rows,
                SEMANTIC_MATRIX_REQUIRED_FIELDS,
                f"{semantic_name}",
            )
        )
        if semantic_rows:
            errors.extend(validate_semantic_depth_rows(semantic_rows, f"{semantic_name}"))
            errors.extend(
                validate_summary_quality(
                    semantic_rows,
                    SEMANTIC_SUMMARY_FIELDS,
                    f"{semantic_name}",
                )
            )

    if not baseline_name:
        errors.append("strict evidence: missing Deterministic Baseline Findings sheet")
    else:
        errors.extend(validate_baseline_rows(baseline_rows, f"{baseline_name}"))

    custom_name, custom_rows = find_sheet(workbook_rows, ["custom", "code"])
    if custom_code_required(reconciliation_rows) and not custom_name:
        errors.append(
            "strict evidence: reconciliation indicates custom-code scope, "
            "but no Custom Code Semantic Review sheet was found"
        )
    elif custom_name:
        errors.extend(validate_custom_code_rows(custom_rows, f"{custom_name}"))

    errors.extend(validate_placeholder_language(workbook_rows))
    errors.extend(validate_cleanup_plan_parent_detail(workbook_rows))
    errors.extend(validate_cleanup_plan_human_taxonomy(workbook_rows))
    warnings.extend(workbook_architecture_warnings(workbook_rows))
    if not custom_code_required(reconciliation_rows) and not custom_name:
        warnings.append("strict evidence: no custom-code review sheet found; treated as not in scope")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV, JSON, or XLSX reconciliation file")
    parser.add_argument(
        "--strict-evidence",
        action="store_true",
        help=(
            "For full audit/cleanup-plan XLSX workbooks, also validate Semantic "
            "Object Matrix and Custom Code Semantic Review evidence."
        ),
    )
    args = parser.parse_args()

    try:
        rows = load_rows(args.input)
        errors, warnings = validate_rows(rows)
        if args.strict_evidence:
            strict_errors, strict_warnings = validate_strict_evidence(args.input, rows)
            errors.extend(strict_errors)
            warnings.extend(strict_warnings)
    except Exception as exc:  # noqa: BLE001 - CLI should report any loading problem.
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Gate status: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1

    print(f"Gate status: PASS ({len(rows)} row(s), {len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
