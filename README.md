# GTM Container Web Analyst

Agent-neutral web analyst skill for Google Tag Manager containers. It is built
to understand the business objective behind tags, validate measurement logic,
detect semantic tracking issues, prepare cleanup plans, support safe cleanup
execution, and guide QA. It is designed for Codex, Claude Code, Gemini, or any
agent that can read Markdown instructions and work with exported GTM container
JSON, GTM API/UI evidence, screenshots, or runtime observations.

## What This Repository Contains

- `SKILL.md`: the main web analyst workflow and operating rules.
- `agents/openai.yaml`: Codex skill metadata and default prompt.
- `references/`: focused audit, cleanup, reporting, QA, and safety playbooks.
- `scripts/`: optional deterministic helpers for GTM JSON inspection, diffs,
  artifact validation, workbook gates, and release checks.

The skill is instruction-first. Python is recommended for repeatable
large-container analysis, but it is not required to read or apply the workflow.

## Core Behavior

- Audit deeply by default; do not downgrade scope unless the user asks for a
  limited review.
- Build an internal business and measurement model before judging meaningful
  tags, triggers, variables, formulas, vendor fields, or cleanup candidates.
- Complete the measurement diagnosis gate before cleanup: business model,
  decision outcome, conversion hierarchy, platform role, and expected data
  contract.
- Complete required D1-D3 review from export, API, UI, source, or code evidence.
  Only D4 runtime proof may be deferred without making the audit incomplete.
- Treat cleanup as one workflow covering naming, unused objects, duplicates,
  consolidation, consent, GA4/current Google tags, media/vendor payloads,
  ecommerce, custom code, server-side caution, folders, templates, and QA.
- Treat cleanup as the consequence of analyst judgment, not as the goal by
  itself.
- Use official Google, CMP, and vendor documentation as the source of truth for
  standard events, payload shape, consent expectations, and validation methods.
- Mutate GTM only after explicit approval, in a dedicated workspace, with a
  rollback export. Never publish or create GTM versions unless explicitly asked.
- Keep user-facing cleanup plans and change logs concise and actionable. Keep
  raw proof matrices, validator traces, and scratch reasoning in backing files
  or hidden workbook tabs.

## Quick Start

Ask the agent to use this skill with the available GTM evidence and context:

```text
Use this skill to audit GTM-XXXXXXX_workspace123.json for https://example.com.
It is a web GTM container for a lead-generation site with OneTrust CMP.
Prepare the audit and cleanup plan only. Do not modify GTM yet.
```

For approved cleanup, choose the route before any operation is generated:

- Direct GTM API/MCP cleanup in a new workspace for readable in-place changes.
- Importable JSON only when that route is explicitly chosen and validated.
- Runtime QA when browser, Tag Assistant, network, consent, or vendor-platform
  proof is required.

## Reference Map

