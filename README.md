# GTM Container Audit Cleanup

Reusable Codex skill for auditing Google Tag Manager web containers and preparing practical cleanup plans. The skill is centered on cleanup usefulness: it separates deterministic hygiene, semantic business hygiene, and technical custom-code optimization, then reconciles the findings into one user-facing cleanup plan with hidden evidence for agent or analyst continuation.

## What This Repository Contains

- `SKILL.md`: main workflow, intake rules, execution phases, and completion gates.
- `agents/openai.yaml`: Codex skill metadata and default prompt.
- `references/01-skill/`: purpose, users, inputs, outputs, acceptance criteria, and boundaries.
- `references/02-commands/`: validation commands, runtime QA prompts, and forward-test prompts.
- `references/03-rules/`: audit rules, protected pipeline rules, naming rules, workbook rules, operation schema, change-log rules, and mutation safety.
- `scripts/`: deterministic helper scripts for source mapping, baseline findings, custom-code extraction, semantic source scans, finding reconciliation, package gates, and release checks.

The repo is human-facing, so it keeps this README. The installable skill itself remains driven by `SKILL.md`, references, scripts, and metadata.

## Product Vision

The skill should help a web analyst produce a cleanup plan that a real user can understand and act on. It does this through three independent review lenses:

- Deterministic hygiene: find objective GTM cleanup issues such as unused objects, duplicates, outdated Universal Analytics style objects, broken references, naming inconsistencies, trigger architecture issues, and folder organization gaps.
- Semantic business hygiene: verify whether tags, triggers, variables, ecommerce logic, values, formulas, and event routes make business and measurement sense, including impossible logic such as total price being built from unrelated fixed product-index values.
- Technical custom-code optimization: review custom HTML and custom JavaScript variables at a code-health level for risk, simplification, maintainability, security, and performance.

Each lens scans the export or connected container independently. The inventory and dependency map is only a navigation map, not the evidence source. Final output is reconciled so duplicate findings are merged without losing lens-specific evidence.

## Core Workflow

1. Read `SKILL.md` first and ask the required intake questions before assuming container, client, mode, or output format.
2. Build a source model from the GTM export or connected container.
3. Run independent deterministic, semantic, and technical scans against source evidence.
4. Reconcile findings into operation packets with current behavior, problem, expected clean state, exact action, QA, rollback, confidence, blockers, and source finding IDs.
5. Produce a user-facing cleanup plan workbook with concise visible tabs and hidden evidence tabs.
6. Execute cleanup only after explicit approval, in a safe workspace or approved artifact route.
7. After execution, produce a change log with one row per modified element plus summary tabs when useful.

## Quick Start

Ask Codex to use the skill with a GTM export and the desired mode:

```text
Start clean. Use gtm-container-audit-cleanup.
The export is a GTM web-container JSON file in Downloads.
It is a web GTM container.
Mode: audit + cleanup plan only.
Output: XLSX workbook.
Do not edit files or run cleanup until I confirm the intake summary.
```

For approved cleanup, choose the route before any mutation:

- Direct GTM API/MCP cleanup in a new workspace for readable in-place changes.
- Importable JSON only when explicitly chosen and validated.
- Runtime QA when browser, Tag Assistant, network, consent, or vendor-platform proof is required.

## Helper Commands

Run from the repository root.

```powershell
python -B scripts/gtm_source_model.py path\to\container.json --pretty
python -B scripts/gtm_baseline_audit.py path\to\container.json --pretty
python -B scripts/gtm_custom_code_extract.py path\to\container.json --pretty
python -B scripts/gtm_semantic_source_scan.py path\to\container.json --pretty
python -B scripts/gtm_findings_reconcile.py deterministic_findings.json cleanup_resolution.xlsx
python -B scripts/gtm_export_inspect.py path\to\container.json
python -B scripts/gtm_validate_artifact.py artifact.json --mode overwrite
python -B scripts/gtm_diff_operations.py original.json cleaned.json
python -B scripts/gtm_audit_gate_check.py --strict-evidence audit_workbook.xlsx
python -B scripts/gtm_audit_package_check.py container.json audit_workbook.xlsx
python -B scripts/gtm_self_test.py
python -B scripts/check_release.py --tag vYYYY.MM.DD.N
```

## Reference Map

| File | Purpose |
| --- | --- |
| `references/01-skill/purpose.md` | Product vision and analyst posture. |
| `references/01-skill/users-and-questions.md` | Target users and questions the skill resolves. |
| `references/01-skill/inputs-outputs.md` | Supported evidence inputs and deliverable outputs. |
| `references/01-skill/acceptance-criteria.md` | Completion criteria and failure conditions. |
| `references/01-skill/non-goals.md` | Boundaries the skill must not cross. |
| `references/03-rules/protected-audit-pipeline.md` | Protected deterministic, semantic, and technical scan architecture. |
| `references/03-rules/completion-gates.md` | Mandatory workstreams and definition of done. |
| `references/03-rules/execution-assurance.md` | Anti-skip rules, proof artifacts, and validation gates. |
| `references/03-rules/container-json-guide.md` | Export parsing, dependency mapping, and object inventory guidance. |
| `references/03-rules/naming-standardization.md` | Naming scenarios, default policy, and object-level rename evidence. |
| `references/03-rules/operation-schema.md` | Cleanup operation packet schema and technical handoff rules. |
| `references/03-rules/workbook-architecture.md` | Visible cleanup tabs, hidden proof tabs, and workbook validation. |
| `references/03-rules/change-log-template.md` | Post-cleanup change-log schema and coherence rules. |
| `references/02-commands/validation-commands.md` | Local validation and release-check commands. |
| `references/02-commands/forward-test-prompts.md` | Regression prompts for future skill execution tests. |

## Release And Versioning

Use Calendar Versioning:

- First release of a day: `vYYYY.MM.DD`
- Same-day follow-up: `vYYYY.MM.DD.N`
- Release title: `GTM Container Audit Cleanup vYYYY.MM.DD[.N]`

Before pushing a release:

```powershell
python -B scripts/gtm_self_test.py
python -B scripts/check_release.py --tag vYYYY.MM.DD.N --release-notes path\to\release-notes.md
git diff --check
git status --short
```

Release notes should use these sections: `Why This Release Matters`, `What Changed`, `What Users Should Do`, `Validation`, and `Known Limits`.

## Repository Hygiene

Do not commit client-specific GTM exports, audit workbooks, container IDs, domains, emails, screenshots, generated reports, Python cache files, or temporary release artifacts. The repository should contain reusable skill instructions, generic helper scripts, metadata, and human-facing repository documentation only.

## Safety Notes

- Do not delete GTM objects based on age alone.
- Do not rewrite custom HTML by replacing GTM variable references with hardcoded values.
- Do not treat Universal Analytics as the default for ambiguous Google events.
- Do not let semantic or technical checks depend only on summarized inventory output.
- Do not mutate GTM without explicit approval, rollback evidence, and a safe route.
