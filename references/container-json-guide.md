# Container JSON Guide

Use this reference to turn exported GTM JSON or API/UI evidence into scalable
inventory and dependency tables. The exact field names can vary by export/API
shape, so inspect the source structure before assuming paths.

## Contents

- Preferred Evidence Order
- Normalize These Tables
- Reference Extraction
- Semantic Profiling
- Google Event Classification Pass
- Official Documentation Mapping
- Standard Ecommerce Variable Pass
- Importable JSON Cleanup Pass
- Custom Code Export Review
- Runtime Checks Not Proven By JSON
- Scalable Audit Loop
- Usage Status Values

## Preferred Evidence Order

1. Fresh exported container JSON from the target workspace/version.
2. GTM API reads for specific objects or fresh inventory.
3. GTM UI screenshots/tables when export/API is unavailable.
4. Tag Assistant, browser network traces, page source, crawler output, and
   stakeholder notes for website behavior.

Exports are best for reproducibility. Browser evidence is still required for
installation, consent timing, duplicate network hits, CSP blocking, and real
runtime behavior.

## Normalize These Tables

Create compact tables instead of working directly from raw JSON:

### Tags

Fields:

- name;
- tagId or path;
- type/vendor;
- folderId/name;
- firingTriggerId list;
- blockingTriggerId list;
- setup/teardown tag references;
- consent settings;
- parameter summary;
- custom HTML body snippet or hash when relevant;
- referenced variables;
- expected payload fields and field types;
- official documentation source and expected event contract;
- event/page/business role;
- gateway role, such as loader, dispatcher, event tag, conversion tag, or helper;
- last edited/fingerprint/version metadata when present.

### Triggers

Fields:

- name;
- triggerId or path;
- type/event type;
- folderId/name;
- filter/customEventFilter summary;
- trigger group members;
- connected firing tags;
- connected blocking tags;
- referenced variables;
- hostname/market/region/scope signals;
- consolidatable condition pattern, such as same event plus hostname, same event
  plus product-line regex, same CMP vendor condition, or same route pattern.

### Variables

Fields:

- name;
- variableId or path;
- type;
- folderId/name;
- dataLayer key or parameter summary;
- custom JS body snippet or hash when relevant;
- lookup/regex table summary;
- consumers by layer;
- references to other variables;
- standard ecommerce role, such as revenue, total price, total quantity, item
  IDs, item array, tax, shipping, or transaction ID;
- formula or aggregation method for derived ecommerce values;
- expected output type and sample shape;
- likely consumer fields and vendor requirements;
- null/default behavior.

### Templates And Folders

Fields:

- name;
- ID/path;
- type;
- consumers;
- update state if available;
- owner/notes.

## Reference Extraction

Search both structured fields and text bodies:

- `{{Variable Name}}` references inside tag parameters, trigger filters, custom
  HTML, custom JavaScript, templates, and notes;
- trigger IDs in tag firing/blocking lists and trigger groups;
- setup/teardown relationships, including `tagName` references used by GTM
  import validation;
- folder IDs for organizational review;
- event names in custom event triggers and dataLayer pushes;
- vendor IDs, pixel IDs, conversion IDs, measurement IDs, server container
  URLs, transport URLs, and first-party tagging endpoints;
- server-forwarded parameters such as consent state, CMP group values, cookie
  consent, click IDs, event IDs, user data, and media/vendor identifiers.

When object names are duplicated, rely on IDs/paths for dependency logic and
flag duplicate names as a maintainability finding.

## Semantic Profiling

After the first inventory, create semantic groups before writing findings:

- by destination/vendor and event name;
- by ecommerce event schema, such as detail, impression, add, checkout, remove,
  purchase, or GA4 items;
- by trigger-group member count, especially groups containing exactly one
  trigger;
- by market/language/hostname/path;
- by name-inferred scope tokens, such as country codes, product ranges,
  campaign suffixes, or internal prefixes;