| File | Purpose |
| --- | --- |
| `references/completion-gates.md` | Mandatory workstreams, phase model, and definition of done. |
| `references/execution-assurance.md` | Anti-skip rules, proof artifacts, and validation gates. |
| `references/policy-register.md` | Stable policy IDs for repeatable safety and reporting rules. |
| `references/limited-audit-protocol.md` | Boundaries for explicitly limited audits. |
| `references/audit-rubric.md` | Full audit checklist and semantic review rules. |
| `references/audit-domain-checks.md` | Governance, implementation, security, hygiene, and scenario checks. |
| `references/container-json-guide.md` | GTM export parsing, dependency mapping, and object inventory guidance. |
| `references/source-map.md` | Official documentation sources and source refresh workflow. |
| `references/naming-standardization.md` | Naming hierarchy, local convention adaptation, case rules, uniqueness, and QA. |
| `references/audit-ga4-ecommerce.md` | GA4/current Google tag, dataLayer, ecommerce, and standard variable checks. |
| `references/audit-consent-server.md` | CMP, consent mode, browser-to-server, and server-side caution checks. |
| `references/audit-media-vendors.md` | Media/vendor payload, signal quality, and cross-vendor checks. |
| `references/vendor-playbooks.md` | Vendor-specific setup and payload checks. |
| `references/semantic-model-protocol.md` | Internal business objective and measurement system model. |
| `references/semantic-object-matrix.md` | Depth tiers, D1-D3 proof requirements, and semantic coverage matrix. |
| `references/semantic-logic-checks.md` | Internal graph, formula, context, and payload contradiction checks. |
| `references/summary-quality.md` | Proof-summary levels and user-facing report boundaries. |
| `references/optimization-patterns.md` | Cleanup pattern library from hygiene to strategic redesign. |
| `references/import-json-policy.md` | Same-container merge, View Changes, overwrite, and schema-dependency rules. |
| `references/runtime-qa-templates.md` | Tag Assistant, browser, network, consent, and server-side QA templates. |
| `references/severity-calibration.md` | Severity, priority, and confidence calibration. |
| `references/operation-schema.md` | Cleanup aggressiveness, route, and operation table schema. |
| `references/mutation-playbook.md` | Pre-write and mutation safety rules. |
| `references/report-templates.md` | Audit, cleanup plan, workbook, and change-log schemas. |
| `references/workbook-architecture.md` | Compact visible workbook tabs, hidden proof tabs, and workbook validation. |
| `references/change-log-template.md` | Post-cleanup change-log schema and coherence rules. |
| `references/forward-test-prompts.md` | Regression prompts for future skill execution tests. |

## Helper Commands

```powershell
python scripts/gtm_export_inspect.py path\to\container.json
python scripts/gtm_validate_artifact.py path\to\artifact.json --mode overwrite
python scripts/gtm_diff_operations.py original.json cleaned.json
python scripts/gtm_audit_gate_check.py reconciliation.xlsx
python scripts/gtm_audit_gate_check.py --strict-evidence audit_workbook.xlsx
python scripts/gtm_audit_package_check.py container.json audit_workbook.xlsx
python scripts/gtm_self_test.py
python scripts/check_release.py
```

## Release And Versioning

Use Calendar Versioning for public releases:

- Tag format: `vYYYY.MM.DD` for the first release of a day.
- Same-day follow-up format: `vYYYY.MM.DD.N`, where `N` starts at `1`.
- Release title format: `GTM Container Web Analyst vYYYY.MM.DD[.N]`.
- Release notes should be written for real users, not as an internal commit log.
  Use clear sections: `Why This Release Matters`, `What Changed`,
  `What Users Should Do`, `Validation`, and `Known Limits`.

Historical timestamped tags are kept for traceability. New releases should use
the CalVer pattern above.

Optional release check:

```powershell
python scripts/check_release.py --tag v2026.06.28
python scripts/check_release.py --tag v2026.06.28 --release-notes release-notes.md
```

Recommended release-note shape:

```markdown
## Why This Release Matters

One short paragraph explaining the practical user benefit.

## What Changed

- User-readable change.
- User-readable change.

## What Users Should Do

- Update/install the new version.
- Re-run or regenerate affected outputs when relevant.

## Validation

- Check that passed.
- Check that could not run, with the exact reason.

## Known Limits

- Remaining limitation or `None known`.
```

## Privacy And Repository Hygiene

This repository should contain only reusable skill instructions and generic
helper scripts. Do not commit client-specific GTM exports, audit workbooks,
container IDs, domains, emails, screenshots, or generated reports.

Before release:

```powershell
python scripts/check_release.py --tag vYYYY.MM.DD
git status --short
```

## Safety Notes

- Do not delete objects based on age alone.
- Do not rewrite custom HTML by replacing GTM variable references with hardcoded
  values.
- Do not treat Universal Analytics as the default for ambiguous Google events.
- Do not mark required D3 work as blocked when export/source/code evidence is
  available.
- Do not use same-container JSON imports for broad readable rename reviews; use
  direct GTM API/MCP or a name-preserving review artifact instead.

## Project Status

Public reusable skill package. No license has been selected in this repository;
choose one intentionally before granting external redistribution rights.
