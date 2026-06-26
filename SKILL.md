---
name: gtm-container-audit-cleanup
description: Audit, clean, and standardize Google Tag Manager web or server-side containers from exported container JSON, GTM API/UI evidence, Tag Assistant observations, or implementation screenshots. Use when an agent is asked to review GTM governance, container installation, one tag gateway patterns, consent mode, GA4/ecommerce, marketing pixels, server-side tagging, custom HTML/JavaScript, naming conventions, duplicate or consolidatable tags/triggers/variables, obsolete elements, cleaned importable container JSON, or cleanup plans. Compatible with Codex, Claude Code, Gemini, and other agents that can read Markdown. Default to a complete deep audit; mutate only after explicit user approval; never publish or create GTM versions unless explicitly requested.
---

# GTM Container Audit Cleanup

Use this skill to audit and clean a Google Tag Manager container with a
repeatable, evidence-based workflow. Treat this Markdown folder as an
agent-neutral operating guide: no step depends on Codex-only behavior, hidden
memory, or a specific runtime.

## Operating Modes

- **Audit only**: Inspect evidence, understand object semantics, classify
  findings, identify consolidation opportunities, and recommend actions. This is
  the default when writes are not approved.
- **Cleanup plan**: Convert findings into an ordered roadmap with
  dependencies, risks, and expected verification.
- **Approved cleanup**: Modify GTM only after explicit approval, a dedicated
  workspace, a fresh export/snapshot, and the mutation playbook.
- **Importable JSON cleanup**: Generate a valid GTM container import/export JSON
  file for the user to import manually. This means a GTM-compatible `.json`
  container file, not a Markdown report or code block containing JSON. Treat
  manual same-container import as conflict-sensitive unless the user says they
  will overwrite or import into a new container.
- **Report generation**: Produce a technical audit table, executive summary,
  stakeholder report, cleanup plan, or change log.

If the user has not clearly approved GTM writes, stay in audit-only or planning
mode.

## Route-Specific Cleanup Strategy

Choose the mutation strategy from the execution route before creating the final
operation set:

- **Direct GTM/MCP/API cleanup**: create a new workspace first, then prioritize
  modifying existing tags, triggers, variables, folders, and templates in place
  when this is safe. Preserve IDs, history, permissions, and references. Create
  replacement objects only when the object represents a new reusable concept, an
  in-place edit would be riskier than a staged migration, or GTM/API limits make
  in-place correction unsafe.
- **Importable JSON cleanup for manual same-container merge**: prepare for GTM
  import conflict handling. It is acceptable to create finalized replacement or
  additive objects, update consumers inside the JSON, and provide an old-to-new
  replacement/decommission map instead of forcing every existing object to be
  edited in place. This avoids hard-to-resolve import conflicts and empty-value
  errors. GTM merge conflicts are name-based, so broad renaming in JSON import
  will appear as add/delete churn rather than clean in-place modifications. If
  the user needs GTM's View Changes review, generate a name-preserving review
  patch and defer naming standardization to direct GTM/API/MCP or a separate
  final-state artifact. For human review, generate a minimal merge patch that
  includes changed tags, triggers, variables, folders, and templates plus schema
  dependencies required to import those changed objects. Omit unchanged object
  arrays so GTM workspace changes are not polluted by untouched elements, but
  keep referenced folder definitions and the complete `customTemplate` set when
  GTM needs it to resolve `parentFolderId` or `cvt_...` entity types. Preserve
  the complete intended `builtInVariable` enabled set; omitting that layer can
  be interpreted by GTM import as disabling built-in variables.
- **Importable JSON cleanup for overwrite or new-container import**: a full
  cleaned export may update/delete existing objects directly, because
  same-container conflict resolution is not the primary constraint.

If the user asks for JSON but does not specify the import mode, assume manual
same-container merge, state that assumption, and document the conflict strategy.

Use `references/operation-schema.md` before preparing any cleanup plan,
operation table, direct GTM/MCP/API write, or importable JSON. It defines the
cleanup aggressiveness levels, route decision matrix, operation fields, scenario
playbooks, and regression gates.

## Depth And Completeness Defaults

Default to the deepest complete audit and cleanup the evidence supports. Do not
choose a lighter or conservative scope unless the user explicitly asks for a
quick audit, a sample, a narrow layer, or a minimal fix.

