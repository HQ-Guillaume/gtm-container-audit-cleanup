#!/usr/bin/env python3
"""Run synthetic regression checks for GTM cleanup helper scripts."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def export(cv: dict) -> dict:
    return {"exportFormatVersion": 2, "exportTime": "2026-01-01 00:00:00", "containerVersion": cv}


def base_cv() -> dict:
    return {
        "accountId": "1",
        "containerId": "2",
        "containerVersionId": "0",
        "tag": [
            {
                "tagId": "1",
                "name": "Meta - PageView",
                "type": "cvt_2_10",
                "firingTriggerId": ["1"],
                "parentFolderId": "1",
                "parameter": [
                    {"type": "TEMPLATE", "key": "value", "value": "{{DLV - value}}"}
                ],
            }
        ],
        "trigger": [{"triggerId": "1", "name": "PV - All Pages", "type": "PAGEVIEW"}],
        "variable": [
            {
                "variableId": "1",
                "name": "DLV - value",
                "type": "v",
                "parameter": [{"type": "TEMPLATE", "key": "name", "value": "value"}],
            }
        ],
        "folder": [{"folderId": "1", "name": "Meta"}],
        "customTemplate": [{"templateId": "10", "name": "Meta Pixel", "templateData": "x"}],
        "builtInVariable": [{"name": "Page URL", "type": "PAGE_URL"}],
    }


def process_cv() -> dict:
    html = "<script>dataLayer.push({event:'bridge_event', value:'{{DLV - value}}'});</script>"
    cjs = "function() { return {{DLV - value}} || ''; }"
    bad_total_cjs = "function() { return Number({{DLV - product price 1}}) + Number({{DLV - product price 2}}); }"
    return {
        "accountId": "1",
        "containerId": "2",
        "containerVersionId": "0",
        "tag": [
            {
                "tagId": "1",
                "name": "Vendor - Event A",
                "type": "cvt_2_10",
                "firingTriggerId": ["1"],
                "parameter": [{"type": "TEMPLATE", "key": "value", "value": "{{DLV - value}}"}],
            },
            {
                "tagId": "2",
                "name": "Vendor - Event B",
                "type": "cvt_2_10",
                "firingTriggerId": ["2"],
                "parameter": [{"type": "TEMPLATE", "key": "value", "value": "{{DLV - value}}"}],
            },
            {
                "tagId": "3",
                "name": "HTML - Bridge 1",
                "type": "html",
                "firingTriggerId": ["1"],
                "parameter": [{"type": "TEMPLATE", "key": "html", "value": html}],
            },
            {
                "tagId": "4",
                "name": "HTML - Bridge 2",
                "type": "html",
                "firingTriggerId": ["1"],
                "parameter": [{"type": "TEMPLATE", "key": "html", "value": html}],
            },
            {
                "tagId": "5",
                "name": "GA4 - checkout_step_1 legacy",
                "type": "gaawe",
                "firingTriggerId": ["4"],
                "parameter": [
                    {"type": "TEMPLATE", "key": "eventName", "value": "checkout_step_1"},
                    {
                        "type": "TEMPLATE",
                        "key": "item_id",
                        "value": "{{DLV - UA fixed product ID}}",
                    },
                ],
            },
            {
                "tagId": "985",
                "name": "PA - Consent Mode",
                "type": "cvt_2_10",
                "firingTriggerId": ["6", "7"],
                "blockingTriggerId": ["8", "9"],
                "parameter": [
                    {"type": "TEMPLATE", "key": "commandChoice", "value": "setConsentMode"},
                    {"type": "TEMPLATE", "key": "consentPurpose", "value": "AM"},
                    {
                        "type": "TEMPLATE",
                        "key": "consentMode",
                        "value": "{{CJS - Consent Mode State}}",
                    },
                    {
                        "type": "TEMPLATE",
                        "key": "configuration",
                        "value": "{{PA - Configuration}}",
                    },
                ],
            },
            {
                "tagId": "1006",
                "name": "PA - Consent Mode (AM)",
                "type": "cvt_2_10",
                "firingTriggerId": ["6", "7"],
                "blockingTriggerId": ["8", "9"],
                "parameter": [
                    {"type": "TEMPLATE", "key": "commandChoice", "value": "setConsentMode"},
                    {"type": "TEMPLATE", "key": "consentPurpose", "value": "AM"},
                    {
                        "type": "TEMPLATE",
                        "key": "consentMode",
                        "value": "{{CJS - Consent Mode State}}",
                    },
                    {
                        "type": "TEMPLATE",
                        "key": "configuration",
                        "value": "{{PA - Configuration}}",
                    },
                ],
            },
        ],
        "trigger": [
            {"triggerId": "1", "name": "PV - All Pages", "type": "PAGEVIEW"},
            {"triggerId": "2", "name": "PV - All Pages Copy", "type": "PAGEVIEW"},
            {
                "triggerId": "3",
                "name": "Group - Single",
                "type": "TRIGGER_GROUP",
                "parameter": [
                    {
                        "type": "LIST",
                        "key": "triggerIds",
                        "list": [{"type": "TEMPLATE", "value": "1"}],
                    }
                ],
            },
            {"triggerId": "4", "name": "CE - checkout_step_1", "type": "CUSTOM_EVENT"},
            {"triggerId": "6", "name": "CE - CMP Event", "type": "CUSTOM_EVENT"},
            {"triggerId": "7", "name": "CE - Piano Init", "type": "CUSTOM_EVENT"},
            {"triggerId": "8", "name": "Block - CMP Interaction", "type": "CUSTOM_EVENT"},
            {"triggerId": "9", "name": "Block - Preview", "type": "CUSTOM_EVENT"},
        ],
        "variable": [
            {
                "variableId": "1",
                "name": "DLV - value",
                "type": "v",
                "parameter": [{"type": "TEMPLATE", "key": "name", "value": "value"}],
            },
            {
                "variableId": "2",
                "name": "DLV - value copy",
                "type": "v",
                "parameter": [{"type": "TEMPLATE", "key": "name", "value": "value"}],
            },
            {
                "variableId": "3",
                "name": "CJS - value",
                "type": "jsm",
                "parameter": [{"type": "TEMPLATE", "key": "javascript", "value": cjs}],
            },
            {
                "variableId": "4",
                "name": "CJS - value copy",
                "type": "jsm",
                "parameter": [{"type": "TEMPLATE", "key": "javascript", "value": cjs}],
            },
            {
                "variableId": "5",
                "name": "DLV - UA fixed product ID",
                "type": "v",
                "parameter": [
                    {
                        "type": "TEMPLATE",
                        "key": "name",
                        "value": "ecommerce.checkout.products.0.id",
                    }
                ],
            },
            {
                "variableId": "6",
                "name": "DLV - product price 1",
                "type": "v",
                "parameter": [{"type": "TEMPLATE", "key": "name", "value": "ecommerce.checkout.products.0.price"}],
            },
            {
                "variableId": "7",
                "name": "DLV - product price 2",
                "type": "v",
                "parameter": [{"type": "TEMPLATE", "key": "name", "value": "ecommerce.checkout.products.1.price"}],
            },
            {
                "variableId": "8",
                "name": "CJS - total price bad fixed indexes",
                "type": "jsm",
                "parameter": [{"type": "TEMPLATE", "key": "javascript", "value": bad_total_cjs}],
            },
            {
                "variableId": "9",
                "name": "CJS - Consent Mode State",
                "type": "jsm",
                "parameter": [
                    {
                        "type": "TEMPLATE",
                        "key": "javascript",
                        "value": "function() { return 'opt-in'; }",
                    }
                ],
            },
            {
                "variableId": "10",
                "name": "PA - Configuration",
                "type": "c",
                "parameter": [{"type": "TEMPLATE", "key": "value", "value": "site=123"}],
            },
        ],
        "customTemplate": [{"templateId": "10", "name": "Vendor Template", "templateData": "x"}],
        "builtInVariable": [{"name": "Page URL", "type": "PAGE_URL"}],
    }


def run(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-B", *args],
        cwd=str(ROOT),
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


PASS_CHECKS = {
    "valid_view",
    "diff_ops",
    "source_model",
    "baseline_audit",
    "custom_code_extract",
    "semantic_source_scan",
    "package_build",
}


def write_test_exports(tmpdir: Path) -> dict[str, Path]:
    paths = {
        "original": tmpdir / "original.json",
        "valid": tmpdir / "valid.json",
        "missing_builtins": tmpdir / "missing-builtins.json",
        "renamed": tmpdir / "renamed.json",
        "process_export": tmpdir / "process.json",
        "baseline_json": tmpdir / "baseline.json",
        "partial_resolution": tmpdir / "partial-resolution.json",
        "full_resolution": tmpdir / "full-resolution.json",
        "package_dir": tmpdir / "package",
    }

    cv = base_cv()
    paths["original"].write_text(json.dumps(export(cv)), encoding="utf-8")
    paths["valid"].write_text(json.dumps(export(cv)), encoding="utf-8")

    bad_cv = json.loads(json.dumps(cv))
    bad_cv.pop("builtInVariable")
    paths["missing_builtins"].write_text(json.dumps(export(bad_cv)), encoding="utf-8")

    renamed_cv = json.loads(json.dumps(cv))
    renamed_cv["tag"][0]["name"] = "Meta - page_view"
    paths["renamed"].write_text(json.dumps(export(renamed_cv)), encoding="utf-8")
    paths["process_export"].write_text(json.dumps(export(process_cv())), encoding="utf-8")
    return paths


def run_checks(paths: dict[str, Path]) -> list[tuple[str, subprocess.CompletedProcess[str]]]:
    return [
        (
            "valid_view",
            run(
                "gtm_validate_artifact.py",
                str(paths["valid"]),
                "--original",
                str(paths["original"]),
                "--mode",
                "same-container-view",
            ),
        ),
        (
            "missing_builtins",
            run(
                "gtm_validate_artifact.py",
                str(paths["missing_builtins"]),
                "--original",
                str(paths["original"]),
                "--mode",
                "same-container-view",
            ),
        ),
        (
            "rename_churn",
            run(
                "gtm_validate_artifact.py",
                str(paths["renamed"]),
                "--original",
                str(paths["original"]),
                "--mode",
                "same-container-view",
            ),
        ),
        ("diff_ops", run("gtm_diff_operations.py", str(paths["original"]), str(paths["renamed"]))),
        ("source_model", run("gtm_source_model.py", str(paths["process_export"]))),
        ("baseline_audit", run("gtm_baseline_audit.py", str(paths["process_export"]))),
        ("custom_code_extract", run("gtm_custom_code_extract.py", str(paths["process_export"]))),
        ("semantic_source_scan", run("gtm_semantic_source_scan.py", str(paths["process_export"]))),
        (
            "package_build",
            run(
                "gtm_audit_package_build.py",
                str(paths["process_export"]),
                "--out-dir",
                str(paths["package_dir"]),
            ),
        ),
    ]


def validate_check_exit_codes(
    checks: list[tuple[str, subprocess.CompletedProcess[str]]],
    failures: list[dict],
) -> None:
    for name, proc in checks:
        passed = proc.returncode == 0
        if passed != (name in PASS_CHECKS):
            failures.append(
                {
                    "check": name,
                    "returncode": proc.returncode,
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                }
            )


def validate_source_model(proc: subprocess.CompletedProcess[str], failures: list[dict]) -> None:
    if proc.returncode != 0:
        return
    source_model = json.loads(proc.stdout)
    counts = source_model.get("counts", {})
    if (
        source_model.get("kind") != "gtm_source_model_navigation_map"
        or source_model.get("coverage_gate") != "pass"
        or counts.get("field_edges", 0) == 0
        or counts.get("trigger_edges", 0) == 0
        or not source_model.get("raw_evidence_must_be_rechecked_for_findings")
    ):
        failures.append(
            {
                "check": "source_model_expected_map",
                "kind": source_model.get("kind"),
                "coverage_gate": source_model.get("coverage_gate"),
                "counts": counts,
            }
        )


def validate_baseline(
    proc: subprocess.CompletedProcess[str],
    paths: dict[str, Path],
    failures: list[dict],
) -> None:
    if proc.returncode != 0:
        return

    baseline = json.loads(proc.stdout)
    paths["baseline_json"].write_text(proc.stdout, encoding="utf-8")
    finding_types = {
        finding["finding_type"]
        for finding in baseline["findings"]
        if finding["finding_type"] != "zero_findings"
    }
    required_types = {
        "normalized_duplicate_tag_signature",
        "duplicate_configuration",
        "duplicate_variable_path",
        "duplicate_custom_code",
        "single_member_trigger_group",
        "outdated_ua_styled_setup_object",
    }
    missing_types = sorted(required_types - finding_types)
    if missing_types:
        failures.append(
            {
                "check": "baseline_expected_finding_types",
                "missing": missing_types,
                "finding_types": sorted(finding_types),
            }
        )

    piano_duplicate_modules = {
        finding["module_name"]
        for finding in baseline["findings"]
        if {"985", "1006"}.issubset(set(finding.get("object_ids", [])))
    }
    required_duplicate_modules = {
        "duplicate_tag_configurations",
        "normalized_duplicate_tag_signatures",
    }
    missing_duplicate_modules = sorted(required_duplicate_modules - piano_duplicate_modules)
    if missing_duplicate_modules:
        failures.append(
            {
                "check": "piano_consent_duplicate_regression",
                "missing_modules": missing_duplicate_modules,
                "matched_modules": sorted(piano_duplicate_modules),
            }
        )

    real_findings = [
        finding for finding in baseline["findings"] if finding["finding_type"] != "zero_findings"
    ]
    paths["partial_resolution"].write_text(
        json.dumps(
            [
                {
                    "finding_id": real_findings[0]["finding_id"],
                    "resolution_status": "cleanup_operation",
                }
            ]
        ),
        encoding="utf-8",
    )
    paths["full_resolution"].write_text(
        json.dumps(
            [
                {
                    "finding_id": finding["finding_id"],
                    "resolution_status": "cleanup_operation",
                }
                for finding in real_findings
            ]
        ),
        encoding="utf-8",
    )
    reconcile_partial = run(
        "gtm_findings_reconcile.py",
        str(paths["baseline_json"]),
        str(paths["partial_resolution"]),
    )
    reconcile_full = run(
        "gtm_findings_reconcile.py",
        str(paths["baseline_json"]),
        str(paths["full_resolution"]),
    )
    if reconcile_partial.returncode == 0:
        failures.append(
            {
                "check": "reconcile_partial_should_fail",
                "stdout": reconcile_partial.stdout,
                "stderr": reconcile_partial.stderr,
            }
        )
    if reconcile_full.returncode != 0:
        failures.append(
            {
                "check": "reconcile_full_should_pass",
                "stdout": reconcile_full.stdout,
                "stderr": reconcile_full.stderr,
            }
        )


def validate_custom_code(proc: subprocess.CompletedProcess[str], failures: list[dict]) -> None:
    if proc.returncode != 0:
        return
    extracted = json.loads(proc.stdout)
    rows = extracted.get("rows", [])
    has_datalayer_push = any(row.get("dataLayer_pushes_or_writes") for row in rows)
    has_technical_status = all("technical_code_health_status" in row for row in rows)
    if extracted.get("custom_code_count", 0) < 4 or not has_datalayer_push or not has_technical_status:
        failures.append(
            {
                "check": "custom_code_expected_extraction",
                "custom_code_count": extracted.get("custom_code_count"),
                "has_datalayer_push": has_datalayer_push,
                "has_technical_status": has_technical_status,
            }
        )


def validate_semantic_scan(proc: subprocess.CompletedProcess[str], failures: list[dict]) -> None:
    if proc.returncode != 0:
        return
    semantic = json.loads(proc.stdout)
    topics = {row.get("semantic_scan_topic") for row in semantic.get("rows", [])}
    required_topics = {
        "legacy_universal_analytics_setup",
        "fixed_index_ecommerce_logic",
        "business_logic_sanity",
        "custom_code_semantic_review",
    }
    missing_topics = sorted(required_topics - topics)
    if missing_topics:
        failures.append(
            {
                "check": "semantic_source_scan_expected_topics",
                "missing": missing_topics,
                "topics": sorted(topic for topic in topics if topic),
            }
        )


def validate_package_builder(proc: subprocess.CompletedProcess[str], failures: list[dict]) -> None:
    if proc.returncode != 0:
        return
    package = json.loads(proc.stdout)
    expected_files = {
        "source_model",
        "deterministic_findings",
        "technical_code_findings",
        "semantic_findings",
        "manifest",
    }
    missing_files = [
        name
        for name in expected_files
        if not Path(package.get("files", {}).get(name, "")).exists()
    ]
    if package.get("status") != "pass" or missing_files:
        failures.append(
            {
                "check": "package_builder_expected_outputs",
                "status": package.get("status"),
                "missing_files": missing_files,
                "stdout": proc.stdout,
            }
        )


def validate_outputs(
    checks: list[tuple[str, subprocess.CompletedProcess[str]]],
    paths: dict[str, Path],
) -> list[dict]:
    failures: list[dict] = []
    validate_check_exit_codes(checks, failures)

    check_map = dict(checks)
    validate_source_model(check_map["source_model"], failures)
    validate_baseline(check_map["baseline_audit"], paths, failures)
    validate_custom_code(check_map["custom_code_extract"], failures)
    validate_semantic_scan(check_map["semantic_source_scan"], failures)
    validate_package_builder(check_map["package_build"], failures)
    return failures


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        paths = write_test_exports(tmpdir)
        checks = run_checks(paths)
        failures = validate_outputs(checks, paths)

        if failures:
            print(json.dumps({"status": "fail", "failures": failures}, indent=2))
            return 1
        print(json.dumps({"status": "pass", "checks": [name for name, _ in checks]}, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
