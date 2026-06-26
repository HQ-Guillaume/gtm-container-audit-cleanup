# Mutation Playbook

Read this immediately before any GTM create, update, rename, delete, import,
workspace change, or batch cleanup. The goal is small, reversible changes with
fresh verification after each batch.

## Contents

- Pre-Write Gate
- Execution Route Decision
- Route-Specific Cleanup Strategy
- Full Cleanup Scope Gate
- Change Plan
- API Mechanics
- Dependency Sweep
- Mandatory Naming Standardization Gate
- Sequencing Strategy
- Safe Batch Order
- Consent And Payload Change Rules
- Custom HTML Reference Safety
- Importable JSON Validation
- Rollback And Verification
- Stop Conditions

## Pre-Write Gate

Proceed only when all are true:

- the user explicitly approved mutation, not just an audit or recommendation;
- the user chose the execution route: direct GTM/MCP/API cleanup or an
  importable GTM container JSON file for manual import;
- the cleanup aggressiveness level is recorded as Conservative, Standard, Deep,
  or Transformational;
- the approved scope lists the account, container, workspace, and operation
  types;
- for direct GTM/MCP/API cleanup, a newly created dedicated workspace exists;
- if GTM cannot create a new workspace because of a workspace quota or active
  workspace limit, the user has been alerted before any cleanup and has chosen
  whether to free a workspace, use importable JSON, or stop;
- for importable JSON cleanup, the output target is a GTM-compatible container
  import/export `.json` file, not a Markdown report or pasted JSON block;
- for importable JSON cleanup, the intended import mode is recorded as manual
  same-container merge, overwrite, or new-container import; if unspecified,
  default to manual same-container merge and state that assumption;
- a fresh export/snapshot exists for rollback;
- a dependency sweep has been completed for every rename/delete/update;
- the final naming scheme for new helper variables, triggers, and tags is known;
- the completion ledger has no blank mandatory workstreams;
- a structured operation table exists using `operation-schema.md`;
- Google analytics/ecommerce objects have been classified as GA4/current Google
  tag by default, with UA only as an explicit documented exception;
- GA4 standard/ecommerce events have an official dataLayer/event payload schema
  map, or GA4 is out of scope/not applicable;
- consolidation-obsolete objects have been separated from currently unused
  objects;
- publish/version creation is explicitly excluded unless the user requested it.

If any item is missing, stop and ask for the missing approval or evidence.

Read `operation-schema.md` before building the operation table. Do not execute
from a prose-only plan.

## Execution Route Decision

When the user allows cleanup, ask this before preparing writes:

```text
Do you want me to apply the cleanup directly in GTM through the available
tools/MCP/API, or generate an importable GTM container JSON file for manual
import?
```

Use direct GTM/MCP/API cleanup only when a new workspace can be created and
identified in the plan. If workspace creation fails or GTM reports a workspace
limit, stop and alert the user before changing anything.

Use importable JSON cleanup when the user wants manual control, when live access
is unavailable, or when workspace limits make direct cleanup unsafe. The JSON
must preserve GTM export/import structure and should be accompanied by a concise
change log and validation notes.

## Route-Specific Cleanup Strategy

Select the object mutation style from the execution route before building the
operation table:

- **Direct GTM/MCP/API cleanup**: prioritize in-place updates to existing
  objects when safe. Preserve object IDs, existing references, history, and
  workspace traceability. Create replacement objects only for genuinely new
  reusable concepts, staged migrations, or cases where GTM/API behavior makes an
  in-place edit unsafe.
- **Importable JSON for manual same-container merge**: prepare for GTM import
  conflict handling. Replacement/additive objects are allowed, and often safer,
  when editing existing objects would create difficult import conflicts or
  `value cannot be empty` errors. Emit a minimal review patch that contains only
  changed objects, update consumers inside the JSON, keep an old-to-new map, and
  list old objects as post-QA decommission candidates rather than pretending
  they vanished safely from the existing container. If the user cares about GTM
  View Changes as the review surface, preserve existing object names in the JSON
  and defer naming standardization; GTM merge conflict matching is name-based.