Use `cleanup` as the single operational term. Treat related user phrasing as a
cleanup request, not as a separate mode: run the audit first, then apply or
prepare all safe audit-driven improvements across
tags, triggers, variables, folders, templates, consent routing, ecommerce
payloads, custom code, naming, unused objects, exact duplicates, and similar
consolidatable patterns.

Naming standardization is mandatory in every cleanup. It may be
deferred only when the user explicitly excludes it or when unclear business
tokens make safe renaming impossible; in that case, document the blocker and the
exact names that need owner clarification.

Every proposed final name must be unique within its GTM object layer. GTM cannot
reliably support duplicate names for tags, triggers, variables, or folders, and
duplicate proposed names are poor maintenance practice. When two objects share
the same vendor and event role, add a meaningful suffix such as scope, trigger
event, page context, consent category, destination ID suffix, sequence role,
market, product range, variant, or `Legacy`/`Paused`/`Decommission candidate`.
Use an object ID suffix only as a temporary audit placeholder when the real
business distinction is unknown, and mark the blocker.

Treat Google Analytics/event/ecommerce tracking as GA4 or current Google tag
tracking by default. Classify a Google analytics object as Universal Analytics
only when the tag type, property ID, explicit user instruction, or verified
legacy migration evidence proves that it is truly UA. UA is sunset; do not
create or preserve active UA ecommerce mappings unless the user explicitly asks
for a legacy exception and the report marks the risk.

Use conservative judgment only at the individual-change level. If a specific
change lacks enough business, CMP/legal, vendor-platform, or runtime evidence,
defer that change with a concrete blocker and required evidence. Do not use that
blocker to reduce the overall audit or cleanup scope.

Audit depth and mutation aggressiveness are separate. The audit should be deep
by default. Execution should use `Standard` cleanup by default, escalate to
`Deep` or `Transformational` only after explicit approval, and downgrade to
`Conservative` only when the user requests minimal risk or evidence is thin.

## Mandatory Completion Ledger

For every audit, cleanup plan, cleanup run, or importable JSON run, maintain a
completion ledger. Do not rely on an implied checklist.

The ledger must cover these mandatory workstreams:

- scope and evidence freshness;
- full inventory for tags, triggers, variables, folders, templates, and consent
  settings;
- dependency map, including custom HTML/JavaScript references;
- structured operation schema when a cleanup plan or mutation is requested;
- official documentation map for GA4 and every meaningful vendor/event family;
- Google event classification, with ambiguous Google Analytics events treated
  as GA4/current Google tag rather than UA;
- official dataLayer/event payload format map for GA4 standard and ecommerce
  events, not only tag UI settings;
- deep semantic review for high-risk and shared tags, triggers, and variables;
- standard ecommerce variable checks;
- missing standard events and dataLayer readiness;
- naming convention and naming standardization;
- one tag gateway and consolidation review;
- currently unused, consolidation-obsolete, and deferred objects;
- tag payload, trigger, variable, folder, template, consent, custom-code, and
  naming cleanup decisions;
- mutation route, route-specific cleanup strategy, rollback source, import
  conflict strategy when applicable, and validation results when cleanup is
  requested;
- generated JSON self-QA when an importable container is produced;
- regression checks for route-specific hazards, including same-container JSON
  add/delete churn, built-in variable omission, partial custom-template layers,
  and missing schema dependencies;
- change log and deferred blocker summary.

Each ledger row must be marked `Done`, `Deferred`, `Not applicable`, or
`User-excluded`. `Deferred` requires affected objects, exact blocker, required
evidence, risk, and next action. Do not mark a workstream complete just because
one example or one vendor family was checked.

Before final delivery, run a final coverage check:

- No mandatory workstream is blank or silently skipped.
- Every layer has either changes, findings, or a documented reason for no
  change.
- Naming standardization is applied or blocked with explicit object-level
  reasons.
- Official documentation was checked for every material vendor/event family, or
  the missing source is documented after checking bundled references and
  searching the internet for official vendor documentation.
- Every Google analytics/ecommerce object is classified as GA4/current Google
  tag or an explicit UA exception; no UA Enhanced Ecommerce path remains as an
  active GA4 mapping without a verified mapper and outgoing payload proof.
