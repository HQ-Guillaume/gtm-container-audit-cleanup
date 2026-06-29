# Report Templates

Use these templates to keep audits, cleanup plans, and handoffs
consistent across containers, clients, and agents.

## Contents

- Audit Header
- Executive Summary
- Finding Table
- Inventory Summary
- Cleanup Roadmap
- Cleanup Plan
- Final Handoff
- Spreadsheet-Friendly Tabs
- Workbook And Summary Routing
- Change Log Columns
- Cleanup Plan And Change Log Coherence
- Output Format Selection
- Required Closing Question

## Audit Header

```text
Client / property:
Website / app scope:
GTM account / container:
Workspace or version:
Audit date:
Auditor / agent:
Evidence sources:
Evidence freshness:
Scope boundary:
Not a full-container audit: Yes | No
Official documentation checked:
Vendor playbooks checked:
Google event classification: GA4/current Google tag default | Explicit UA exceptions
GA4 dataLayer / event payload contracts checked:
Naming convention:
Audit mode: Audit only | Cleanup plan | Approved cleanup | Report generation
Cleanup route strategy:
Cleanup aggressiveness: recommended default plus selectable options per material step
JSON import mode / conflict strategy:
Semantic depth: Complete full-container review | Explicitly limited by user
Semantic validation status:
Custom-code semantic review status:
Runtime QA status:
Severity calibration basis:
Completion gate result: Complete | Incomplete / blocked
Reconciliation status:
Measurement diagnosis status:
Limitations:
Completion ledger status:
```

## Executive Summary

```text
Overall health:
Top risks:
Highest-priority fixes:
Consent/privacy status:
GA4 / conversion tracking status:
Google/UA exception status:
Critical ecommerce variable issues:
Official vendor documentation status:
Vendor playbook coverage:
Measurement diagnosis status:
Runtime QA status:
GA4 dataLayer format status:
Missing standard events / dataLayer readiness:
Operational maintainability:
Gateway / consolidation opportunity:
Naming standardization status:
Full cleanup coverage:
Cleanup aggressiveness: recommended default and selectable alternatives by operation
Reconciliation status:
Unresolved workstream/object-family count:
Skipped / deferred mandatory workstreams:
Recommended next step:
```

## Finding Table

```text
Finding ID:
Category:
Layer: Governance | Implementation | Security | Architecture | Tag | Trigger | Variable | Consent | GA4 | Server-side GTM | Vendor pixel | Google Ads | Naming | Payload
Object name / ID:
Status: Correct | Issue | Needs improvement | Not applicable | More info needed
Severity: Critical | High | Medium | Low | Info
Priority: P0 Now | P1 This sprint | P2 Planned cleanup | P3 Backlog | Decision needed
Confidence: High | Medium | Low
Evidence:
Official documentation basis:
Vendor playbook basis:
Impact:
Logical consequence:
Affecting / affected consumers:
Recommendation:
Dependencies:
Semantic role:
Expected payload / output shape:
Runtime QA required: Yes | No
Consolidation opportunity: None | Exact duplicate | Similar pattern | Gateway candidate | Replaced by approved design
Mutation required: Yes | No
Owner / decision needed:
Approval status: Pending | Approved | Rejected | Deferred | Not required
```

## Operation Table

```text
Change ID:
Recommended aggressiveness: Conservative | Standard | Deep | Transformational
Aggressiveness options: Conservative includes/excludes/risk/QA; Standard includes/excludes/risk/QA; Deep includes/excludes/risk/QA; Transformational includes/excludes/risk/QA; blocked levels with reason
Route: Direct GTM/MCP/API | Same-container JSON | Overwrite JSON | New-container JSON | Report-only
Layer:
Action: Add | Update | Rename | Delete | Replace | Flatten | Consolidate | Defer | Document exception
Object ID / path:
Before name:
After name:
Semantic role:
Reason:
Official documentation basis:
Dependencies:
Risk:
QA method:
Rollback:
Status: Proposed | Approved | Applied | Verified | Deferred | Rejected
Blocker:
```

## Custom Code Semantic Review Table

