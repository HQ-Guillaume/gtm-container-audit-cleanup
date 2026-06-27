# Workbook Architecture

Use this reference when producing XLSX cleanup plans, audit workbooks, change
logs with proof tabs, or any stakeholder-facing spreadsheet.

## Contents

- Audience Layers
- Default Visible Tabs
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

A normal cleanup-plan workbook should open on two visible tabs:

- `01 Executive Decision Summary`: overall status, top risks, recommended
  route, cleanup level, safe-now work, blocked work, owner decisions, validation
  status, and next step.
- `02 Cleanup Action Plan`: one operational table that consolidates findings,
  roadmap, operations, deferred blockers, runtime QA, route, and naming into
  actionable rows.

Default `02 Cleanup Action Plan` columns:

- `ID`
- `Phase`
- `Priority`
- `Area`
- `Affected objects`
- `Decision`
- `Reason / impact`
- `Recommended action`
- `Before action requirement`
- `QA method`
- `Route`
- `Status`

Add extra visible tabs only when the user asks, the execution route needs a
separate working tracker, or merging unrelated audiences would make the visible
table harder to use.

## Hidden Proof Tabs

Common hidden proof tabs:

- `03 Inventory - Tags`
- `04 Inventory - Triggers`
- `05 Inventory - Variables`
- `06b Measurement Diagnosis`
- `07 Semantic Object Matrix`
- `07b Custom Code Semantic Review`
- `08 Official Docs Map`
- `08b Vendor Playbook Coverage`
- `09 GA4 DataLayer Contracts` when not material to the decision view
- `10 Consolidation Map`
- `11 Naming Standardization`
- `18 Completion Ledger`
- `18b Workstream Reconciliation`
- `19 Generated JSON QA`

Hidden proof tabs must also be information-clean:

- remove duplicate columns when the schema allows it;
- if a validator requires both fields, make their content distinct;
- use observed-evidence columns for source/input/side effects;
- use judgment columns for expectation, decision, owner question, or QA impact;
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
- keep raw code, raw template fields, hashes, full dependency graphs, and
  validator traces out of user-facing tabs.

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