- Standard ecommerce variables and their consumers were reviewed.
- Trigger, tag, and variable names match their actual logic; for example, a
  `form_submit` trigger group must contain form-submit logic, not a purchase
  trigger.
- Naming standardization covers every tag, trigger, variable, and folder in
  scope, not only examples or high-risk objects. Mixed trigger prefixes such as
  `Didomi`, `Block`, `TR`, `TG`, and `Trigger` are resolved to the chosen
  convention or documented with object-level blockers.
- Proposed and applied final names are unique within each layer. If a naming
  pattern would produce duplicates, the plan adds meaningful suffixes that
  explain the actual distinction between objects, or marks the affected names as
  blocked pending business clarification.
- No trigger group contains only one trigger after cleanup. Map every
  consuming tag directly to the child trigger, then delete the group for direct
  GTM/API or overwrite/new-container JSON. For same-container merge JSON, where
  deletion by omission is not reliable, mark the group as a delete candidate and
  provide the overwrite/direct-deletion artifact or instruction.
- Every rename/delete/update has a dependency sweep, including `setupTag` and
  `teardownTag` `tagName` references after tag renames.
- Generated importable JSON has no new missing references and no unresolved
  duplicate/unused candidates unless documented as intentional.
- Cleanup operations match the selected route: direct GTM cleanup modifies
  existing objects in place when safe, while same-container import JSON may use
  replacement/additive objects with a decommission map to avoid import conflicts.
- Same-container JSON intended for GTM View Changes preserves existing tag,
  trigger, variable, folder, and template names for modified existing objects.
  Do not combine full naming standardization with a View Changes JSON and then
  claim the result will review as in-place modifications; GTM merge conflicts
  are name-based. Provide a separate final-standardized artifact or direct
  GTM/API/MCP plan for naming.
- For same-container merge/review JSON, unchanged objects are omitted from the
  import patch except schema dependencies required by changed objects: folder
  definitions required by `parentFolderId` references and, when any included
  tag/variable uses a custom-template `type` such as `cvt_123_456`, the complete
  intended `customTemplate` set. Verify dependency-only objects are byte-for-byte
  unchanged unless intentionally edited, and explain why they are present in the
  import file.
- Preserve the complete `builtInVariable` array in importable JSON whenever the
  source or cleanup draft has enabled built-in variables. Treat it as the
  container's enabled built-in-variable set, not ordinary unchanged noise.
- Generated importable JSON passes a final self-audit as a fresh artifact:
  parses as GTM JSON, has unique IDs, resolves trigger, variable, setup-tag, and
  teardown-tag references, covers all layers, applies naming or documents
  blockers, and lists every residual issue before delivery.
- Any produced change log matches the `Change Log Columns` in
  `references/report-templates.md` exactly, unless the user explicitly asks for
  a different schema.

If the user asks for a short answer, create the full ledger in the report or
workbook and summarize only the status in chat.

## Next-Step Discipline

At the end of every completed audit, cleanup-plan phase, cleanup phase,
JSON generation phase, QA phase, or handoff, state the recommended next step.
Make it specific to the current status, such as owner decision, runtime QA,
cleanup route selection, GTM workspace creation, importable JSON generation,
change-log preparation, or publish readiness review.

When a step is blocked, the next step must name the missing evidence, decision,
or access needed. When a step completes cleanly, the next step must name the
next executable action and whether it requires user approval. Do not end a
deliverable with only findings, files, or a generic "let me know" close.

## Agent Portability Contract

Follow these rules in Codex, Claude Code, Gemini CLI, or any similar agent:

- Read `SKILL.md` first, then load only the referenced files needed for the task.
- Use available local tools, browser tools, GTM API clients, MCP connectors, or
  manual evidence supplied by the user; do not require a specific toolchain.
- Prefer exported GTM container JSON for reproducible first-pass analysis.
- Summarize large inventories into counts, object names, IDs, dependencies, and
  evidence snippets. Avoid pasting whole container exports into chat.
- Mark assumptions, confidence, and missing evidence explicitly.
- Keep all recommendations reversible unless the user asks for final execution.

## Resource Routing

- Read `references/audit-rubric.md` for the complete audit checklist, severity
  model, cleanup heuristics, and classification rules.