```text
Layer: Tag | Variable | Template
Object ID:
Object name:
Type:
Role category: Vendor loader | Event dispatcher | Listener | DOM helper | Storage/cookie helper | Consent/CMP UI | Identity helper | Payload transformer | Template | Obsolete/paused | Other
Purpose:
Export review completed: Yes | No | Not applicable
Trigger / consumer context:
Consent assumption:
External URLs / storage / cookie / DOM / dataLayer side effects:
Variable references:
Expected output / side effect:
Runtime risks:
Official documentation basis:
Semantic status: Keep | Fix | Consolidate | Delete candidate | More info needed | Not applicable
Cleanup recommendation:
Recommended aggressiveness:
Aggressiveness options:
QA method:
Blocker:
```

Use `summary-quality.md` for Custom Code Semantic Review wording. The
`Expected output / side effect` and runtime-risk fields must explain what the
object reads, returns, loads, pushes, mutates, or calls, plus the judgment. Do
not use generic phrases such as `custom code inspected`, `external URL found`,
`dataLayer push detected`, or `no obvious browser side effect` as the main
summary.

## Workstream Reconciliation Table

Use this table to prove that audit scope, measurement diagnosis, semantic
validation, and cleanup decisions reconcile. A completed audit or cleanup plan
must not have unresolved rows.

```text
Workstream:
Object family:
Total source count:
Inventoried count:
Dependency-mapped count:
Measurement-diagnosed count:
Semantically validated count:
Cleanup-decision count:
Deferred count:
Not applicable count:
User-excluded count:
Unresolved count:
Inventory phase status: Done | Deferred | Not applicable | User-excluded
Dependency phase status: Done | Deferred | Not applicable | User-excluded
Measurement diagnosis phase status: Done | Deferred | Not applicable | User-excluded
Semantic validation phase status: Done | Deferred | Not applicable | User-excluded
Cleanup decision phase status: Done | Deferred | Not applicable | User-excluded
Report reconciliation phase status: Done | Deferred | Not applicable | User-excluded
Reconciliation formula status:
Failed gate:
Affected objects:
Blocker:
Risk:
Required next evidence:
Owner:
Next action:
```

## Vendor Playbook Coverage Table

```text
Vendor / family:
Object names / IDs:
Official source checked:
Playbook checks applied:
Base / loader status:
Event / payload status:
Consent status:
Ecommerce/dataLayer status:
Runtime QA status:
Findings linked:
Deferred evidence:
Confidence:
```

## Runtime QA Plan Table

```text
QA ID:
URL / page type:
Action / event:
Consent state:
Expected GTM event:
Expected tag(s):
Expected network request(s):
Expected payload fields:
Vendor/platform validation:
Evidence needed:
Owner:
Status: Planned | Pass | Fail | Blocked | Not applicable
Blocker:
```

## Inventory Summary

```text
Tags:
Triggers:
Variables:
Folders:
Templates:
Workspaces / versions reviewed:
Server-side clients/tags/transformations:
Gateway candidates:
Currently unused candidates:
Consolidation-obsolete candidates:
Standard ecommerce variables checked:
Official vendor/event docs checked:
Vendor playbooks checked:
GA4 event schema maps completed:
Missing standard events:
DataLayer readiness blockers:
Naming convention and rename blockers:
Meaningful object families semantically validated:
Meaningful object families measurement-diagnosed:
Object families only inventoried:
Custom code semantic review:
Reconciliation counts:
Unresolved count:
Completion ledger:
Tag Assistant / browser checks:
Notes:
```

## Cleanup Roadmap

```text
Phase:
Goal:
Included findings:
Operations:
Dependencies:
Risk:
Verification:
Owner decision needed:
Changed layers:
Deferred layers and blockers:
```

Recommended phases:

1. Consent/privacy and broken measurement fixes.
2. Revenue/GA4 ecommerce and conversion accuracy.
3. Gateway/consolidation design for similar tags, triggers, and variables.
4. Duplicate/redundant object cleanup after consolidation impact is known.
5. Custom code and payload simplification.
6. Naming, folders, and documentation.

Apply naming standardization in phase 6 only after semantic fixes,
consolidation, and deletion decisions are stable. If the user asks only for
audit or planning, include the proposed naming convention and rename blockers.

