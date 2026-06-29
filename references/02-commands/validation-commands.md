# Validation Commands

Use this file to decide which local checks to run and when.

## Release And Repo Checks

Run before committing or releasing:

```powershell
python -m ruff check scripts
python -B scripts/gtm_self_test.py
python scripts/check_release.py --tag vYYYY.MM.DD
python scripts/check_release.py --tag vYYYY.MM.DD.N --release-notes release-notes.md
git diff --check
git status --short
```

If Python is unavailable, run the non-Python checks and state the Python blocker
in the release notes.

## GTM JSON Checks

Run when producing or validating importable JSON:

```powershell
python scripts/gtm_validate_artifact.py artifact.json --mode overwrite
python scripts/gtm_validate_artifact.py artifact.json --original original.json --mode same-container-view
python scripts/gtm_diff_operations.py original.json cleaned.json
```

## Workbook And Audit Gates

Run when delivering an XLSX audit or cleanup plan:

```powershell
python scripts/gtm_audit_gate_check.py --strict-evidence workbook.xlsx
python scripts/gtm_audit_package_check.py export.json workbook.xlsx
```

These gates should verify inventory, dependency mapping, measurement diagnosis,
semantic validation, custom-code review, and cleanup-decision coverage.

## Source Model And Export Inspection

Use for the source-model map and scalable first-pass cleanup facts:

```powershell
python scripts/gtm_audit_package_build.py container.json --out-dir audit-package --pretty
python scripts/gtm_source_model.py container.json --pretty
python scripts/gtm_export_inspect.py container.json
python scripts/gtm_baseline_audit.py container.json --pretty
python scripts/gtm_custom_code_extract.py container.json --pretty
python scripts/gtm_semantic_source_scan.py container.json --pretty
```

The source model is a navigation map, not an evidence substitute. Script output
guides the cleanup lenses, but findings must still be verified against raw
export/API/config/code/runtime evidence.

## Finding Reconciliation

Run when a cleanup plan or workbook resolves deterministic findings:

```powershell
python scripts/gtm_findings_reconcile.py deterministic_baseline.json cleanup_resolution.xlsx
```

Every nonzero deterministic baseline finding must resolve to a cleanup
operation, documented exception, runtime blocker, owner decision needed, or not
applicable with evidence.

Run the stricter operation-packet gate when the three independent scans are
available:

```powershell
python scripts/gtm_findings_reconcile.py deterministic_findings.json reconciled_operations.json --operation-packets --semantic semantic_findings.json --technical technical_code_findings.json
```

Every required deterministic, semantic, and technical source finding must map to
an operation packet with current behavior, problem, expected clean state, exact
action, QA, rollback, confidence, blocker, and source finding IDs. Vague packet
actions such as `review code`, `simplify`, `consolidate`, `harden`, or `fix`
without the exact intended state must fail validation.