- Read `references/operation-schema.md` when turning audit findings into a
  cleanup plan, selecting aggressiveness, choosing direct GTM/MCP/API versus
  JSON, preparing an operation table, or validating route-specific risks.
- Read `references/container-json-guide.md` when analyzing exported GTM JSON or
  creating scalable inventory, dependency, and semantic-role tables from API/UI
  data.
- Read `references/source-map.md` when checking modern GTM, GA4, consent mode,
  server-side tagging, UA, Google Optimize assumptions, or official vendor
  event/payload documentation.
- Read `references/mutation-playbook.md` immediately before any create, update,
  rename, delete, or batch cleanup.
- Read `references/report-templates.md` before delivering audit results,
  cleanup plans, final handoffs, or change logs.
- When Python is available and a GTM export is provided, use
  `scripts/gtm_export_inspect.py` to accelerate inventory, duplicate,
  dependency, unused-candidate, and ecommerce-variable discovery. Treat script
  output as audit hints that still require semantic review.
- Use `scripts/gtm_diff_operations.py` when comparing an original export to a
  cleanup draft or post-change export. It emits structured operations and can
  produce change-log-shaped CSV.
- Use `scripts/gtm_validate_artifact.py` before delivering any generated JSON or
  after a direct cleanup readback. Select the route mode explicitly.
- When producing a manual same-container merge JSON from a full cleanup draft,
  use `scripts/gtm_make_merge_patch.py` to emit a minimal patch containing only
  changed objects and to validate that original export plus patch reconstructs
  the cleaned state.
- When producing a same-container JSON intended for GTM View Changes, use
  `scripts/gtm_make_name_preserving_review_patch.py` and state that naming
  standardization is deferred from that artifact.

## Intake

Ask for or infer the minimum context needed:

- GTM account/container name plus `accountId`, `containerId`, and workspace or
  exported version if available.
- Website domains, key page types, ecommerce status, app/SPA/PWA behavior, and
  relevant markets or regions.
- Whether the task covers web GTM, server-side GTM, or both.
- Current evidence source: exported container JSON, GTM API access, UI
  screenshots, Tag Assistant output, page source, crawl output, or stakeholder
  notes.
- Consent/CMP stack and applicable privacy regions, such as EEA, UK, Brazil,
  California, or internal policy zones.
- Known naming convention, ownership model, release process, and previous audit
  or cleanup decisions.

Do not reuse stale IDs, stale exports, or prior assumptions without saying so.

## Evidence Standards

Classify every meaningful check as:

- `Correct`: Evidence supports the current setup.
- `Issue`: Evidence shows broken, risky, duplicate, non-compliant, or obsolete
  behavior.
- `Needs improvement`: Functional but hard to maintain, fragile, inconsistent,
  or inefficient.
- `Not applicable`: The check does not apply to this business, container, or
  scope.
- `More info needed`: The evidence is insufficient or a business/legal decision
  is required.

Attach a confidence level: `High`, `Medium`, or `Low`. Prefer object names plus
IDs, exact trigger/filter conditions, consent settings, custom code snippets, or
observed browser behavior over generic descriptions.

## Workflow

1. **Confirm scope and mode**. Establish whether this is audit-only, planning,
   or approved cleanup.
2. **Load the right references**. Start with `audit-rubric.md`; add JSON,
   sources, mutation, or reporting references only when needed.
3. **Build inventory**. Inventory tags, triggers, variables, folders,
   templates, consent settings, workspaces/versions when relevant, and website
   implementation evidence. For large exports, run the bundled inspection
   script when available.
4. **Map dependencies**. Connect tags to firing/blocking triggers, trigger
   groups, setup/teardown tags, variables, custom templates, and custom
   HTML/JavaScript references.
5. **Map official documentation contracts**. Identify every tag/vendor/event
   family and use official documentation as the default source of truth for
   standard event names, website/dataLayer event payload format, required and
   recommended parameters, data types, value formats, base/event sequencing, and
   validation method. First use the bundled source references when the vendor is
   listed. If a vendor, CMP, template, or event family is not pre-included in the
   skill references, search the internet for that vendor's official
   documentation before judging payload correctness. If no official source is
   available after searching, document the search, say so, and lower confidence.
   For Google Analytics/event/ecommerce tracking, default to GA4/current Google
   tag contracts unless the evidence explicitly proves a UA exception.
