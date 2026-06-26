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
- Custom Code Triage
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
- vendor IDs, pixel IDs, conversion IDs, measurement IDs, and server container
  URLs.

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
- by custom code body hash and variable reference set;
- by dataLayer path family, such as `ecommerce.purchase.products.*`;
- by expected output type.

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
import/export JSON file after the complete audit and cleanup design. Do not
produce a partial patch unless the user explicitly asked for one.

Required pass order:

1. Preserve the original export as rollback evidence.
2. Record the intended import mode: manual same-container merge, overwrite, or
   new-container import. If unspecified, assume manual same-container merge and
   document the conflict strategy.
3. Build complete dependency maps for tags, triggers, variables, trigger groups,
   setup/teardown, folders, templates, and custom code references.
4. Classify Google analytics/ecommerce objects as GA4/current Google tag by
   default, with UA only as an explicit documented exception.
5. Classify all objects as keep, safe change, safe delete candidate,
   consolidation obsolete, or deferred with blocker.
6. Choose the JSON object strategy. For manual same-container merge, emit a
   minimal review patch containing only changed objects. Allow finalized
   replacement/additive objects when in-place edits would create GTM import
   conflicts or empty-value errors. For overwrite or new-container imports,
   direct object updates/deletions may be appropriate. If the user wants GTM
   View Changes to show modified existing objects, preserve existing object
   names in the review JSON; GTM merge conflicts are name-based, so broad
   renaming belongs in direct GTM/API/MCP cleanup or a separate final-state
   artifact.
7. Apply all evidence-safe fixes across tags, triggers, variables, custom code,
   folders, naming, duplicates, and consolidation candidates.
8. Flatten trigger groups with exactly one member by remapping every consuming
   tag to the child trigger. Delete the group for overwrite/new-container JSON;
   for same-container merge JSON, mark it as a delete candidate and provide the
   required direct/overwrite deletion path because merge patches cannot reliably
   delete omitted existing objects.
9. Recompute dependencies after every consolidation/delete batch in the draft
   JSON.
10. Validate that the JSON still parses, IDs are unique, references resolve, and
   no new missing trigger, variable, setup-tag, or teardown-tag references were
   introduced.
11. Self-audit the generated file as a fresh export: inventory all layers, detect
   duplicate configurations, unresolved unused objects, naming/logic
   mismatches, active UA Enhanced Ecommerce mappings, missing references, and
   residual blockers.
12. Validate import-noise handling. For manual same-container merge, omit
   unchanged object arrays from the import patch except schema dependencies
   needed to resolve changed objects: folder definitions for `parentFolderId`
   references and the complete intended `customTemplate` set when included
   tags/variables use template `type` values such as `cvt_123_456`. If custom
   templates are included only as dependencies, verify they are byte-for-byte
   unchanged from the source export and document that they are present only to
   resolve GTM entity types. Preserve the complete intended `builtInVariable`
   array whenever the source or cleanup draft has enabled built-in variables.
   Preserve a separate full-export backup only for rollback or
   overwrite/new-container use.
13. For manual same-container merge JSON that uses replacement/additive objects,
   produce an old-to-new replacement map, consumer-update evidence, and
   post-QA decommission plan for the original objects.
14. Produce a change log that lists changed objects and deferred objects by
   blocker.

Use deterministic helpers when Python is available:

- `scripts/gtm_diff_operations.py <original> <draft>` to produce a structured
  operation diff or change-log-shaped CSV for full exports.
- `scripts/gtm_diff_operations.py <original> <patch> --patch` for
  same-container patch artifacts, so omitted unchanged objects are not treated
  as removals.
- `scripts/gtm_validate_artifact.py <artifact> --original <original> --mode
  same-container-view` for GTM View Changes JSON.
- `scripts/gtm_validate_artifact.py <artifact> --original <original> --mode
  same-container-final` for same-container final-state JSON.
- `scripts/gtm_validate_artifact.py <artifact> --mode overwrite` or
  `--mode new-container` for overwrite/new-container artifacts.

Do not deliver a JSON artifact when `gtm_validate_artifact.py` fails unless the
failure is intentionally accepted by the user and documented as a residual
blocker.

When a full cleanup draft exists and the deliverable is manual same-container
merge for final state, use `scripts/gtm_make_merge_patch.py` to create the final
file. The script omits unchanged arrays and validates that applying the patch to
the original export reconstructs the cleaned draft.

When the deliverable is a same-container JSON intended for GTM View Changes, use
`scripts/gtm_make_name_preserving_review_patch.py`. It preserves existing names
and rewrites variable/setup/teardown references so GTM can match conflicts by
name and show modifications instead of broad add/delete churn. State that this
review artifact intentionally defers naming standardization.

The cleanup JSON should include safe trigger and variable cleanup, not only
tag payload or ecommerce fixes. For same-container merge patches, "include"
means include every changed object needed for the final state, not every
unchanged object from the source export. If a category has no changes, state why:
already clean, blocked by evidence, blocked by business meaning, or not
applicable.
Do not call the JSON import-ready when the generated-file self-audit has blank
workstreams or unresolved duplicate/unused/reference/name mismatches that are
not documented as intentional residuals.
Do not call template modified/delete/add noise acceptable when no template
behavior changed. If no included object needs a `cvt_...` type, omit the
`customTemplate` layer. If included objects need `cvt_...` types, include the
complete intended custom-template set, not a partial subset, and verify the
dependency-only templates are unchanged.

Do not omit folders that are referenced by `parentFolderId` in changed tags,
triggers, or variables. Referenced folders are schema dependencies for GTM
import, even when the folder objects themselves are unchanged.

Do not omit custom templates that are referenced by included tags or variables
whose `type` is a `cvt_...` value. Referenced custom templates are schema
dependencies for GTM import, even when the template objects themselves are
unchanged.

Do not use a rename-heavy JSON import as the human-review artifact. GTM merge
conflicts are name-based, so renamed tags, triggers, and variables can appear as
added/deleted rather than modified. Use direct GTM/API/MCP for true in-place
renaming, or produce a name-preserving review JSON plus a separate
final-standardized artifact.

Do not omit `builtInVariable` when the source export has enabled built-in
variables. GTM import can interpret a missing built-in-variable layer as an
empty enabled set, which disables built-ins such as Page URL, Event, Click, and
Form variables.

Do not call a cleanup complete when active tags still depend on a trigger group
that contains only one trigger. That group must be flattened or explicitly
blocked by the route, with the direct/overwrite deletion path documented.

Do not apply direct GTM/MCP/API in-place cleanup assumptions to manual
same-container import JSON. If the file is meant for manual merge into the same
container, prepare the artifact for import conflict handling and make the
replacement/decommission path explicit.

## Custom Code Triage

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
window.

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
- whether vendor platforms record conversions.

Mark these as requiring Tag Assistant, browser/network, crawler, or platform
evidence.

## Scalable Audit Loop

For large containers:

1. Count objects by layer, type, vendor, folder, and naming prefix.
2. Build dependency maps before judging deletion candidates.
3. Profile semantic roles and expected payload/output types.
4. Cluster exact duplicates and similar consolidatable objects by normalized
   name, type, event, vendor ID, market, dataLayer path family, and code hash.
5. Audit high-risk families first: consent, GA4/ecommerce, Ads/Meta conversions,
   server-side forwarding, custom HTML/JS.
6. Design consolidation candidates before finalizing cleanup candidates.
7. Recompute what becomes obsolete after the consolidation design.
8. Sample low-risk naming/hygiene patterns, then expand only when findings
   repeat.
9. Keep raw object details in files/tables and report only evidence snippets.

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
