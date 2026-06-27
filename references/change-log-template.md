# Change Log Template

Use this reference when producing a post-cleanup change log or a generated-JSON
review log.

## Contents

- Purpose
- Required Columns
- Coherence Rules
- Output Boundary

## Purpose

The cleanup plan is the decision source. The change log is the execution record.
Do not make the change log a second audit or a place for new analysis.

The change log should contain only what changed, why it changed, impact, QA,
owner/status, and rollback/evidence notes needed for review.

## Required Columns

Use exactly these columns unless the user explicitly requests another schema:

```text
Change ID
Operation ID
Layer
Object ID
Object type
Before name
After name
Action
Before state / value
After state / value
Reason / decision
Functional impact
Consent / privacy impact
Dependencies updated
QA priority
QA method
QA status
Rollback note
Evidence / source
Owner / blocker
Status
```

Recommended action values:

- `Created`
- `Updated`
- `Renamed`
- `Paused`
- `Deleted`
- `Moved folder`
- `Dependency remapped`
- `Documented exception`
- `No-op / Route-limited`

## Coherence Rules

Before delivering both cleanup plan and change log:

- every change-log row maps to a cleanup operation `Change ID`, except explicit
  `No-op / Documented exception` rows;
- object IDs, before names, after names, action, reason/decision, impact, QA,
  owner, and status do not contradict the cleanup plan;
- if semantic checks discover a bad setup after the plan was drafted, update the
  cleanup operation first, then mirror the executed/generated change in the
  change log;
- deferred semantic issues appear as deferred/blocker operations, not as changed
  rows;
- naming, JSON route, and rollback notes match the selected execution route.

## Output Boundary

Do not expose raw JSON, full semantic matrices, raw code/config, validator
traces, scratch reasoning, or full dependency graphs in the change log. Put that
evidence in hidden proof tabs or technical appendices when needed.

The row should be understandable to a business or analytics owner without
reading proof tabs, while still linking to operation/finding IDs for expert
review.