- **Importable JSON for overwrite or new-container import**: a full cleaned
  export may update, rename, or delete existing objects directly because manual
  conflict resolution against the existing container is not the main constraint.

Do not use the direct-cleanup in-place default for same-container import JSON,
and do not use the JSON replacement-default for direct GTM cleanup when an
in-place update is safer.

Prefer direct GTM/MCP/API cleanup when the user wants existing objects modified
in place, especially for naming standardization, trigger/variable consolidation,
and deletion. JSON import is best for backup, migration, overwrite/new-container
artifacts, or a name-preserving review patch with known limitations.

## Full Cleanup Scope Gate

Before writing directly or generating importable JSON, confirm the cleanup plan
covers the full container unless the user explicitly requested a smaller scope.

The plan must address:

- tag corrections, tag consolidation, consent routing, sequencing, naming, and
  folder placement;
- Google event classification, with ambiguous Google analytics/ecommerce
  objects treated as GA4/current Google tag rather than UA;
- GA4 dataLayer/event payload correctness before GA4 variable or tag fixes;
- trigger duplicates, near duplicates, trigger groups, exceptions, unused
  triggers, single-member trigger groups, and reusable trigger opportunities;
- variable duplicates, ecommerce helpers, custom JS, lookup/regex table
  opportunities, unused variables, and consolidation-obsolete variables;
- custom HTML and custom JavaScript safety;
- templates and folders;
- exact duplicates and similar consolidatable patterns;
- currently unused objects and objects that become obsolete after consolidation.

If a layer is not changed, document the reason. Valid reasons are: no issue
found, not applicable, blocked by missing runtime evidence, blocked by CMP/legal
decision, blocked by unclear business scope, or deliberately excluded by the
user.

Do not proceed when a mandatory workstream is merely "not yet looked at".
Complete it, mark it not applicable, or defer it with object-level blockers.
Do not proceed when active Google/GA4 mappings still use UA Enhanced Ecommerce
paths without verified mapper and outgoing payload evidence.

## Aggressiveness Gate

Record one cleanup aggressiveness level:

- `Conservative`: clear breakage only; no broad renames, deletion, or
  consolidation without separate approval.
- `Standard`: default execution level; in-place fixes, safe naming,
  single-member trigger-group flattening, obvious duplicates, and documented
  delete candidates after dependency sweep.
- `Deep`: cross-layer consolidation, reusable helpers, deletion after QA, broad
  naming, and custom-code hardening with strong evidence.
- `Transformational`: gateway redesign, ecommerce contract redesign,
  server-side migration, or market architecture changes.

If a change belongs to a higher level than the approved level, defer it with a
blocker instead of quietly applying it.

## Change Plan

Prepare a compact operation table before writing:

| Field | Meaning |
| --- | --- |
| Change ID | Stable ID for discussion and rollback. |
| Aggressiveness | Conservative, Standard, Deep, or Transformational. |
| Layer | Tag, Trigger, Variable, Template, Folder, Workspace, Server-side. |
| Action | Add, Update, Rename, Delete, Replace, Document exception. |
| Object | Name and ID/path. |
| Route strategy | In-place direct update, same-container JSON replacement/addition, or overwrite/new-container JSON update. |
| Reason | Finding or decision driving the change. |
| Official documentation basis | Official source or not applicable. |
| Semantic role | Vendor/event/business role. |
| Before name | Required for rename/standardization operations. |
| After name | Required for rename/standardization operations. |
| Dependencies | Consumers, blockers, setup/teardown, trigger groups, code refs. |
| Risk | Data, consent, performance, release, or rollback risk. |
| Verification | Preview/debug, export diff, network check, Tag Assistant, owner QA. |
| Rollback | Exact object/export/version or reversal step. |
| Replaces | Objects made obsolete by this operation, if any. |

Include skipped operations and why they are skipped.

## API Mechanics

When using GTM API or an agent tool wrapping it:

- treat updates as full-replace operations unless the tool documents patch
  semantics;
- preserve required `fingerprint`/ETag/version metadata exactly;
- re-fetch objects immediately before a write when fingerprints may be stale;
- keep batches small, roughly 10 to 16 operations or less;
- re-fetch objects after each batch because list ordering and references can
  change;