## Cleanup Plan

```text
Workspace:
Execution route: Direct GTM/MCP/API cleanup | Importable GTM container JSON
Route-specific cleanup strategy:
JSON import mode / conflict strategy:
Cleanup depth: Full container | User-limited scope
Scope:
Pre-write snapshot/export:
Approved operations:
Skipped operations:
Cleanup aggressiveness: recommended default plus selectable alternatives by operation
Changed by layer:
Deferred by layer:
Old-to-new replacement map:
Post-QA decommission plan:
Deferred blocker evidence needed:
Naming convention:
Before/after rename map:
Batching strategy:
Rollback path:
Verification checks:
Generated JSON self-QA:
Completion gate result:
Failed gates:
Reconciliation counts:
Runtime QA plan:
Stop conditions:
Completion ledger:
Open questions:
```

## Final Handoff

```text
Completed:
Verified:
Intentional exceptions:
Deferred / blocked:
Execution route and cleanup strategy:
JSON import mode / conflict strategy:
Changed by layer:
Deferred by layer and blocker:
Naming convention applied:
Rename map produced:
Replacement/decommission map:
Generated JSON self-QA status:
Completion ledger complete:
Completion gate result:
Failed gates:
Reconciliation counts:
Open organization-decision items:
Files or exports produced:
Importable GTM JSON path:
Rollback source:
Publish/version status: Not published
Recommended next step:
```

## Next-Step Requirement

Every completed audit, cleanup phase, importable JSON
delivery, QA pass, and final handoff must include `Recommended next step`.
Use a concrete action, not a generic closing sentence:

- If audit-only is complete, recommend validation decisions, cleanup route
  selection, runtime QA, or missing evidence collection.
- If a cleanup phase is complete, recommend the next phase and whether it
  needs user approval.
- If cleanup is complete, recommend QA, change-log generation, stakeholder
  review, import, or publish-readiness review.
- If blocked, name the missing evidence, owner decision, access, or legal/CMP
  validation needed.

## Spreadsheet-Friendly Tabs

Default stakeholder workbooks should use compact tabs, usually no more than
7-8 total tabs and 5-6 decision columns per tab. Use expanded technical tabs
only when the user asks for them or a validation workflow requires them.

Recommended compact audit/cleanup plan tabs:

- `01 Summary`
- `02 Cleanup Plan`
- `03 D3 Evidence`
- `04 Source Model & Dependencies`
- `05 Synergy & Consolidation`
- `06 QA & Blockers`
- `07 References & Validation`

Recommended `02 Cleanup Plan` columns:

```text
ID:
Level: Summary | Detail | Single
Area / problem type:
Affected object(s):
Problem / evidence:
Action / priority / QA:
```

Use `Summary` rows only as visual parents. Put concrete object findings
directly beneath them as `Detail` rows with IDs such as `F001.1`, `F001.2`, and
so on. Use `Single` when the row is already object-specific. Do not collapse
distinct object-level findings into a family row without detail rows.

Use one `Single` row for generic hygiene batches when the whole batch has the
same evidence, action, QA, and rollback: unused variables/triggers/tags, exact
duplicates, naming convention, folder organization, and other mechanical
cleanup. Split into detail rows as soon as the business logic, dependency risk,
or recommended action differs by object.

Before writing visible rows, use `human-problem-taxonomy.md` to translate
operation packets into human problem rows. `Area / problem type` should be
specific enough for a web analyst to scan, such as `Event firing logic /
Over-firing`, `Media platform tracking / Wrong product scope`, or `Consent &
compliance / Consent mismatch`. Do not write rows whose visible problem is only
`semantic issue`, `configuration issue`, `tracking issue`, or another internal
scan label.

Recommended `03 D3 Evidence` columns:

```text
Object:
Literal behavior:
Consumer / context:
Analyst judgment:
Cleanup implication:
Evidence / QA blocker:
```

Use `03 D3 Evidence` or a hidden support tab to keep independent semantic
source scan rows separate from deterministic baseline rows until reconciliation.
Use `04 Source Model & Dependencies` for the navigation map and unresolved
edges; put custom-code technical review fields in hidden proof when the visible
plan only needs the resulting action, QA, or blocker.