6. **Profile object semantics**. For each meaningful tag, trigger, and variable,
   infer the intended business role, consumed dataLayer fields, output shape,
   vendor payload fields, consent gate, page/event context, and downstream
   dependency. Do not stop at object counts.
7. **Validate GA4 dataLayer format before variables**. For every GA4 standard or
   ecommerce event, compare the current website/dataLayer event payload to the
   official GA4 event schema before judging or creating GTM variables. For GA4
   ecommerce, verify that event-level fields such as `transaction_id`, `value`,
   `currency`, `tax`, `shipping`, `coupon`, and `items` exist in the expected
   current event context and that `items` is an array of GA4 item objects using
   fields such as `item_id`, `item_name`, `item_brand`, `item_category`, `price`,
   and `quantity`. Treat old Universal Analytics Enhanced Ecommerce paths such
   as `ecommerce.purchase.actionField.*`, `ecommerce.purchase.products.*`,
   `ecommerce.add.products.*`, or `ecommerce.detail.products.*` as migration
   evidence, not as correct GA4 paths, unless there is explicit mapping evidence
   and Preview/debug proves the outgoing GA4 payload is correct.
8. **Validate standard ecommerce logic**. Always inspect common ecommerce
   variables such as revenue, total price, total quantity, tax, shipping,
   transaction ID, product IDs, names, categories, item arrays, checkout
   products, and purchase products. Confirm paths, formulas, output types,
   multi-item handling, null/`NaN` behavior, and every consuming tag field.
9. **Audit missing standard events and dataLayer readiness**. For GA4 and each
   vendor with official event documentation, identify missing useful standard
   events and whether the website/dataLayer already provides the required
   event, item, value, currency, ID, and consent data. Treat missing dataLayer
   readiness as a blocker before creating tags.
10. **Infer naming scope carefully**. Use object names to detect country, market,
   language, product range, campaign, or audience scope, but do not assume
   unclear tokens are understood. Ask the user about ambiguous labels such as
   product-range or internal campaign prefixes before judging correctness.
11. **Define the naming convention**. Unless the user provides a house style,
   use `Vendor - Event/role - Scope/detail` for tags, `Utility/type - Event or
   condition - Scope/detail` for triggers, and `VariableTypeAcronym - Variable
   name/source path` for variables. Decide final names before creating helpers,
   reusable triggers, or replacement tags. Validate proposed names for
   uniqueness within each layer before publishing the audit plan, operation
   table, rename map, or cleanup artifact.
12. **Detect gateway and consolidation patterns**. Identify whether the container
   uses a one tag gateway, server-side gateway, lookup-table gateway, shared
   vendor loader, or repeated one-tag-per-market/event pattern. Cluster exact
   duplicates, single-member trigger groups, and similar objects that could be
   consolidated safely.
13. **Audit by risk area**. Review governance, implementation, security,
   organization, setup hygiene, privacy/consent, GA4, server-side GTM, vendor
   pixels, and Google Ads.
14. **Prioritize**. Rank findings by business impact, data quality impact,
   privacy risk, operational risk, performance impact, and cleanup complexity.
15. **Stage cleanup decisions**. Separate objects that are currently unused from
   objects that become obsolete only after an approved consolidation. Do not
   present the first orphan list as the final cleanup list.
16. **Compile operations**. Convert findings into structured operations with
   route, aggressiveness, dependencies, QA method, rollback, and blockers. Use
   `operation-schema.md`; do not jump from findings directly to writes.
17. **Build the full cleanup set**. For cleanup or importable JSON,
   include every evidence-safe correction, consolidation, deletion candidate,
   naming/folder improvement, trigger cleanup, variable cleanup, tag
   payload fix, and custom code hardening. Do not stop at the first high-risk
   family.
18. **Flatten single-member trigger groups before final naming**. For each
   trigger group with exactly one child trigger, update consuming tags to use the
   child trigger directly, then delete the group in direct GTM/API or
   overwrite/new-container JSON. In same-container merge JSON, document that the
   merge patch can remap consumers but cannot reliably delete omitted existing
   objects; provide a direct/overwrite deletion path.
