#!/usr/bin/env python3
"""Dependency-light workbook helpers for GTM audit validation scripts."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple
from xml.etree import ElementTree

HEADER_ALIASES = {
    "total": "total_source_count",
    "total_count": "total_source_count",
    "source_count": "total_source_count",
    "total_source_objects": "total_source_count",
    "dependency_mapped": "dependency_mapped_count",
    "measurement_diagnosed": "measurement_diagnosed_count",
    "business_diagnosed_count": "measurement_diagnosed_count",
    "measurement_diagnosis_count": "measurement_diagnosed_count",
    "semantically_validated": "semantically_validated_count",
    "semantic_validated_count": "semantically_validated_count",
    "cleanup_decided_count": "cleanup_decision_count",
    "cleanup_decisioned_count": "cleanup_decision_count",
    "cleanup_decision_objects": "cleanup_decision_count",
    "not_applicable": "not_applicable_count",
    "user_excluded": "user_excluded_count",
    "unresolved": "unresolved_count",
    "source_output_status": "source_or_code_logic_status",
    "source_logic_status": "source_or_code_logic_status",
    "code_logic_status": "source_or_code_logic_status",
    "configuration_code_logic_status": "configuration_logic_status",
    "business_role": "inferred_business_role",
    "business_intent": "inferred_business_role",
    "business_outcome": "decision_outcome",
    "outcome": "decision_outcome",
    "conversion_type": "conversion_hierarchy",
    "signal_type": "conversion_hierarchy",
    "vendor_platform_role": "platform_role",
    "destination_role": "platform_role",
    "data_contract": "expected_data_contract",
    "expected_contract": "expected_data_contract",
    "payload_contract": "expected_data_contract",
    "linked_finding_operation": "finding_or_operation_id",
    "linked_finding_or_operation": "finding_or_operation_id",
    "finding_operation_id": "finding_or_operation_id",
    "blocker_next_evidence": "blocker_or_next_evidence",
    "trigger_consumer_context": "trigger_or_consumer_context",
    "consumer_context": "trigger_or_consumer_context",
    "expected_output_side_effect": "expected_output_or_side_effect",
    "expected_output": "expected_output_or_side_effect",
    "operation": "operation_id",
    "operationid": "operation_id",
    "op_id": "operation_id",
    "objects": "affected_objects",
    "affected_object_s": "affected_objects",
    "identity": "object_identity",
    "object_key": "object_identity",
    "lenses": "source_lenses",
    "current_state": "current_behavior",
    "current_behaviour": "current_behavior",
    "why_matters": "why_it_matters",
    "expected_state": "expected_clean_state",
    "clean_state": "expected_clean_state",
    "exact_action": "exact_proposed_action",
    "proposed_action": "exact_proposed_action",
    "qa": "qa_steps",
    "qa_status": "qa_steps",
    "source_findings": "source_finding_ids",
    "linked_source_finding_ids": "source_finding_ids",
    "d3_source_inputs": "d3_inputs_or_sources",
    "d3_sources": "d3_inputs_or_sources",
    "d3_inputs": "d3_inputs_or_sources",
    "d3_output": "d3_output_or_side_effect",
    "d3_side_effect": "d3_output_or_side_effect",
    "d3_consumer": "d3_consumer_expectation",
    "d3_decision": "d3_correctness_decision",
}


def normalize_header(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = text.strip("_")
    return HEADER_ALIASES.get(text, text)


def normalize_sheet_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def column_index(cell_ref: str) -> int:
    letters = "".join(ch for ch in cell_ref if ch.isalpha()).upper()
    index = 0
    for char in letters:
        index = index * 26 + (ord(char) - ord("A") + 1)
    return index - 1


def xml_text(node: ElementTree.Element | None) -> str:
    if node is None:
        return ""
    return "".join(node.itertext())


def workbook_target_path(target: str) -> str:
    return "xl/" + target.lstrip("/") if not target.startswith("xl/") else target


def rows_from_values(parsed_rows: List[List[Any]]) -> List[Dict[str, Any]]:
    if not parsed_rows:
        return []
    headers = [normalize_header(value) for value in parsed_rows[0]]
    rows = []
    for values in parsed_rows[1:]:
        if not values or all(value in (None, "") for value in values):
            continue
        rows.append({headers[i]: values[i] for i in range(min(len(headers), len(values)))})
    return rows


def load_xlsx_workbook_openpyxl(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    try:
        import openpyxl  # type: ignore
    except ImportError as exc:
        raise RuntimeError("openpyxl is unavailable") from exc

    workbook = openpyxl.load_workbook(path, data_only=True, read_only=True)
    result: Dict[str, List[Dict[str, Any]]] = {}
    for sheet_name in workbook.sheetnames:
        sheet = workbook[sheet_name]
        values = [list(row) for row in sheet.iter_rows(values_only=True)]
        result[sheet_name] = rows_from_values(values)
    workbook.close()
    return result


def load_xlsx_workbook_stdlib(path: Path) -> Dict[str, List[Dict[str, Any]]]:
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

        shared_strings: List[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall("main:si", ns):
                shared_strings.append(xml_text(item))

        result: Dict[str, List[Dict[str, Any]]] = {}
        for sheet in workbook.findall("main:sheets/main:sheet", ns):
            name = sheet.attrib.get("name", "")
            rel_id = sheet.attrib.get(f"{{{ns['rel']}}}id")
            target = rel_targets.get(rel_id or "")
            if not name or not target:
                continue
            sheet_target = workbook_target_path(target)
            if sheet_target not in archive.namelist():
                continue

            parsed_rows: List[List[str]] = []
            sheet_root = ElementTree.fromstring(archive.read(sheet_target))
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
            result[name] = rows_from_values(parsed_rows)
    return result


def load_xlsx_workbook(path: Path) -> Dict[str, List[Dict[str, Any]]]:
    try:
        return load_xlsx_workbook_openpyxl(path)
    except Exception as first_exc:  # noqa: BLE001 - stdlib fallback covers missing optional deps.
        try:
            return load_xlsx_workbook_stdlib(path)
        except Exception as second_exc:  # noqa: BLE001 - preserve both failure reasons.
            raise RuntimeError(
                f"Unable to read XLSX workbook with openpyxl or stdlib fallback. "
                f"openpyxl error: {first_exc}; fallback error: {second_exc}"
            ) from second_exc


def find_sheet(
    workbook_rows: Dict[str, List[Dict[str, Any]]], required_terms: Iterable[str]
) -> Tuple[str | None, List[Dict[str, Any]]]:
    terms = [term.lower() for term in required_terms]
    for sheet_name, rows in workbook_rows.items():
        normalized = normalize_sheet_name(sheet_name)
        if all(term in normalized for term in terms):
            return sheet_name, rows
    return None, []
