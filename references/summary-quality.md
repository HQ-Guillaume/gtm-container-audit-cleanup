# Summary Quality

Use this reference whenever producing Semantic Object Matrix rows, Custom Code
Semantic Review rows, cleanup plans, change logs, executive summaries, or
handoffs. It prevents two opposite failures: generic audit proof that proves
nothing, and user-facing reports that expose too much internal detail.

## Contents

- Summary Levels
- Proof Summary Pattern
- User-Facing Boundary
- Generic Summary Anti-Patterns
- Examples

## Summary Levels

Use the smallest summary level that supports the audience and decision.

| Level | Use for | Must include |
| --- | --- | --- |
| L1 Category | Inventory rows, repeated low-risk families, normal helpers. | Object role and source family. |
| L2 Logic | Semantic Object Matrix and Custom Code Review proof. | Source/input, action/formula/config, output or side effect, consumer expectation. |
| L3 Judgment | Findings, operations, blockers, cleanup plan rows. | What is wrong or changing, why it matters, recommended action, QA/blocker. |

Do not use L1 where D2/D3 is required. A D3 row needs L2 proof plus an L3
correctness decision when the object drives a finding, operation, or blocker.

## Proof Summary Pattern

For proof tabs, write compact semantic summaries with this shape:

```text
category -> source/input -> logic/action -> output/side effect -> judgment
```

Examples of valid proof summaries:

- `Consent helper. Reads cmpConsentPurposes and returns granted when purpose
  ,1, is present, otherwise denied. Issue: this duplicates Analytics Storage
  logic and needs purpose mapping confirmation.`
- `Event bridge/listener. Listens to window message events, accepts
  cta_tracking payloads, and pushes the payload to dataLayer. Issue: origin and
  schema are not guarded.`
- `DataLayer source variable. Reads article_id and is consumed by Piano
  page.display tags; coherent if article_id is present on article page events.`

## User-Facing Boundary

The cleanup plan is the decision source. The semantic matrix is the proof
source. The change log is the execution record.

Cleanup plans and change logs should include only:

- issue or opportunity;
- affected object names/IDs;
- business, data-quality, privacy, performance, or maintenance impact;
- recommended action or completed action;
- risk/severity and priority;
- practical QA/debug method;
- owner decision or blocker;
- status and next action.

Keep these in proof tabs or technical appendices, not in the main cleanup plan
or change log:

- raw code bodies, raw template fields, full parameter dumps, hash/signature
  values, full dependency graphs, validator traces, scratch reasoning, normal
  object rows with no action, and full D1/D2/D3 evidence.

The user-facing row should be understandable without reading the proof tabs,
but it should link to finding/operation IDs when detailed evidence exists.

For XLSX workbooks, keep proof tabs in the same file but hide them with the
normal Excel `hidden` state when they are not part of the human decision view.
Do not use `veryHidden` unless the user explicitly asks for locked-down
technical evidence. Hidden proof tabs remain available through Excel's Unhide
command and to validators or future agents.

Use visible workbook tabs for decision flow, not proof completeness. A normal
cleanup-plan workbook should open on two concise tabs: `Executive Decision
Summary` and `Cleanup Action Plan`. Merge findings, roadmap, operations,
deferred blockers, runtime QA, route, and naming into the action plan unless the
user explicitly wants separate working tabs. Put inventories, semantic
matrices, custom-code proof, official documentation maps, full consolidation
maps, full rename maps, completion ledgers, and reconciliation tables in hidden
proof tabs.

Before delivery, review columns for information value:

- hide or remove blank columns from user-facing tabs;
- hide constant columns when the value can be summarized once;
- hide exact duplicate columns unless a validator requires both in a proof tab;
- in hidden proof tabs, do not leave two validator-required columns with the
  same text. Keep the schema, but make the content distinct: one field should
  record observed evidence, while the other records judgment, expectation,
  owner decision, or QA implication;
- merge columns that answer the same human question, such as side effect and
  expected output, in user-facing views;
- keep IDs, operation IDs, owner, status, QA, blocker, and next action visible
  when they are needed for approval or debugging.

## Generic Summary Anti-Patterns

These phrases are not valid semantic proof when used alone or as the main
summary:

- `custom code inspected`
- `configuration reviewed`
- `code scanned`
- `external URL found`
- `dataLayer push detected`
- `no obvious browser side effect`
- `no issue found`
- `see config`
- `see export`
- `static scan completed`
- `reviewed manually`

These are evidence signals, not summaries. Replace them with the object role,
source/input, logic/action, output or side effect, and judgment.

## Examples

### Custom JavaScript Consent Helper

Too generic:

```text
custom code inspected; no external URL or obvious browser side effect detected
```

Better:

```text
Consent helper. Reads cmpConsentPurposes and returns granted when purpose ,1,
is present, otherwise denied. Issue: this helper is also used for
analytics_storage, so consentmanager purpose mapping must be confirmed.
```

### Vendor Loader

Too detailed for cleanup plan:

```text
The tag creates script elements, sets type=module and nomodule, inserts them
before the first script tag, and loads marfeel-sdk.js and marfeel-sdk.es5.js
with accountId 2152.
```

Better for cleanup plan:

```text
Three Marfeel tags load the same SDK account with different route rules. Run
route QA, then consolidate or document mutually exclusive loaders to prevent
duplicate SDK initialization.
```

### Trigger

Too generic:

```text
event cmpEvent with filters
```

Better:

```text
Consent trigger. Fires on cmpEvent after the user choice is known and requires
vendor s1498 in the CMP vendor list. Treat it as a Google Advertising consent
gate until the vendor ID owner confirms the mapping.
```

### Change Log

Too much:

```text
Updated variable 647 JavaScript from function() { var PurposesGroup = ... } to
function() { ... }; D3 source logic was inspected...
```

Better:

```text
Modified Analytics Storage helper so it uses the confirmed analytics consent
purpose instead of the advertising-purpose rule. QA: Tag Assistant consent mode
accept/refuse tests passed.
```