19. **Apply naming last when behavior changes exist**. After payload fixes,
   consolidation, deletion, and folder moves are decided, rename remaining
   objects according to the final convention and produce a before/after naming
   map. Re-scan all `{{Variable Name}}` references, especially inside custom HTML
   and custom JavaScript, plus setup/teardown `tagName` references after tag
   renames.
20. **Recommend next actions**. Separate no-write recommendations,
   user/business decisions, consolidation candidates, and approved mutation
   candidates.
21. **Confirm execution route**. When the user approves cleanup, ask whether
   they want direct GTM execution through available
   tools/MCP/API or a GTM-compatible import JSON file they can import manually.
22. **Select route-specific cleanup strategy**. For direct GTM/MCP/API cleanup,
   preserve and modify existing objects in place when safe. For manual
   same-container import JSON, use a conflict-aware replacement/additive strategy
   when it reduces GTM import conflicts, emit only changed objects in the import
   file, and document old-to-new decommission mapping. For overwrite/new-container
   JSON, direct object updates/deletions may be appropriate.
23. **Stop before writes**. If mutation is requested, read
   `mutation-playbook.md`, prepare a plan, and ask for explicit approval unless
   approval has already been given for the exact operations.
24. **Self-QA generated outputs**. Before delivering an importable JSON, inspect
   the generated file as if it were a fresh export: run inventory, dependency,
   duplicate, unused, naming, GA4 dataLayer, and residual-issue checks. This is
   a self-audit gate, not an external workspace/export check.
25. **State the next step**. After each completed audit or workflow phase,
   state the concrete next step, including whether the user must approve a
   route, decide an owner/business question, provide evidence, or allow
   execution.
26. **Report clearly**. Use `report-templates.md` and provide a reproducible
   audit trail.

## Non-Negotiable Safety Rules

- Do not publish, submit, or create a GTM version unless the user explicitly
  requests that exact action.
- Do not delete tags, triggers, variables, or templates based on age alone.
- Do not mark unused objects as safe to delete until a dependency sweep covers
  tags, triggers, variables, trigger groups, setup/teardown tags, templates, and
  custom HTML/JavaScript bodies.
- Do not finalize deletion candidates until consolidation/refactor proposals
  have been evaluated; consolidation can make currently used objects obsolete.
- Do not turn an approved cleanup into a minimal correction pass
  unless the user explicitly asked for minimal or conservative changes.
- Do not generate a cleaned importable JSON that only fixes one object
  family when evidence-safe cleanup exists in triggers, variables, tags,
  folders, naming, duplicates, or consolidation candidates.
- Do not treat Google analytics/event/ecommerce tracking as Universal Analytics
  by default. UA objects are deprecated exceptions; ambiguous Google events are
  GA4/current Google tag candidates until proven otherwise.
- Do not leave active UA Enhanced Ecommerce paths such as
  `ecommerce.purchase.actionField.*`, `ecommerce.purchase.products.*`,
  `ecommerce.add.products.*`, or `ecommerce.detail.products.*` as GA4 mappings
  unless a verified mapper and outgoing GA4 payload evidence exist.
- Do not modify production/default workspaces when a dedicated workspace can be
  used.
- Do not perform direct GTM cleanup in an existing/default workspace. Create a
  new workspace first, unless the user explicitly accepts a different path after
  being warned.
- Do not proceed with direct cleanup when GTM workspace creation is blocked by a
  quota or active-workspace limit. Alert the user and offer the importable JSON
  route or a workspace cleanup decision.
- Do not apply the same mutation assumptions to both cleanup routes. Direct
  GTM/MCP/API cleanup should preserve and update existing objects where safe;
  manual same-container import JSON may use replacement/additive objects to
  reduce conflict resolution and empty-value import errors.
- Do not change consent behavior, dataLayer semantics, or vendor payload shape
  without identifying the privacy/business impact.
- Do not invent custom JavaScript variables or synthetic calculations to bypass
  missing standard website/dataLayer fields when official documentation expects
  those fields to be sent by the site. Flag the missing dataLayer/event contract
  as the issue and mark tag creation as blocked until the dataLayer is ready.
- Do not "fix" GA4 ecommerce by mapping Universal Analytics Enhanced Ecommerce
  paths into GA4 unless the migration/mapping is explicit, documented, and
  verified at the outgoing GA4 payload boundary. Prefer a website/dataLayer fix
  when the official GA4 event payload is missing.
