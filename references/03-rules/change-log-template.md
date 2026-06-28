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

Produce a real change log only after direct GTM cleanup, importable JSON
generation, or another concrete cleanup execution has occurred. Before
execution, use `planned change preview`. When the user explicitly asks for a
test artifact "as if cleanup was done", label it `simulated post-cleanup change
log` and mark rows as simulated/not verified.

The change log should contain only what changed, why it changed, impact, QA,
owner/status, and rollback/evidence notes needed for review. It must be
granular enough for the user to understand the applied change without opening
GTM View Changes, while still avoiding raw JSON, code dumps, and proof matrices.

## Required Columns

Use the compact end-user schema by default:

```text
Change ID
Affected object(s)
What changed
Why / impact
QA / rollback
Status
```

`What changed` must include the human-visible before/after behavior, name,
dependency, trigger routing, payload field, variable source, consent setting,
or folder/template relationship that actually changed. Do not fill it with
generic text such as `updated`, `reviewed`, or `see GTM`.

`Why / impact` must include the linked operation ID when available and explain
the business, measurement, consent, privacy, or maintainability consequence.

Use a detailed technical appendix only when the user explicitly asks for it or
when a validator/workflow requires it. In that case, keep the appendix separate
or hidden and make every detailed field distinct. Do not expose a 15-25 column
change log as the default user-facing file.

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

- every change-log row maps to a cleanup operation ID, except explicit
  `No-op / Documented exception` rows;
- object IDs/names, before/after behavior, action, reason/decision, impact,
  QA, owner/blocker, and status do not contradict the cleanup plan;
- if semantic checks discover a bad setup after the plan was drafted, update the
  cleanup operation first, then mirror the executed/generated change in the
  change log;
- deferred semantic issues appear as deferred/blocker operations, not as changed
  rows;
- naming, JSON route, and rollback notes match the selected execution route.
- the row can be understood on its own by an analytics or business owner who
  has not opened GTM View Changes.

## Output Boundary

Do not expose raw JSON, full semantic matrices, raw code/config, validator
traces, scratch reasoning, or full dependency graphs in the change log. Put that
evidence in hidden proof tabs or technical appendices when needed.

The row should be understandable to a business or analytics owner without
reading proof tabs, while still linking to operation/finding IDs for expert
review.
