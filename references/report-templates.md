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
- Change Log Columns
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
Official documentation checked:
Google event classification: GA4/current Google tag default | Explicit UA exceptions
GA4 dataLayer / event payload contracts checked:
Naming convention:
Audit mode: Audit only | Cleanup plan | Approved cleanup | Report generation
Cleanup route strategy:
Cleanup aggressiveness:
JSON import mode / conflict strategy:
Semantic depth: Complete full-container review | Explicitly limited by user
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
GA4 dataLayer format status:
Missing standard events / dataLayer readiness:
Operational maintainability:
Gateway / consolidation opportunity:
Naming standardization status:
Full cleanup coverage:
Cleanup aggressiveness:
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
Impact:
Logical consequence:
Affecting / affected consumers:
Recommendation:
Dependencies:
Semantic role:
Expected payload / output shape:
Consolidation opportunity: None | Exact duplicate | Similar pattern | Gateway candidate | Replaced by approved design
Mutation required: Yes | No
Owner / decision needed:
Approval status: Pending | Approved | Rejected | Deferred | Not required
```

## Operation Table

```text
Change ID:
Aggressiveness: Conservative | Standard | Deep | Transformational
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
GA4 event schema maps completed:
Missing standard events:
DataLayer readiness blockers:
Naming convention and rename blockers:
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
Cleanup aggressiveness:
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
  triggers, trigger groups, vendor pageview patterns, exceptions.
- `07 Semantic Review`: intended role, name-inferred scope, scope confidence,
  clarification needed, consumed variables, expected output shape, actual output
  risk, affected consumers, logical consequence, and context for important
  tags/triggers/variables.
- `08 Official Docs Map`: vendor/platform, implemented event, official source,
  required/recommended parameters, expected data types, observed gap, and whether
  resolution is GTM-only or requires website/dataLayer work.
- `09 GA4 DataLayer Contracts`: GA4 event, official event, trigger event,
  expected event-level parameters, expected item fields, actual dataLayer paths,
  legacy UA path risks, outgoing payload evidence, and resolution type.
- `10 Consolidation Map`: exact duplicates, similar patterns, gateway
  candidates, proposed replacements, and objects that become obsolete.
- `11 Naming Standardization`: proposed convention, object ID, before name,
  after name, layer, reason, dependency risk, uniqueness status, collision
  resolution suffix when needed, and blocker when not renamed.
- `12 Cleanup Roadmap`: phased cleanup plan with dependencies and QA.
- `13 QA Plan`: preview/debug checks, owner, status, evidence, and sign-off.
- `14 Route Strategy`: execution route, import mode, conflict strategy,
  in-place/replacement rationale, old-to-new map, and decommission plan.
- `15 Operations`: structured operation table using the Operation Table fields.
- `16 Change Log`: only when changes were made or approved.
- `17 Deferred Blockers`: objects or patterns not changed, blocker type,
  missing evidence, owner, and recommended next action.
- `18 Completion Ledger`: mandatory workstream, status, affected layer/object
  scope, evidence, blocker, required next evidence, and owner.
- `19 Generated JSON QA`: for importable JSON only; parse status, unique ID
  check, missing references, duplicate configurations, unresolved unused
  objects, GA4/current Google vs UA exception status, naming/logic mismatches,
  residual blockers, import mode, conflict strategy, and import readiness.

Use `Keep`, `Currently unused`, `Consolidation obsolete`,
`Delete candidate`, `Not sure`, `Needs owner validation`, and `Do not delete` as
usage-status values. Avoid plain `Delete` unless deletion was explicitly
approved and verified.

## Change Log Columns

```text
Change ID
Layer
Action
Status
Before name
After name
Object ID(s)
Change category
Plain-language summary
Reason / decision
Functional impact
Consent / privacy impact
QA priority
QA status
Owner
Evidence / notes
```

Use concise `Action` values: Added, Removed, Renamed, Modified, Renamed +
Modified, Replaced, No-op / Documented exception.

When a change log is produced, validate the header before delivery. The file
must contain exactly the columns above in the same order unless the user
explicitly requests a different schema. Do not deliver a shortened operational
log as the change log.

Keep raw JSON out of stakeholder-facing tabs. Put raw normalized traceability
details in a separate technical tab only when the user asks for them.

## Output Format Selection

Follow the user's requested format. If unspecified:

1. Prefer `.xlsx` when the environment can create it reliably.
2. Prefer native Google Sheets only when a Drive/Sheets connector is available
   and the user wants collaborative cloud output.
3. Otherwise create Markdown plus CSV files, one CSV per tab.

Do not assume a cloud destination. Do not include reusable skill examples with
client-specific IDs, names, URLs, or paths.

## Required Closing Question

End audit and cleanup results with:

```text
Would you like me to prepare a change log? I can use Excel if it is available,
Google Sheets if Drive/Sheets is connected, or CSV as a fallback. I can first
propose a client-readable format that tracks every change without making the file
too dense.
```