- retry only after reading the failure reason;
- note cosmetic normalization from the API but do not chase formatting-only
  diffs;
- verify whether variable renames auto-propagated before manually rewriting
  references.

## Dependency Sweep

Before deleting or renaming a variable, search:

- tag parameters, custom HTML, custom templates, setup/teardown metadata, and
  monitoring metadata;
- trigger filters and custom event filters;
- other variables, lookup tables, regex tables, and custom JavaScript variables;
- exported JSON text for `{{Variable Name}}`, object IDs, and display names;
- any documentation or notes supplied by the user.

Before deleting or renaming a trigger, search:

- tag firing and blocking trigger IDs;
- trigger group members;
- exceptions/blocking logic;
- notes or folders indicating a planned but inactive use.

Before deleting or flattening a trigger group, search:

- the `triggerIds` member list and confirm member count;
- every tag firing or blocking reference to the group ID;
- nested trigger group references, if any;
- whether the selected route can actually delete omitted existing objects.

Before changing a tag, search:

- setup/teardown dependencies, including name-based `setupTag` and
  `teardownTag` `tagName` references that must be updated after tag renames;
- consent settings;
- sequencing requirements;
- server-side duplicates and deduplication IDs;
- downstream reports or conversions that depend on event names/parameters.

Treat export-based orphan findings as candidates until a fresh export or API
read confirms the same result.

## Mandatory Naming Standardization Gate

For cleanup, standardization, or importable JSON generation, apply
naming standardization unless the user explicitly excludes it or the required
business meaning is unclear.

Default convention when no house style exists:

- Tags: `Vendor - Event/role - Scope/detail`.
- Triggers: `Utility/type - Event or condition - Scope/detail`.
- Variables: `Type acronym - Variable name/source`.
- Folders: `Vendor` or `Domain / Function`.

Before any rename:

- define the final convention for tags, triggers, variables, and folders;
- decide final event names from official vendor documentation when applicable;
- clarify ambiguous tokens such as product ranges, campaigns, or agency codes;
- produce a before/after rename map with object IDs;
- dependency-sweep every renamed variable across tags, triggers, variables,
  lookup tables, templates, custom HTML, and custom JavaScript;
- dependency-sweep every renamed trigger/tag for reports, setup/teardown
  `tagName` references, sequencing, and owner references where evidence is
  available.

If naming standardization is skipped or deferred, document the exact object
names, the blocker, and the proposed final pattern. Do not silently treat naming
as optional hygiene.

## Sequencing Strategy

Use this planning sequence before any write:

1. Define the final semantic model: event schema, vendor payload contracts,
   consent pattern, gateway/consolidation pattern, and naming convention.
2. Create or update helper variables first only when their final names,
   returned type, and consumers are already clear.
3. Create or update reusable triggers next, using final naming and exact
   conditions.
4. Update tags in the smallest coherent vendor/event family batch.
5. Verify payloads and consent behavior.
6. Flatten single-member trigger groups by remapping consumers to the child
   trigger, then delete the group when the selected route supports deletion.
7. Delete consolidation-obsolete objects only after their replacements are live
   and verified.
8. Rename cosmetic objects last.

Avoid introducing temporary names or temporary helper variables unless the user
approved a staged migration and the cleanup step is documented.

For direct GTM/MCP/API cleanup, apply this sequence as in-place updates wherever
safe, then delete obsolete objects after verification. For manual same-container
import JSON, the same final semantic model may be represented by replacement or
additive objects; in that case, every replaced object needs a consumer update,
old-to-new map, QA step, and decommission plan.

## Safe Batch Order

1. Create finalized helper variables, lookup tables, and consent/scoping triggers.
2. Normalize consent routing for one vendor/tag family at a time.
3. Update tags and triggers to use the helpers.
4. Verify behavior in Preview/debug, Tag Assistant, exported JSON, or API reads.
5. Recompute consumers and obsolete objects.
6. Flatten single-member trigger groups by remapping consumers to the child
   trigger, then delete the group when the selected route supports deletion.
7. Delete currently unused and consolidation-obsolete elements only after
   verification.
