# Execution Assurance

Use this reference for every full audit, cleanup plan, or user-facing workbook.
It turns the skill from prose instructions into a proof-backed execution
contract.

## Contents

- Principle
- Required Proof Artifacts
- User-Facing Separation
- Anti-Failure Rules
- Validation Commands

## Principle

Do not trust the final narrative by itself. The agent must leave evidence that
the audit actually covered the container:

```text
source export/API evidence -> inventory/dependency facts
-> measurement diagnosis -> semantic rows -> findings/operations
-> reconciliation/gate result
```

The user-facing cleanup plan should remain concise, but the backing workbook or
CSV package must prove that high-impact objects, custom code, vendor payloads,
triggers, and variables were actually reviewed.

Required D1-D3 work is never optional in a complete audit. When the source export
or API contains the object configuration, code, trigger filters, variable paths,
lookup rows, or template settings, the agent must inspect them. Only D4 runtime
proof may be blocked by lack of browser, server, CMP, or vendor-platform access.

## Required Proof Artifacts

A completed full audit or cleanup plan must include or generate:

- source export/API identifier and freshness;
- inventory rows for tags, triggers, variables, templates, folders, and enabled
  built-ins;
- dependency evidence for triggers, variables, setup/teardown, folders,
  templates, and custom-code references;
- Measurement Diagnosis rows or fields for meaningful object families, covering
  business model, decision outcome, conversion hierarchy, platform role, and
  expected data contract;
- Semantic Object Matrix rows for all high-impact active tags/variables and all
  reviewed meaningful families;
- Custom Code Semantic Review rows for active, referenced, risky, unused, or
  cleanup-relevant Custom HTML, Custom JavaScript, and custom templates;
- Official Docs Map rows for material vendor/event/CMP families;
- Operations rows for every proposed mutation, no-change exception, deferred
  blocker, or owner decision;
- Workstream Reconciliation rows with zero unresolved count for complete
  deliverables.

If an artifact is not produced because the user asked for a limited/sample audit,
mark the deliverable limited and use `limited-audit-protocol.md`.

## User-Facing Separation

Proof artifacts are for execution assurance and expert review. They should not
make cleanup plans or change logs dense, technical, or hard for end users to
act on.

For end-user cleanup plans, surface only material findings, decisions,
operations, blockers, QA requirements, owner decisions, risk/impact, and the
recommended next step. For post-cleanup change logs, surface only changed
objects, before/after names or values when useful, action, reason, impact, QA
status, owner/status, and rollback/evidence notes.

Keep full semantic rows, D3 proof fields, raw configs, code bodies, dependency
maps, validator traces, and exhaustive evidence in separate backing tabs/files.
The user-facing file must be coherent with those backing artifacts, but it
should not force stakeholders to read internal agent evidence to understand what
to approve or verify.

## Anti-Failure Rules

These behaviors are failed execution, not harmless limitations:

- high-impact objects appear in the export but not in the Semantic Object Matrix;
- meaningful object families move to cleanup operations without measurement
  diagnosis;
- Custom HTML/JS exists but the Custom Code Semantic Review tab is missing or
  says the export review still needs to be done;
- a finding or operation says to review code, variables, triggers, or payloads
  later when that review is needed to judge correctness now;
- a variable/tag is accepted as correct because names look similar, without
  inspecting the source path, formula, output type, and consumers;
- runtime uncertainty is used to skip export-level analysis instead of marking
  only runtime proof as blocked;
- required D3 rows say D3 is blocked even though the export contains the code,
  source path, lookup/regex table, trigger filter, or tag/template parameters;
- D3 evidence is limited to a hash, code length, URL list, or generic static
  scan without explaining inputs, logic, output/side effect, consumer
  expectation, and correctness decision;
- D2/D3 proof uses generic phrases such as `custom code inspected`,
  `configuration reviewed`, `external URL found`, `dataLayer push detected`,
  `no obvious browser side effect`, `see config`, or `see export` instead of a
  semantic summary;
- the cleanup plan or change log exposes raw code, full parameter dumps,
  validator traces, dependency graphs, or normal no-action rows that belong in
  proof tabs or technical appendices;
- a final cleanup plan contains only duplicate/unused/naming hygiene while
  media, ecommerce, consent, server-side, custom-code, or business-logic
  families have not been semantically reviewed.

When a rule fails, deliver `Incomplete / blocked`, list affected objects, and
state the exact evidence needed. Do not present the file as a completed audit.

## Validation Commands

When Python is available and the audit uses an export plus XLSX workbook, run:

```bash
python scripts/gtm_audit_package_check.py export.json audit_workbook.xlsx
```

For any workbook with reconciliation rows, also run:

```bash
python scripts/gtm_audit_gate_check.py --strict-evidence audit_workbook.xlsx
```

If a command fails, fix the missing evidence or label the deliverable
`Incomplete / blocked`. Do not hide failed gates in the limitations section.
