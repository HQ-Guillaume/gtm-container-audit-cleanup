# Semantic Logic Checks

Use this reference as an internal reasoning pass before writing findings,
cleanup operations, generated JSON, or a change log. The goal is not to add more
report volume. The goal is to understand whether the container configuration
makes business and data sense as a whole.

## Contents

- Principle
- Semantic Graph
- Formula Sanity
- Context Consistency
- Contradiction Patterns
- Cross-Consumer Checks
- Media Signal Quality
- Cleanup Plan And Change Log Coherence

## Principle

A GTM object can be syntactically valid and still be analytically wrong. Do not
stop at "tag exists", "trigger fires", "variable resolves", or "vendor field is
filled". Check whether the object meaning, source data, formula, event context,
payload shape, and consumers agree with each other.

Only surface the result when it changes a finding, operation, blocker, or QA
step. Keep scratch reasoning internal or in a technical workbook tab when the
user asks for traceability.

## Semantic Graph

Build a graph for meaningful tags, triggers, variables, folders, templates, and
custom code:

```text
business action -> trigger/event context -> tag -> vendor field
                                      -> variable/helper -> source path/formula
                                      -> custom code side effect
                                      -> consent/server routing
```

For each edge, infer:

- meaning: purchase value, item price, total quantity, form type, lead ID,
  product/category, consent group, market, page type, or audience;
- source of truth: current dataLayer event, previous dataLayer history, DOM,
  URL, cookie, constant, lookup table, server container, or vendor platform;
- output type: number, numeric string, scalar ID, array, object, array of
  objects, JSON string, boolean, URL, or side effect;
- consumer expectation: vendor field, GA4 parameter, trigger condition, custom
  HTML placeholder, setup/teardown reference, or report-only metadata.

## Formula Sanity

For every variable or custom code block that computes a business value, test the
logic against its name, source fields, event context, and consumers.

Flag as suspect when:

- total price sums fixed item prices such as `product_price_1 + product_price_2
  + product_price_3` instead of iterating current items, multiplying unit price
  by quantity where required, or using the official order value;
- total quantity reads price fields, value fields, or fixed product indexes
  instead of item quantities;
- order value reads a product unit price, first item price, subtotal from a
  different event, stale product-detail data, or DOM text unrelated to the
  conversion event;
- discount, tax, shipping, coupon, or currency are missing from the value model
  when the destination or business reporting expects them;
- item arrays are built from scalar IDs, comma-joined strings, fixed indexes, or
  `[object Object]` output where the vendor expects an array/object shape;
- lead value is static or copied across all form types when names/triggers imply
  materially different lead value;
- custom JavaScript searches historical `dataLayer` pushes and may return stale
  product, cart, user, or consent values.

Do not replace a nonsensical formula with another guess. If the website or
dataLayer should provide the source field, mark website/dataLayer work as the
blocker.

## Context Consistency

Check whether each variable is valid at the moment each consuming tag fires:

- Does the trigger event carry the source data the variable reads?
- Does the variable read the current event or an older event?
- Does the same variable serve incompatible contexts, such as product detail,
  add-to-cart, checkout, and purchase?
- Does the tag fire before consent, dataLayer, product, lead, or transaction
  fields are available?
- Does a pageview tag consume form/product variables that are only available
  later?
- Does a thank-you page trigger represent one form type, several form types, or
  an unknown backend outcome?

If the export cannot prove the runtime context, classify the check as runtime
QA required rather than assuming correctness.

Runtime QA required is not permission to skip export-level logic checks. Still
inspect source paths, formulas, lookup rows, custom code/config, output shape,
and consumers before marking only the runtime proof as blocked.

## Contradiction Patterns

Actively search for contradictions:

- name says `purchase`, `lead`, `qualified lead`, `appointment`, `FR`,
  `product range`, or `consent granted`, but trigger/filter/payload does not
  enforce that meaning;
- tag event name is final conversion but trigger is a click, form start,
  generic pageview, or shared thank-you page;
- trigger is reused by tags with different business meanings and no downstream
  parameter distinguishes those meanings;
- variable name says total/order/quantity/items/category but formula reads a
  narrower, unrelated, stale, or differently typed value;
- vendor field expects array/object but receives scalar DLV, joined string,
  fixed index, or unguarded custom JS;
- same business action sends different values, currencies, IDs, item sets,
  event IDs, or lead types to different vendors without a documented reason;
- cleanup/naming would make two semantically different objects look identical.

## Cross-Consumer Checks

A variable can be correct for one tag and wrong for another. For shared
variables:

- list all consuming tags and fields;
- compare each consumer's expected type and business meaning;
- split, rename, or defer when one helper is serving incompatible semantics;
- avoid "fixing" a shared variable for one vendor in a way that breaks another.

## Media Signal Quality

For media and conversion tags, infer the platform optimization signal:

- final conversion, micro-conversion, audience event, exclusion, remarketing,
  attribution helper, enhanced matching, or server-forwarding event;
- high-intent vs low-intent action;
- value/currency/source ID quality;
- event ID/deduplication and browser/server relationship;
- whether the signal is likely to train bidding toward the intended business
  outcome.

Only report media-signal concerns when they produce an actionable operation,
blocker, or owner question. Do not expand the cleanup plan with a strategy
essay.

## Cleanup Plan And Change Log Coherence

The cleanup plan is the decision source. The change log is the execution record.

- Every change-log row must map to a cleanup operation ID or explicitly state
  that it is a no-op/documented exception.
- Do not introduce new findings, new reasoning, or different risk wording in the
  change log.
- If semantic logic checks discover a bad setup, create or update the cleanup
  operation first; then the change-log row mirrors that operation after it is
  executed or generated.
- Keep the plan and change log aligned on object IDs, before/after names,
  action, reason, impact, QA, owner, and status.
- When no mutation is made because evidence is missing, use a deferred/blocker
  operation; do not create a misleading "changed" log row.