8. Rename cosmetic objects last, layer by layer.
9. Run a final fresh inventory and compare against the plan.

Do not combine consent-routing changes, payload changes, and naming changes in
the same batch unless the container is tiny and the user approved the combined
risk.

## Consent And Payload Change Rules

- Inventory all pageview-level tags for a vendor before changing one of them.
- Keep base/config/pageview/server-side duplicates aligned unless an exception is
  documented.
- Do not change event names, transaction IDs, item arrays, currency/value logic,
  consent mode calls, or vendor-required keys without calling out semantic
  impact.
- Do not patch GA4 ecommerce variables from old UA Enhanced Ecommerce paths
  unless the official GA4 payload schema, source dataLayer event, and outgoing
  GA4 payload have been mapped. If the required GA4 dataLayer fields do not
  exist, mark the website/dataLayer implementation as the blocker instead of
  inventing GTM-side values.
- Do not treat Google analytics/ecommerce events as UA by default. UA is a
  sunset/deprecated exception that requires explicit evidence and reporting.
- Before changing standard ecommerce variables such as total price, total
  quantity, revenue, tax, shipping, transaction ID, item IDs, categories, or
  item arrays, trace every consumer and verify the required output shape for
  each destination.
- Test ecommerce helper changes against empty, one-item, and multi-item payloads,
  plus missing price, quantity, currency, and product fields where those cases
  are possible.
- Use helper variables for repeated derived values, guards, and multi-item
  checks instead of duplicating custom JavaScript across tags.

## Custom HTML Reference Safety

Custom HTML edits are high risk. Before changing one:

- extract every `{{variable}}` reference and map it to its expected type;
- identify constants separately from dynamic values;
- preserve dynamic variable references unless a semantic change is explicitly
  approved;
- verify quotation, escaping, URL encoding, JSON serialization, and array/object
  formatting for every inserted value;
- never replace `{{variable}}` with a sample literal, unrelated hardcoded value,
  or copied value from another tag;
- compare before/after payload fields at the vendor boundary, not just the GTM
  object diff;
- re-scan the full export for broken `{{variable}}` references after editing.

## Importable JSON Validation

For importable GTM container JSON:

- keep a copy of the original export path or source as rollback evidence;
- record the import mode and conflict strategy. If the user did not specify an
  import mode, assume manual same-container merge and use a conflict-aware
  replacement/additive strategy when safer than in-place edits;
- preserve the GTM export/import schema rather than producing a Markdown or
  pseudo-JSON artifact;
- for manual same-container merge, include only changed objects in the import
  patch; omit unchanged layers and unchanged objects so GTM workspace changes
  remain human-reviewable, except folder definitions required to resolve
  `parentFolderId` references on changed objects and the complete intended
  custom-template set required to resolve included tag/variable `cvt_...` types;
  also preserve the complete intended `builtInVariable` enabled set;
- for manual same-container merge intended for GTM View Changes, preserve
  existing object names and do not apply broad naming standardization in that
  JSON; produce a direct GTM/API/MCP step or a separate final-state artifact for
  naming;
- when a full cleanup draft exists, generate the final review patch with
  `scripts/gtm_make_merge_patch.py` or an equivalent reconstruction check;
- keep object IDs unique and references valid after additions, deletions,
  renames, and consolidations;
- compare missing variable, trigger, setup-tag, and teardown-tag references
  before and after generation so pre-existing built-in/internal references are
  not confused with new breakage;
- run the generated file through the same inventory/dependency checks as a fresh
  export before delivery; this is a self-audit gate, not an external
  workspace/export check;
- include safe trigger, variable, tag, folder, naming, and consolidation changes,
  not only the first high-confidence payload fix;
- omit unrelated `customTemplate` objects in manual same-container merge patches
  unless no included object needs them; when included objects use tag/variable
  `cvt_...` types, include the complete intended custom-template set and verify
  dependency-only templates are byte-for-byte unchanged;
- include unchanged folder objects when changed tags, triggers, or variables
  keep `parentFolderId`; otherwise GTM import can reject the file with unknown
  folder errors;