- by consent vendor/purpose;
- by client-to-server transport pattern, including Google tags or event tags
  that use a server endpoint, gateway naming, S2S naming, placeholder-looking
  destination IDs, or consent/routing parameters;
- by custom code body hash and variable reference set;
- by dataLayer path family, such as `ecommerce.purchase.products.*`;
- by expected output type;
- by semantic role and formula family, such as total value, item price, total
  quantity, item array, content IDs, lead type, transaction ID, consent group,
  market, or product category.

For each group, decide whether objects are:

- exact duplicates;
- near duplicates with only market/vendor ID/event name differences;
- intentionally separate because ownership or QA differs;
- candidates for lookup-table, regex-table, custom JS, trigger-group, or gateway
  consolidation;
- currently unused;
- used now but likely obsolete after consolidation.

Do not report only exact duplicates. Similar objects at scale are often the main
cleanup opportunity.

After grouping, run `semantic-logic-checks.md` for shared variables, computed
values, media/ecommerce payloads, custom code, and any object whose name implies
a business action or scope. The JSON export can reveal contradictions such as a
`total_quantity` helper reading prices, a purchase-value tag reading a product
unit price, or several vendors consuming the same variable with incompatible
field-shape expectations.

For complex containers, build the semantic model from
`semantic-model-protocol.md` before proposing consolidation. This is especially
important when repeated objects differ by market, product line, form type,
campaign, consent category, server route, or vendor payload shape.

## Google Event Classification Pass

For exported containers, treat Google Analytics/event/ecommerce objects as
GA4/current Google tag tracking unless the export or user explicitly proves a UA
exception.

Classify as UA only when there is concrete evidence such as:

- a UA-specific tag type or `UA-` property ID;
- an explicit user request to preserve legacy UA;
- a documented mapper that converts UA Enhanced Ecommerce pushes into verified
  outgoing GA4 payloads.

Otherwise, old custom event names and old ecommerce paths are migration signals.
Flag active paths such as `ecommerce.purchase.actionField.*`,
`ecommerce.purchase.products.*`, `ecommerce.add.products.*`,
`ecommerce.detail.products.*`, `ecommerce.checkout.products.*`, and
`ecommerce.impressions` when they feed GA4, Google, or media tags without a
verified mapper.

Do not treat a Google tag or Google event tag as broken solely because a
placeholder-looking `G-XXXXXX` or non-final measurement ID appears in the web
container when a server container URL, transport URL, first-party endpoint, S2S
name, or server-forwarded consent/routing parameters are present. Mark it as a
client-to-server candidate and require server container evidence before
recommending ID replacement, blocking-trigger changes, or deactivation.

## Official Documentation Mapping

Create a compact documentation contract table for every vendor/event family
found in the export:

- vendor/platform;
- tag names and IDs;
- implemented event names;
- official documentation source checked, access date, and confidence;
- standard event names expected by the platform;
- required parameters and recommended parameters;
- expected data type and shape for each important field;
- expected source of truth, such as current dataLayer event, ecommerce item
  array, server event, cookie, hashed identifier, or static configuration;
- observed implementation gap;
- whether the gap can be solved in GTM or requires website/dataLayer work.

Use this table to prevent false fixes. If a GA4, Meta, TikTok, Snapchat,
Pinterest, Microsoft, LinkedIn, or affiliate event expects price, quantity,
currency, item IDs, contents, or item arrays from the current user action, do not
create a GTM helper that guesses the value from unrelated events. Flag missing
or incomplete dataLayer instrumentation instead.

## Standard Ecommerce Variable Pass

Run this pass before finalizing GA4, media, affiliate, or cleanup findings:

1. List all common ecommerce variables, including transaction ID, revenue,
   value, tax, shipping, currency, total price, total quantity, product IDs,
   product names, categories, quantities, item arrays, checkout products,
   purchase products, add-to-cart products, and remove-from-cart products.
2. Group them by dataLayer path family and event context so variables from
   different events are not mixed accidentally.
