# GTM Container Audit Cleanup Skill

Agent-neutral workflow for deep Google Tag Manager container audits and cleanup
planning. It is designed for Codex, Claude Code, Gemini, or any agent that can
read Markdown instructions and work with exported GTM container JSON.

## What It Does

- Audits web and server-side GTM containers from exported JSON, API/UI evidence,
  Tag Assistant observations, screenshots, or implementation notes.
- Builds full inventories for tags, triggers, variables, folders, templates,
  consent settings, custom HTML/JavaScript, and dependencies.
- Checks GA4/current Google tag implementations, consent mode, CMP routing,
  server-side tagging, media pixels, custom code, naming, duplicates, and
  consolidation opportunities.
- Uses official Google and vendor documentation as the source of truth for
  standard events, payload shape, consent expectations, and validation methods.
- Adds completion gates, limited-audit boundaries, severity calibration, vendor
  playbooks, semantic modeling, semantic logic checks, optimization patterns,
  execution assurance, centralized policies, runtime QA templates, route-aware
  operation tables, importable JSON checks, and change logs without publishing
  or creating GTM versions.

## Core Principles

- Audit deeply by default.
- Complete required D1-D3 review from export/API/source evidence. Only D4
  runtime proof can be deferred without making the audit incomplete.
- Mutate only after explicit approval.
- Prefer direct GTM API/MCP cleanup in a new workspace for in-place changes.
- Use importable JSON only when that route is intentionally chosen.
- Treat cleanup and optimization as one workflow.
- Apply naming standardization as a mandatory cleanup step unless explicitly
  excluded or blocked by unclear business meaning.
- Keep proposed final names unique within each GTM layer.
- Keep cleanup plans and change logs end-user readable. Put deep proof matrices,
  raw code/config, validator traces, and scratch reasoning in backing files or
  tabs.

## Repository Structure

```text
SKILL.md                         Main agent workflow
agents/openai.yaml               Codex skill metadata
references/                      Audit, source, mutation, reporting guides
scripts/                         Deterministic helper scripts for exports,
                                  diffs, patches, validation, and self-tests
```

Key references:

- `completion-gates.md`: mandatory workstreams, phase model, and definition of
  done.
- `execution-assurance.md`: proof artifacts, anti-skip rules, and validation
  commands for full audits and workbooks.
- `policy-register.md`: stable policy IDs for repeated safety, naming, JSON,
  mutation, and reporting rules.
- `limited-audit-protocol.md`: rules for explicitly limited audits.
- `audit-rubric.md`: full audit checklist and semantic review rules.
- `audit-domain-checks.md`: governance, implementation, security, hygiene, and
  scenario-specific audit checklists.
- `naming-standardization.md`: naming hierarchy, local convention adaptation,
  case rules, uniqueness, and rename QA.
- `audit-ga4-ecommerce.md`: GA4/current Google tag, dataLayer, ecommerce, and
  standard variable checks.
- `audit-consent-server.md`: CMP, consent mode, browser-to-server, and
  server-side caution checks.
- `audit-media-vendors.md`: media/vendor payload, signal quality, and
  cross-vendor checks.
- `vendor-playbooks.md`: vendor-specific payload and setup checks.
- `semantic-model-protocol.md`: internal business objective and measurement
  system model.
- `semantic-object-matrix.md`: depth tiers, D1-D3 proof requirements, and
  semantic coverage matrix.
- `semantic-logic-checks.md`: internal graph, formula, context, and payload
  contradiction checks.
- `summary-quality.md`: semantic proof-summary levels and user-facing cleanup
  plan/change-log boundaries.
- `optimization-patterns.md`: hygiene-to-strategic optimization pattern library.
- `import-json-policy.md`: same-container merge, View Changes, overwrite, and
  schema-dependency rules for importable JSON.
- `runtime-qa-templates.md`: Tag Assistant, browser, network, consent, and
  server-side QA templates.
- `severity-calibration.md`: severity, priority, and confidence calibration.
- `operation-schema.md`: cleanup aggressiveness, route, and operation schema.
- `mutation-playbook.md`: pre-write and mutation safety rules.
- `report-templates.md`: workbook/report/change-log schemas.
- `workbook-architecture.md`: compact visible workbook tabs, hidden proof tabs,
  duplicate-column discipline, and workbook validation.
- `change-log-template.md`: post-cleanup change-log schema and coherence rules.

## Using The Skill

Give the agent:

- GTM export JSON, or GTM API/UI evidence.
- Website domain and business model.
- Web/server-side scope.
- CMP and consent assumptions.
- Whether the task is audit-only, cleanup planning, direct cleanup, or JSON.

Example:

```text
Use this skill to audit GTM-XXXXXXX_workspace123.json for https://example.com.
It is a web GTM container, lead-generation site, OneTrust CMP. Do audit first,
then prepare a cleanup plan. Do not modify GTM yet.
```

For direct cleanup, create a new GTM workspace first and keep a rollback export.
Do not publish unless explicitly requested.

## Helper Scripts

The bundled Python scripts are optional accelerators. They use exported GTM JSON
to inspect inventories, produce diffs, generate same-container patches, and
validate artifacts.

Useful commands:

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

Python is not required to understand or apply the skill instructions, but it is
recommended for repeatable large-container analysis.

## Safety Notes

- Do not publish GTM versions from this skill unless explicitly requested.
- Do not delete objects based on age alone.
- Do not rewrite custom HTML by replacing GTM variable references with hardcoded
  values.
- Do not treat Universal Analytics as the default for ambiguous Google events.
- Do not mark required D3 work as blocked when the export contains code, source
  paths, lookup rows, trigger filters, or tag/template parameters.
- Do not use same-container JSON imports for readable broad rename reviews; use
  direct GTM API/MCP or a name-preserving review artifact instead.

## Status

This repository contains the reusable skill and generic helper scripts only. It
should not contain client-specific exports, audit workbooks, IDs, domains,
emails, or test artifacts.