Use the larger legacy tab list below only for technical appendices, validator
fixtures, or explicit user requests.

When creating a workbook or CSV set, use these stable tabs:

- `00 Method`: scope, source exports/workspaces, evidence freshness, analysis
  method, ignored metadata fields, confidence rules, limitations.
- `01 Executive Summary`: counts by layer/category/severity/status/priority and
  top recommended actions.
- `02 Findings`: one row per audit finding using the Finding Table columns.
- `03 Inventory - Tags`: name, ID, type, folder, firing triggers, blocking
  triggers, consent, last edited when known, usage status, notes.
- `04 Inventory - Triggers`: name, ID, type, event/filter summary, connected
  tags, folder, usage status, notes.
- `05 Inventory - Variables`: name, ID, type, key/config summary, consumers,
  folder, usage status, notes.
- `06 Consent & Routing`: CMP events, consent mode defaults/updates, blocking
  triggers, trigger groups, vendor pageview patterns, client-to-server consent
  forwarding, server-side validation blockers, exceptions.
- `06b Measurement Diagnosis`: business model, decision outcome, conversion
  hierarchy, vendor/platform role, expected event/payload contract,
  intent blockers, linked semantic rows, and linked operations.
- `07 Semantic Object Matrix`: in a full audit, one row per tag, trigger,
  variable, custom template, and referenced configuration branch; in a limited
  audit, one row per scoped object or reviewed family:
  object ID/name/layer, vendor/family, inferred business role, decision outcome,
  conversion hierarchy, platform role, expected data contract, depth required and
  completed, trigger-context status, configuration/code logic status,
  source/output status, consent/server status, evidence level, semantic status,
  confidence, linked finding/operation, runtime QA, and blocker/next evidence.
  If depth required includes `D3`, include D3 inputs/sources, D3 logic summary,
  D3 output or side effect, D3 consumer expectation, and D3 correctness
  decision. Missing D3 proof means incomplete audit, not deferred cleanup.
  Keep raw parameter dumps out of this tab unless they are needed as proof.
- `07a Independent Semantic Source Scan`: direct source scan rows that seed
  semantic coverage and prove the semantic layer did not rely only on
  deterministic baseline summaries. May be folded into `07 Semantic Object
  Matrix` in compact workbooks if the rows remain traceable.
- `07b Custom Code Semantic Review`: object-level Custom HTML, Custom
  JavaScript, and custom-template purpose, role category, export review status,
  side effects, consent assumption, consumers, technical code health/security/
  optimization signals, risk, semantic status, cleanup recommendation,
  aggressiveness options, QA method, and blocker.
- `08 Official Docs Map`: vendor/platform, implemented event, official source,
  required/recommended parameters, expected data types, observed gap, and whether
  resolution is GTM-only or requires website/dataLayer work.
- `08b Vendor Playbook Coverage`: vendor/family, object IDs, official sources,
  playbook checks applied, base/event/payload/consent/ecommerce status, runtime
  QA status, linked findings, deferred evidence, and confidence.
- `09 GA4 DataLayer Contracts`: GA4 event, official event, trigger event,
  expected event-level parameters, expected item fields, actual dataLayer paths,
  legacy UA path risks, outgoing payload evidence, and resolution type.
- `10 Consolidation Map`: exact duplicates, similar patterns, gateway
  candidates, proposed replacements, and objects that become obsolete.
- `11 Naming Standardization`: proposed convention, object ID, before name,
  after name, layer, reason, dependency risk, uniqueness status, collision
  resolution suffix when needed, and blocker when not renamed.
- `12 Cleanup Roadmap`: phased cleanup plan with dependencies, QA,
  recommended aggressiveness, and selectable aggressiveness alternatives.
- `13 Runtime QA Plan`: Tag Assistant/browser/network/vendor-platform checks,
  consent state, URL/page type, expected GTM event, expected tags, expected
  network requests, expected payload fields, owner, status, evidence, and
  blocker.
- `14 Route Strategy`: execution route, import mode, conflict strategy,
  in-place/replacement rationale, old-to-new map, and decommission plan.