3. For each variable, record the source path, formula, expected type, actual
   returned shape if inferable, null/`NaN` behavior, and multi-item behavior.
4. Trace every consumer and vendor field. A variable can be technically valid
   for one destination and wrong for another if the expected shape differs.
5. Promote broken core variables to explicit findings with affected consumers
   and logical consequences.
6. Compare every standard ecommerce variable to the official event contract for
   each consuming tag. If the official contract expects dataLayer/source-site
   values that do not exist, classify it as a dataLayer readiness blocker rather
   than a GTM-only fix.

Common high-risk examples:

- total quantity variables that read price fields or mix quantity and price;
- total price variables that duplicate item indexes, ignore quantity, or return
  `NaN` when one item is absent;
- item ID/category/name variables that return one scalar where the vendor expects
  an array or object;
- helpers that read old dataLayer pushes instead of the current ecommerce event;
- checkout or purchase variables that read add-to-cart or remove-from-cart
  paths.

When object names contain unclear tokens, such as product-range or campaign
labels, record the token and ask the user for its business meaning before
marking the variable incorrect or safe to consolidate.

## Importable JSON Cleanup Pass

When the user asks for cleanup JSON, generate a GTM-compatible container
import/export JSON file after the complete audit and cleanup design. Use
`import-json-policy.md` as the source of truth for same-container merge, View
Changes review, overwrite/new-container imports, schema dependencies, validation
commands, and failure handling.

This guide still owns the export-analysis loop:

1. Preserve the original export as rollback evidence.
2. Build dependency maps for tags, triggers, variables, trigger groups,
   setup/teardown, folders, templates, and custom code references.
3. Classify all objects as keep, safe change, safe delete candidate,
   consolidation obsolete, or deferred with blocker.
4. Apply every evidence-safe fix across tags, triggers, variables, custom code,
   folders, naming, duplicates, and consolidation candidates.
5. Recompute dependencies after every consolidation/delete batch.
6. Validate with `scripts/gtm_validate_artifact.py` and create operation/change
   evidence with `scripts/gtm_diff_operations.py`.

For manual same-container merge patches, use:

- `scripts/gtm_make_merge_patch.py` for final-state patch artifacts;
- `scripts/gtm_make_name_preserving_review_patch.py` for GTM View Changes review
  artifacts.

Do not call a JSON artifact import-ready while generated-file self-audit has
blank workstreams, missing references, unresolved duplicate/unused/name/logic
issues, active unverified UA ecommerce paths, or undocumented route blockers.

## Custom Code Export Review

Do not paste full custom code unless it is necessary evidence. Summarize:

- purpose;
- external scripts loaded;
- vendor endpoints;
- variable references;
- dataLayer reads;
- cookie/localStorage/sessionStorage reads/writes;
- PII or identifier handling;
- consent checks;
- null guards;
- array assumptions;
- repeated logic that should become a helper variable.

Use hashes or short snippets to compare duplicates without filling the context
window. Hashes, external URLs, code length, extracted variable references, and
duplicate groups are triage signals only. They do not complete semantic
validation.

Export-level review is mandatory for every active, referenced, risky, unused, or
cleanup-relevant custom-code object in scope. Runtime QA may still be required
before changing the object, but the audit must already inspect the exported code
or custom-template configuration and explain what it appears to do.

If D3 is required, complete D3 from the export before delivery. The export
usually contains Custom HTML, Custom JavaScript, DLV paths, lookup/regex rows,
trigger filters, and tag/template parameters. Do not mark D3 as blocked merely
because D4 runtime proof, server access, CMP traces, or vendor acceptance is
missing.

For each active Custom HTML tag and each referenced, risky, unused, or
cleanup-relevant Custom JavaScript variable, create an object-level semantic row
that records:

- purpose;
- role category;
- trigger or consumer context;
- consent assumption;
- external URLs, dataLayer pushes, storage, cookie, DOM, listener, and network
  side effects;
- variable references;
- expected output or side effect;
- runtime risks;
- recommended action;
- semantic status.

