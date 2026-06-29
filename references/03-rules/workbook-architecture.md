# Workbook Architecture

Use this reference when producing XLSX cleanup plans, audit workbooks, change
logs with proof tabs, or any stakeholder-facing spreadsheet.

## Contents

- Audience Layers
- Default Visible Tabs
- Change Log Workbooks
- Hidden Proof Tabs
- Column Discipline
- Validation

## Audience Layers

Treat workbook presentation as part of deliverable quality:

- `Visible decision layer`: what the user needs to approve, assign, debug, or QA.
- `Hidden proof layer`: inventories, semantic evidence, official docs maps,
  technical reconciliation, and validator evidence.
- `Traceability`: IDs that connect visible decisions to hidden proof.

Use normal Excel `hidden` sheets for proof tabs. Do not use `veryHidden` unless
the user explicitly asks for locked-down technical evidence. Do not delete proof
tabs merely to simplify the user view; validators and expert reviewers need
them.

## Default Visible Tabs

A normal cleanup-plan workbook should open on two visible tabs and should not
exceed 7-8 total tabs, hidden tabs included, unless the user requests a
technical appendix or the validator explicitly requires an expanded artifact.

- `01 Summary`: overall status, top risks, recommended
  route, cleanup level, safe-now work, blocked work, owner decisions, validation
  status, and next step.
- `02 Cleanup Plan`: one operational table that organizes findings, roadmap,
  operations, deferred blockers, runtime QA, route, and naming into actionable
  rows. Consolidate visually, not semantically: do not hide distinct
  object-level findings inside one broad category row.

Default `02 Cleanup Plan` columns:

- `ID`
- `Level`
- `Area / problem type`
- `Affected object(s)`
- `Problem / evidence`
- `Action / priority / QA`

Add extra visible tabs only when the user asks, the execution route needs a
separate working tracker, or merging unrelated audiences would make the visible
table harder to use.

Use parent/detail rows when several findings share one category or family:

- parent row: `Level = Summary`, ID such as `F001`, family/category scope, and
  the overall action;
- detail rows immediately below: `Level = Detail`, IDs such as `F001.1`,
  `F001.2`, one object or tightly coupled object pair per row, concrete
  evidence, action, QA/status;
- do not use a parent row without detail rows when the underlying issue affects
  multiple objects differently;
- do not merge away a concrete object-level anomaly merely because the visible
  sheet is compact.

Generic hygiene findings may stay as one `Single` row when the evidence,
decision, action, QA, and rollback are identical for the whole set. This
applies to straightforward unused-object deletion candidates, exact duplicate
objects, one naming-convention batch, folder moves, and other mechanical
cleanup buckets. Use detail rows when any object in the bucket has a different
semantic reason, different dependency risk, different owner blocker, or
different recommended action.

Apply `references/03-rules/human-problem-taxonomy.md` before writing visible
rows. `Area / problem type` should combine a human area and a second-level
problem, for example `Media platform tracking / Duplicate firing` or
`Consent & compliance / Consent mismatch`. Do not use internal labels such as
`semantic issue`, `media issue`, `configuration problem`, or `custom-code
review` as the visible problem.

## Change Log Workbooks

For a real post-cleanup change log, use two visible tabs:

- `01 Change Log Summary`: scope, route, counts by action/layer, validation
  result, rollback source, blockers, and next step.
- `02 Change Log Details`: one row per modified object, field, dependency,
  trigger route, variable source, folder move, template/code update, deletion,
  creation, rename, documented exception, or route-limited no-op.

The detail tab must not collapse distinct modifications into a single family
summary. It should still be readable by non-specialists: plain before/after
wording, linked operation ID, impact, QA status, rollback note, and status.
Keep operation packets, raw diffs, validators, and source findings in hidden
proof tabs.

Default visible change-log detail columns:

- `Change ID`
- `Area / object`
- `Change made`
- `Before`
- `After`
- `Reason / QA / status`

Keep full operation IDs, source finding IDs, raw diffs, rollback source,
validator output, and technical proof in hidden tabs when the compact visible
schema would otherwise become too wide.

## Hidden Proof Tabs

Recommended compact hidden/supporting tabs:

- `03 Reconciled Operations`
- `04 D3 Evidence`
- `05 Deterministic Baseline`
- `06 Technical Code Findings`
- `07 Source Model & Dependencies`
- `08 QA & Validation`

`03 Reconciled Operations` is the hidden operation-packet source for the visible
cleanup plan. `04 D3 Evidence` may include the Semantic Object Matrix and
independent semantic source scan. `05 Deterministic Baseline` keeps mechanical
findings and zero-finding proof. `06 Technical Code Findings` keeps custom-code
fact extraction and technical code review fields. `07 Source Model &
Dependencies` keeps the navigation map, unresolved edges, consumers, and
dependency proof.

Split these tabs only when the user asks for a technical workbook, a validator
requires the older schema, or a container is too large for readable compact
tabs. Even hidden tabs must remain human-readable when unhidden.

Hidden proof tabs must also be information-clean:

- remove duplicate columns when the schema allows it;
- if a validator requires both fields, make their content distinct;
- use observed-evidence columns for source/input/side effects;
- use judgment columns for expectation, decision, owner question, or QA impact;
- keep deterministic baseline output, custom-code technical review output, and
  independent semantic source scan output separate until the reconciliation
  rows explain how they combine into visible cleanup actions;
- ensure every visible cleanup row links to an operation packet, except pure
  summary rows whose immediate detail rows have packets;
- keep `current_behavior`, `expected_clean_state`, `exact_proposed_action`,
  `qa_steps`, `rollback`, `blocker`, and `source_finding_ids` in the hidden
  operation packet even if the visible row uses shorter wording;
- hide constant, blank, validator-only, or raw-proof columns when humans may
  unhide the sheet;
- keep required reconciliation fields even when counts/statuses naturally match,
  but hide duplicate proof columns and add a compact phase summary when useful.

## Column Discipline

Visible columns must earn their place for real human use. Keep a column visible
only when it supports approval, debugging, assignment, QA, impact understanding,
or next action.

Before delivery:

- scan visible and hidden tabs for exact duplicate column contents;
- merge columns that answer the same human question;
- hide or remove blank and constant columns unless a validator requires them;
- keep operation IDs and finding IDs visible when they trace to proof rows;
- keep parent/detail IDs visible when a summary row represents several object
  findings;
- keep raw code, raw template fields, hashes, full dependency graphs, and
  validator traces out of user-facing tabs.
- keep visible and hidden tabs around 5-6 useful columns by default. If more
  columns are required for a technical appendix, hide or move the appendix out
  of the main user-facing workbook.
- consolidate columns that answer the same question. For example, merge D3
  source, logic, output, consumer, and decision fields into `Literal behavior`,
  `Consumer / context`, `Analyst judgment`, `Cleanup implication`, and
  `Evidence / QA blocker`.

## Validation

For completed full-audit or cleanup-plan workbooks, run when Python is
available:

```powershell
python scripts/gtm_audit_gate_check.py --strict-evidence workbook.xlsx
python scripts/gtm_audit_package_check.py export.json workbook.xlsx
```

If either gate fails, label the deliverable `Incomplete / blocked` and list the
failed workstream, affected objects, blocker, risk, required evidence, and next
step.