- include unchanged custom template objects when included tags or variables use
  `cvt_...` template types; otherwise GTM import can reject the file with
  unknown entity type errors. Include the complete intended template set rather
  than a partial subset to avoid template delete/add churn;
- include the complete `builtInVariable` array when the source or cleanup
  draft has enabled built-in variables; otherwise GTM import can interpret the
  missing layer as an empty enabled set;
- when replacement/additive objects are used for same-container import, include
  an old-to-new replacement map, the consumer updates made in the JSON, and the
  old objects to decommission after Preview/debug QA;
- confirm no active GA4/current Google mapping depends on UA Enhanced Ecommerce
  paths unless the verified mapper and outgoing payload evidence are documented;
- confirm trigger/tag/variable names match actual behavior and scope, such as
  `form_submit` groups using form-submit triggers and `purchase` groups using
  purchase events;
- confirm no cleaned full export contains trigger groups with exactly one
  child trigger. For same-container merge patches, confirm consumers are mapped
  to the child trigger and remaining single-member groups are explicit
  route-limited delete candidates;
- confirm custom HTML tags that define conversion/helper functions either call
  or register those functions, or are listed as deferred with owner/runtime
  evidence needed;
- confirm page-specific duplicate `PageView` tags are removed, converted to the
  vendor's official funnel event, or deferred with dataLayer/runtime evidence;
- confirm duplicate configurations, unused objects, and consolidation-obsolete
  objects are resolved or listed as intentional residuals with blockers;
- include or attach the completion ledger showing every mandatory workstream as
  `Done`, `Deferred`, `Not applicable`, or `User-excluded`;
- write a concise change log with changed objects, deleted or replaced objects,
  consolidation-obsolete objects, and deferred objects with blockers, using the
  exact `Change Log Columns` schema from `report-templates.md` unless the user
  explicitly requested a different schema;
- recommend import into a new GTM workspace and Preview/debug validation before
  publishing.

## Rollback And Verification

Before ending:

- confirm the previous export/version can restore the prior state;
- produce a post-change export or inventory summary;
- verify references for every deleted/renamed object;
- verify representative tags in Preview/debug or document why browser validation
  was unavailable;
- state publish/version status, usually `Not published`.

## Stop Conditions

Stop and ask the user when:

- workspace/account/container IDs differ from the approved target;
- an API write returns unexpected full-object diffs;
- dependency sweep finds a consumer not covered by the plan;
- consent timing, legal requirements, or dataLayer semantics conflict with the
  plan;
- an operation lacks route, aggressiveness, dependencies, QA method, or rollback;
- the operation requires a higher aggressiveness level than approved;
- generated importable JSON fails parse/reference/duplicate/unused/naming/GA4
  self-QA and the residual issue cannot be documented as intentional;
- a cleaned full export still contains active single-member trigger groups,
  or a merge patch remaps consumers but fails to document that actual deletion
  requires direct GTM/API cleanup or overwrite/new-container JSON;
- the selected cleanup route is known but the operation table uses the wrong
  mutation style, such as JSON-style replacement objects for direct GTM cleanup
  when safe in-place updates are possible, or direct-style in-place assumptions
  for same-container import JSON when import conflicts are likely;
- the user expects GTM View Changes to show existing elements as modified but
  the JSON applies broad renaming or replacement/additive objects that will show
  add/delete churn;
- a requested or produced change log does not match the required template
  columns and the user did not explicitly approve a different schema;
- import preview shows unchanged custom templates as delete/add churn and those
  templates are neither intentional template changes nor required schema
  dependencies for included `cvt_...` tag/variable types;
- manual same-container merge JSON contains unchanged object arrays that pollute
  the workspace change preview, unless the objects are required folder/custom
  template schema dependencies, the `builtInVariable` enabled set, or the user
  explicitly requested a full export artifact;
- importable JSON contains `parentFolderId` values without matching folder
  objects in the imported file;
- importable JSON contains included tag/variable `cvt_...` types without
  matching `customTemplate` definitions in the imported file;
- pageview tags for the same vendor require different consent patterns and the
  rationale is unclear;
- write quota/rate limits become unstable;
- rollback evidence is missing.

Never publish or create a GTM version unless the user explicitly asks for that
action.
