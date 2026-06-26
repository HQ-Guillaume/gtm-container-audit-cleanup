#!/usr/bin/env python3
"""Run synthetic regression checks for GTM cleanup helper scripts."""

from __future__ import annotations

import json
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


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        original = tmpdir / "original.json"
        valid = tmpdir / "valid.json"
        missing_builtins = tmpdir / "missing-builtins.json"
        renamed = tmpdir / "renamed.json"

        cv = base_cv()
        original.write_text(json.dumps(export(cv)), encoding="utf-8")
        valid.write_text(json.dumps(export(cv)), encoding="utf-8")

        bad_cv = json.loads(json.dumps(cv))
        bad_cv.pop("builtInVariable")
        missing_builtins.write_text(json.dumps(export(bad_cv)), encoding="utf-8")

        renamed_cv = json.loads(json.dumps(cv))
        renamed_cv["tag"][0]["name"] = "Meta - page_view"
        renamed.write_text(json.dumps(export(renamed_cv)), encoding="utf-8")

        checks = [
            ("valid_view", run("gtm_validate_artifact.py", str(valid), "--original", str(original), "--mode", "same-container-view")),
            ("missing_builtins", run("gtm_validate_artifact.py", str(missing_builtins), "--original", str(original), "--mode", "same-container-view")),
            ("rename_churn", run("gtm_validate_artifact.py", str(renamed), "--original", str(original), "--mode", "same-container-view")),
            ("diff_ops", run("gtm_diff_operations.py", str(original), str(renamed))),
        ]

        failures = []
        for name, proc in checks:
            should_pass = name in {"valid_view", "diff_ops"}
            passed = proc.returncode == 0
            if passed != should_pass:
                failures.append(
                    {
                        "check": name,
                        "returncode": proc.returncode,
                        "stdout": proc.stdout,
                        "stderr": proc.stderr,
                    }
                )

        if failures:
            print(json.dumps({"status": "fail", "failures": failures}, indent=2))
            return 1
        print(json.dumps({"status": "pass", "checks": [name for name, _ in checks]}, indent=2))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
