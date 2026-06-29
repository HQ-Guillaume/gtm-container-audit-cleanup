# Human Problem Taxonomy

Use this reference when compiling cleanup plans, planned change previews, and
post-cleanup change logs. It turns reconciled operation packets into rows that
web analysts, marketing teams, and analytics owners can understand.

## Contents

- Position In The Pipeline
- Area Taxonomy
- Problem Type Taxonomy
- Row Construction Rules
- Grouping Rules
- Wording Rules
- Cleanup Plan Shape
- Change Log Shape
- Quality Gates
- Examples

## Position In The Pipeline

Add this layer after the three scans and reconciliation:

```text
raw evidence
-> source model navigation map
-> deterministic_findings.json
-> semantic_findings.json
-> technical_code_findings.json
-> reconciled_operations.json
-> human_problem_rows
-> cleanup plan or change log
```

The human problem layer is a translation layer, not an evidence layer. It must
not invent a finding, remove a finding, downgrade a finding, or merge findings
only because they share a vendor, tag type, or technical label. Every visible
row must link to an operation ID and source finding IDs in proof tabs.

## Area Taxonomy

Use these human-facing areas by default. Add site-specific areas only when the
business context requires them.

- `Stack & architecture`
- `GTM hygiene`
- `Tracking plan / dataLayer`
- `Event firing logic`
- `Ecommerce payload quality`
- `Media platform tracking`
- `Consent & compliance`
- `Server-side tracking`
- `Data quality / reporting`
- `Web performance`
- `Governance / ownership`

## Problem Type Taxonomy

Use a second-level problem type so rows are not vague. Prefer these values:

- `Missing tracking`
- `Wrong trigger timing`
- `Over-firing`
- `Under-firing`
- `Duplicate firing`
- `Wrong product, market, or page scope`
- `Incomplete payload`
- `Wrong data format`
- `Wrong value or formula logic`
- `Obsolete or legacy setup`
- `Unclear business purpose`
- `Consent mismatch`
- `Server-side routing unclear`
- `Performance overhead`
- `Naming or ownership unclear`
- `Generic hygiene batch`

Avoid rows whose problem type is only `Semantic issue`, `Media issue`,
`Configuration problem`, `Tracking issue`, `Tag issue`, `Variable issue`, or
`Custom code issue`. These are internal categories, not human problems.

## Row Construction Rules

Each visible cleanup-plan row must answer:

- what business or measurement behavior is wrong or risky;
- which object, family, vendor, event, scope, or dataLayer field is affected;
- one concrete evidence example from the export, API, runtime, or owner blocker;
- what should be true after cleanup;
- what action, QA, or owner decision is needed.

Use cautious wording when evidence is inferential:

- `tag name suggests IGGI scope` instead of `this is definitely IGGI-only`;
- `risk of duplicate conversions` instead of `campaign data is wrong` unless
  runtime/vendor evidence proves duplication;
- `runtime QA required before mutation` only after D1-D3 evidence is complete.

## Grouping Rules

Group rows only when the root cause, expected clean state, action, QA, and
rollback are the same.

Allowed grouped rows:

- unused objects with identical dependency proof and delete action;
- exact duplicate objects with the same replacement action;
- one naming convention or folder organization batch;
- one route-limited JSON/import limitation batch.

Split rows when the business problem differs, even for the same vendor. For
example, do not group these into one `Meta issue` row:

- Meta base/pixel roles are unclear;
- Meta fires the same event twice;
- Meta `add_to_cart` payload is incomplete;
- Meta funnel events are missing;
- Meta server-side behavior is unclear.

Use parent/detail rows when a family needs a summary plus distinct detail rows.
The parent row gives the theme; each detail row states one concrete problem.

## Wording Rules

Write the visible row for a user who understands marketing and analytics but
does not want to read GTM internals.

Prefer:

- `begin_checkout fires at every checkout step`
- `Google Ads IGGI add_to_cart fires for all products`
- `item_variant is mostly not set on purchases`
- `Analytics and advertising consent appear to use the same rule`
- `Promotion data is missing from the dataLayer`

Avoid:

- `semantic issue on tag family`
- `trigger condition too broad`
- `D3 blocked`
- `custom code inspected`
- `payload transformer issue`
- `configuration reviewed`

Technical terms may appear after a plain-language translation:

```text
Only the first product position is read (`products.0`), so multi-product
orders may send incomplete item data.
```

## Cleanup Plan Shape

Default visible cleanup-plan columns:

```text
ID
Level
Area / problem type
Affected object(s)
Problem / evidence
Action / priority / QA
```

Use `Level = Summary`, `Detail`, or `Single`. `Area / problem type` should look
like `Media platform tracking / Duplicate firing`, not only `Media`.

Keep detailed object IDs, source finding IDs, exact parameters, D3 proof, raw
code, and validator traces in hidden proof tabs. The visible row should be
enough to understand the issue, approve the action, and know how to QA it.

## Change Log Shape

The change log uses the same area/problem taxonomy, but it is written after a
change or generated artifact exists. Do not mix it into the cleanup plan.

Default visible change-log detail columns:

```text
Change ID
Area / object
Change made
Before
After
Reason / QA / status
```

Use one row per modified object, field, dependency, trigger route, variable
source, folder move, template/code update, deletion, creation, rename, or
documented route-limited no-op. Batches are allowed only when the before/after,
reason, QA, rollback, and status are identical.

## Quality Gates

Before delivery, check:

- every visible detail/single row links to an operation packet;
- every operation packet has source finding IDs;
- every visible row has an area and second-level problem type;
- no visible row is only an internal category such as `semantic issue`;
- grouped rows have identical root cause, action, QA, and rollback;
- parent summary rows have immediate detail rows;
- confidence is reduced when a business interpretation comes from names only;
- runtime-only proof is stated as QA/blocker, not as a confirmed issue;
- cleanup plans describe proposed work, while change logs describe completed or
  generated work.

## Examples

Too vague:

```text
Media tracking issue. Review Meta tags and consolidate.
```

Better:

```text
Media platform tracking / Duplicate firing. Meta Purchase appears to fire twice
for the same purchase route. Confirm in runtime QA, then keep one purchase path
and document the server/browser deduplication rule.
```

Too technical:

```text
Trigger condition too broad for tag 674919421 / KBhGCN-rntsBEP3n6cEC.
```

Better:

```text
Media platform tracking / Wrong product scope. Google Ads add_to_cart tag name
suggests IGGI scope, but the trigger listens to all add_to_cart events. Confirm
whether this should be IGGI-only; then restrict the trigger or rename the tag.
```

Too generic:

```text
Consent variables have semantic mismatch.
```

Better:

```text
Consent & compliance / Consent mismatch. Analytics storage and advertising
storage appear to use the same CMP condition. Map each storage state to the
correct CMP category, then test accept/refuse/partial-consent states.
```