- Do not rewrite custom HTML by replacing variable references with hardcoded
  values unless the user explicitly approved that semantic change.
- Do not create helper variables, triggers, or tags without defining their final
  naming pattern and all consumers first; avoid proposing elements that will
  immediately need to be renamed or re-referenced.
- Do not let names contradict behavior. A tag, trigger, or variable whose name
  says `purchase`, `form_submit`, a country, a product range, or a consent
  vendor must have configuration that enforces that meaning, or it must be
  renamed/deferred with a blocker.
- Do not skip naming standardization in an approved cleanup unless
  the user excludes it or the required scope/product/campaign meaning is
  unknown. If skipped, list the exact blocker and target naming convention.
- Do not preserve a trigger group with exactly one child trigger as a cleaned
  object. Remap consumers to the child trigger and delete the group when the
  selected route supports deletion; otherwise list it as a route-limited delete
  candidate with the required direct/overwrite cleanup path.
- Do not deliver an importable cleanup JSON until the generated-file self-QA
  gate passes or every failed check is listed as a residual blocker.
- Do not create custom template churn. Identical custom templates should not be
  deleted, re-added, or included in a same-container merge patch as part of a
  tag/trigger/variable cleanup.
- Do not omit folder definitions referenced by `parentFolderId` in an importable
  JSON patch unless folder assignment is intentionally being removed. GTM
  validates folder IDs inside the imported file and rejects unknown folders.
- Do not omit custom template definitions referenced by included tag or variable
  `type` values like `cvt_123_456` in an importable JSON patch. GTM validates
  those template entity types inside the imported file and rejects unknown custom
  template IDs even when the template content itself is unchanged. When a
  `customTemplate` layer is required for a same-container import file, include
  the complete intended template set rather than a partial subset, because
  partial template layers can create delete/add churn.
- Do not omit `builtInVariable` from an importable JSON patch when the source
  export has enabled built-in variables. GTM import can treat omission as an
  empty enabled set, disabling variables such as Page URL, Event, Click, and
  Form variables.
- Do not treat legal/privacy advice as final. Flag legal-dependent decisions for
  the user's privacy/legal owner.

## Output Expectations

For audits, include:

- executive summary;
- evidence sources and freshness;
- inventory counts;
- semantic-role and consolidation summary for tags, triggers, and variables;
- official documentation contracts checked for GA4 and vendor tags;
- official GA4 dataLayer/event payload format checked per standard event;
- missing standard events and dataLayer readiness blockers;
- standard ecommerce variable logic summary, especially broken formulas,
  unexpected output types, and affected tag consumers;
- findings table with status, severity, confidence, evidence, impact,
  recommendation, and mutation requirement;
- cleanup roadmap grouped by risk and dependency;
- open questions and decisions needed.

For approved cleanups, include:

- approved scope and workspace coordinates;
- execution route: direct GTM/MCP/API cleanup or importable GTM container JSON;
- route-specific cleanup strategy, including import mode and conflict handling
  for JSON deliverables;
- for same-container merge JSON, confirmation that the import file contains only
  changed objects and omits unchanged templates/arrays;
- operations performed and skipped;
- structured operation table with change IDs, route, aggressiveness, QA, and
  rollback;
- complete changed-vs-deferred summary by layer, including tags, triggers,
  variables, templates, folders, consent, naming, and consolidation;
- old-to-new replacement map and decommission plan when the JSON route creates
  replacement/additive objects for manual same-container import;
- naming convention applied plus a before/after rename map for tags, triggers,
  variables, and folders;
- explicit blocker and required evidence for every material deferred cleanup;
- verification evidence from a fresh post-change inventory;
- generated JSON self-QA status, including parse/reference/duplicate/unused,
  naming, GA4 dataLayer, and residual blocker checks when applicable;
- change log using the exact template columns from
  `references/report-templates.md` when a change log is requested or produced;
- rollback path;
- publish/version status, usually `Not published`.

Every audit, phase handoff, cleanup result, generated JSON delivery, or QA
summary must include `Recommended next step`. This next step must be concrete
and approval-aware.

End audit and cleanup handoffs with the change-log question from
`references/report-templates.md`.
