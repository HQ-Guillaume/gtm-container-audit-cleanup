#!/usr/bin/env python3
"""Build the protected GTM audit evidence package.

This command is the deterministic first half of a full skill execution. It
creates the source model and the three independent cleanup lens artifacts that
must exist before a user-facing cleanup plan is compiled.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from gtm_baseline_audit import audit_export
from gtm_custom_code_extract import extract_export
from gtm_semantic_source_scan import scan_export
from gtm_source_model import build_model


def write_json(path: Path, payload: dict[str, Any], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2 if pretty else None),
        encoding="utf-8",
    )


def nonzero_findings(payload: dict[str, Any]) -> int:
    return sum(
        1
        for finding in payload.get("findings", [])
        if finding.get("finding_type") != "zero_findings"
    )


def build_package(export_path: Path, out_dir: Path, pretty: bool = False) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)

    source_model = build_model(export_path)
    deterministic = audit_export(export_path)
    technical = extract_export(export_path)
    semantic = scan_export(export_path)

    files = {
        "source_model": out_dir / "source_model.json",
        "deterministic_findings": out_dir / "deterministic_findings.json",
        "technical_code_findings": out_dir / "technical_code_findings.json",
        "semantic_findings": out_dir / "semantic_findings.json",
        "manifest": out_dir / "audit_package_manifest.json",
    }

    manifest = {
        "artifact": str(export_path),
        "kind": "gtm_protected_audit_package_manifest",
        "status": "pass" if source_model.get("coverage_gate") == "pass" else "blocked",
        "source_model_coverage_gate": source_model.get("coverage_gate"),
        "counts": {
            "source_model_objects": sum(
                len(source_model.get("objects", {}).get(key, []))
                for key in ("tags", "triggers", "variables", "customTemplates")
            ),
            "field_edges": source_model.get("counts", {}).get("field_edges", 0),
            "trigger_edges": source_model.get("counts", {}).get("trigger_edges", 0),
            "deterministic_findings": nonzero_findings(deterministic),
            "deterministic_zero_finding_rows": sum(
                1
                for finding in deterministic.get("findings", [])
                if finding.get("finding_type") == "zero_findings"
            ),
            "technical_code_rows": len(technical.get("rows", [])),
            "semantic_source_rows": len(semantic.get("rows", [])),
        },
        "required_next_artifact": "reconciled_operations.json",
        "files": {key: str(path) for key, path in files.items() if key != "manifest"},
        "notes": [
            "This package is evidence, not the user-facing cleanup plan.",
            "Compile visible rows only after deterministic, semantic, and technical findings are reconciled.",
        ],
    }
    manifest["files"]["manifest"] = str(files["manifest"])

    write_json(files["source_model"], source_model, pretty)
    write_json(files["deterministic_findings"], deterministic, pretty)
    write_json(files["technical_code_findings"], technical, pretty)
    write_json(files["semantic_findings"], semantic, pretty)
    write_json(files["manifest"], manifest, pretty)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Path to a GTM container export JSON")
    parser.add_argument(
        "--out-dir",
        type=Path,
        required=True,
        help="Directory where source/lens artifacts should be written",
    )
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON files")
    args = parser.parse_args()

    result = build_package(args.export, args.out_dir, args.pretty)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