Write those fields as compact semantic summaries, not evidence fragments. Use
`summary-quality.md`: category, source/input, logic/action, output or side
effect, and judgment. For example, `Reads cmpConsentPurposes and returns
granted when purpose ,1, is present` is valid proof; `custom code inspected` or
`no external URL found` is not.

If the export does not provide enough evidence to decide the semantic status,
mark the object `More info needed` or defer it with the missing runtime,
business, CMP/legal, or vendor-platform evidence. Do not silently drop it from
the cleanup plan.

Use `More info needed` only after recording the available D3 evidence. It may
block mutation, not source/code inspection.

Do not create a cleanup operation whose main action is to review the same code
later. If export-level code/config inspection has not happened, the current
deliverable is `Incomplete / blocked` for that object. If inspection has
happened but live behavior is uncertain, the operation should be runtime QA,
owner validation, safe rewrite after QA, migration after QA, or no-change
exception with the exact blocker.

For custom JS variables, evaluate the returned value:

- scalar, boolean, number, array, object, JSON string, joined string, or URL;
- behavior for missing dataLayer paths;
- behavior for multi-item carts/purchases;
- whether it reads the current event or searches stale historical pushes;
- whether numeric parsing can produce `NaN`;
- whether DOM selectors can return `null`;
- whether the returned type matches every consuming tag field.

For custom HTML, preserve variable references during any proposed rewrite. If a
value is currently `{{cJS - content ids}}`, a proposal that hardcodes a sample
ID is wrong unless the user explicitly approved that semantic change.

## Runtime Checks Not Proven By JSON

Exported JSON cannot fully prove:

- GTM snippet placement;
- whether GTM loads on every important page template;
- SPA route-change behavior;
- CMP timing and consent update order;
- CSP/browser blocking;
- duplicate network hits;
- whether server-side endpoints receive traffic;
- whether server-side clients, transformations, consent checks, and
  server-to-vendor destination mappings are configured as expected;
- whether vendor platforms record conversions.

Mark these as requiring Tag Assistant, browser/network, crawler, or platform
evidence.

## Scalable Audit Loop

For large containers:

1. Count objects by layer, type, vendor, folder, and naming prefix.
2. Build dependency maps before judging deletion candidates.
3. Profile semantic roles and expected payload/output types in a semantic
   object matrix.
4. Cluster exact duplicates and similar consolidatable objects by normalized
   name, type, event, vendor ID, market, dataLayer path family, and code hash.
5. Audit high-risk families first: consent, GA4/ecommerce, Ads/Meta conversions,
   server-side forwarding, custom HTML/JS.
6. Design consolidation candidates before finalizing cleanup candidates.
7. Recompute what becomes obsolete after the consolidation design.
8. Convert triage clusters into object-level or family-level semantic matrix
   rows. High-impact anomalies need object rows; repeated low-risk patterns may
   use family rows plus anomaly rows. Mark unresolved families as deferred, not
   done.
9. Sample low-risk naming/hygiene patterns, then expand only when findings
   repeat.
10. Reconcile counts by object family: total, inventoried, dependency-mapped,
   semantically validated, cleanup-decisioned, deferred, not applicable,
   user-excluded, and unresolved.
11. Treat any nonzero unresolved count as a failed completion gate until the
   row is resolved or explicitly deferred with blocker evidence.
12. Keep raw object details in files/tables and report only decisions, evidence
   snippets, blockers, operations, and representative exemplars.

## Usage Status Values

Use these normalized values:

- `Keep`: evidence supports active use.
- `Delete candidate`: no consumers and owner/business validation still needed.
- `Consolidation obsolete`: currently used, but expected to be replaced by an
  approved consolidation/refactor.
- `Needs owner validation`: technical evidence is insufficient.
- `Not sure`: evidence is contradictory or incomplete.
- `Do not delete`: object appears unused but is intentionally retained, legally
  required, or needed for planned work.

Do not use `Delete` until deletion is approved and verification is complete.