- `15 Operations`: structured operation table using the Operation Table fields,
  including recommended aggressiveness and user-selectable alternatives.
- `16 Change Log`: only when changes were made or approved.
- `17 Deferred Blockers`: objects or patterns not changed, blocker type,
  missing evidence, owner, and recommended next action.
- `18 Completion Ledger`: mandatory workstream, overall status, inventory phase
  status, dependency phase status, measurement diagnosis phase status, semantic
  validation phase status, cleanup decision phase status, report reconciliation
  phase status, affected
  layer/object scope, evidence, blocker, required next evidence, owner, and
  next action.
- `18b Workstream Reconciliation`: workstream/object family, total source count,
  inventoried count, dependency-mapped count, measurement-diagnosed count,
  semantically validated count, cleanup-decision count, deferred count, not
  applicable count, user-excluded
  count, unresolved count, reconciliation formula status, failed gate, affected
  objects, blocker, risk, required next evidence, owner, and next action.
- `19 Generated JSON QA`: for importable JSON only; parse status, unique ID
  check, missing references, duplicate configurations, unresolved unused
  objects, GA4/current Google vs UA exception status, naming/logic mismatches,
  residual blockers, import mode, conflict strategy, and import readiness.

Use `Keep`, `Currently unused`, `Consolidation obsolete`,
`Delete candidate`, `Not sure`, `Needs owner validation`, and `Do not delete` as
usage-status values. Avoid plain `Delete` unless deletion was explicitly
approved and verified.

## Workbook And Summary Routing

For XLSX cleanup plans, use `workbook-architecture.md`. It defines the default
two-tab visible decision layer, hidden proof tabs, duplicate-column discipline,
and workbook validation commands.

For semantic summary wording and the user-facing boundary, use
`summary-quality.md`. Cleanup plans should judge configuration and expose
findings, blockers, operations, QA, owner decisions, and next steps; proof tabs
hold raw D1/D2/D3 evidence.

## Change Log Columns

Use `change-log-template.md` for the required change-log columns, action
values, coherence rules, and output boundary. The change log must explain the
human-visible before/after behavior of each applied or generated change well
enough that an analytics owner can review what happened without opening GTM
View Changes.

## Cleanup Plan And Change Log Coherence

The cleanup plan is the decision source and the change log is the execution
record. Before delivering both files, apply the coherence checks in
`change-log-template.md`.

Do not let the two files drift: operation IDs, object IDs, before/after names,
reason, functional impact, QA method, blocker, and status must tell the same
story. If execution discovers new facts, update the cleanup plan first and then
mirror the final change-log row.

## Output Format Selection

Follow the user's requested format. If unspecified:

1. Prefer `.xlsx` when the environment can create it reliably.
2. Prefer native Google Sheets only when a Drive/Sheets connector is available
   and the user wants collaborative cloud output.
3. Otherwise create Markdown plus CSV files, one CSV per tab.

Do not assume a cloud destination. Do not include reusable skill examples with
client-specific IDs, names, URLs, or paths.

When both an audit/cleanup plan and a change log are requested, produce separate
deliverables by default because they belong to different lifecycle moments:

- an audit/cleanup plan workbook or report after the audit, for decisions and
  proof;
- a standalone change log workbook or CSV only after cleanup execution or
  generated cleanup artifact creation.

Only combine them when the user explicitly requests one file. If combined, the
change-log tab must still follow `change-log-template.md` exactly and the
workbook must open on the decision layer, not on proof or raw-change tabs.
If no cleanup was executed, do not call the artifact a real change log. Use
`planned change preview` or `simulated post-cleanup change log`, depending on
the user's request.

## Required Closing Question

End audit and cleanup-plan results with a concrete next execution decision, for
example:

```text
Recommended next step: approve the cleanup route. I can either create a new GTM
workspace and apply the approved operations directly, or prepare an importable
JSON if you prefer manual import. A real change log will be produced after
cleanup execution.
```

Offer a planned change preview before execution only when it helps approval.
Do not ask to create a real change log until cleanup was executed or a generated
cleanup artifact was produced.
