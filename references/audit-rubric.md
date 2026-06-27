# Audit Rubric

Use this reference for the complete human and technical audit. It is designed to
work from exported GTM JSON, GTM API reads, GTM UI screenshots, Tag Assistant,
page source, crawl output, or stakeholder-provided evidence.

## Contents

- Severity Model
- Evidence Sources
- Inventory Checklist
- Audit Completeness Contract
- Measurement Truth Before Cleanup
- Official Documentation Contract
- Deep Object Semantics
- Semantic Model Protocol
- Semantic Logic Consistency
- Name-Based Scope Inference
- Mandatory Naming Standardization
- One Tag Gateway Detection
- Domain Checklists
- Cleanup Completeness
- Consolidation Review Order

## Severity Model

Use the highest applicable severity:

| Severity | Use when |
| --- | --- |
| Critical | Tags fire in clear violation of consent/legal requirements, major conversion/analytics collection is broken, or production mutation could cause immediate data loss. |
| High | Data quality, privacy, attribution, or revenue tracking is materially wrong or highly likely to become wrong. |
| Medium | Setup works but is fragile, duplicated, inconsistent, hard to maintain, or likely to cause future implementation mistakes. |
| Low | Minor hygiene, naming, documentation, or operational improvement. |
| Info | Observation with no recommended change, or evidence retained for context. |

Use priority separately from severity when planning work:

`P0 Now`, `P1 This sprint`, `P2 Planned cleanup`, `P3 Backlog`, `Decision needed`.

For examples and edge-case calibration, read `severity-calibration.md`. Keep
severity, priority, and confidence separate; do not lower severity merely
because evidence confidence is low.

## Evidence Sources

Record source freshness for each audit:

- Exported container JSON: export time, container/version/workspace.
- GTM API/UI: account, container, workspace/version, read time.
- Website evidence: URLs, environment, browser, consent state, Tag Assistant or
  network observations, crawl date.
- Stakeholder evidence: owner, date, and confidence.

If evidence conflicts, prefer the freshest source for the exact object and note
the conflict.

## Inventory Checklist

Inventory and count:

- accounts, containers, workspaces, versions, and user permissions when access
  permits;
- tags, tag types/vendors, firing triggers, blocking triggers, setup/teardown
  relationships, consent settings, and sequencing;
- triggers, event types, filters, trigger groups, exceptions, and connected tags;
- variables, variable types, dataLayer keys, lookup tables, custom JS bodies, and
  consumers;
- templates and template update state;
- folders, notes, and naming patterns;
- website/container installation evidence;
- server-side GTM clients, tags, transformations, endpoints, and monitoring when
  in scope.

## Audit Completeness Contract

Default to a complete audit unless the user explicitly asks for a reduced scope.
Large containers still require complete coverage; use normalized tables,
clustering, hashes, and grouped findings to scale the work rather than skipping
object families.

The checklist is a minimum floor, not a ceiling. Agents may do more when the
evidence supports it, but must not do less than the mandatory checks. If a
required check cannot be completed from the available evidence, record it as
`Deferred` or `More info needed` with the exact blocker, affected objects, risk,
required evidence, and next action.

For every audit, cover:

- all tags, triggers, variables, folders, templates, consent settings, and
  built-in variables;
- measurement diagnosis for meaningful conversion, media, ecommerce, lead,
  custom-code, server-side, multi-market, gateway, and consolidation families;
- exact duplicates and near duplicates across tags, triggers, variables, custom
  code, templates, folders, and naming patterns;
- currently unused objects and objects that become obsolete after consolidation;
- object semantics, consumer dependencies, output shape, and trigger context for
  every high-risk or shared object;
- semantic-object matrix rows for meaningful/high-impact objects, with depth
  tier, trigger-context status, configuration/source logic status,
  consent/server status, evidence level, semantic status, and blocker or linked
  finding/operation;
- standard ecommerce variables and all consuming tags;
- custom HTML/JavaScript reference safety;
- gateway and consolidation opportunities where repeated patterns exist.

Sampling is allowed only to explain repeated low-risk hygiene patterns in the
report. It is not a reason to skip dependency mapping or cleanup eligibility
checks for the full container.

Semantic completion gate: a workstream is not complete until semantic
validation is complete or explicitly deferred with a blocker. Inventory,
dependency coverage, hashes, URL extraction, duplicate grouping, script output,
and reference maps are evidence inputs, not semantic validation. Do not mark any
meaningful object family `Done` when the only completed work is inventory or
dependency mapping.

For template tags, do not copy every parameter into the report. Inspect the
meaningful configuration fields for the event/vendor family, infer likely
outgoing behavior, and decide whether it fits the event name, business role,
trigger context, variable output types, and destination/platform expectation.
When a field looks correct only because its variable has a similar name, inspect
the variable configuration or mark runtime/dataLayer proof required.

Reconcile counts before delivery for each meaningful object family:

- total source objects;
- inventoried objects;
- dependency-mapped objects;
- semantically validated objects;
- cleanup-decision objects;
- deferred objects;
- not applicable objects;
- user-excluded objects;
- unresolved objects.

The semantic coverage formula must reconcile:
`total = semantically validated + deferred + not applicable + user-excluded`.
Any nonzero unresolved count means the audit or cleanup plan is incomplete until
the row is resolved or explicitly deferred with a blocker.

If any mandatory gate fails, deliver the result as `Incomplete / blocked`. Do
not soften the failure into a normal limitation, and do not omit the affected
family from the cleanup plan.

Required depth rule: if this rubric, `semantic-object-matrix.md`, or a scenario
playbook makes D1, D2, or D3 necessary, complete that depth from export/API or
supplied evidence before delivery. Do not use `Deferred`, `More info needed`, or
runtime uncertainty to skip source-path, formula, trigger, tag-parameter,
custom-code, or custom-template inspection that is available in the export.
Only D4 runtime proof can remain deferred without making the audit incomplete.

## Measurement Truth Before Cleanup

Treat the container as a measurement system before treating it as an object
cleanup problem. For every meaningful family, infer:

- business model and decision outcome;
- conversion hierarchy, such as primary conversion, micro-conversion,
  engagement, audience, utility, or server-forwarding event;
- vendor/platform role, such as reporting, bidding, attribution, audience,
  enhanced matching, CRM/affiliate handoff, publisher ads, or server routing;
- expected data contract: event name, trigger context, value, currency, IDs,
  item/object shape, lead/form type, consent, market/product scope, and
  deduplication.

Do not propose cleanup for a meaningful object only because it looks unused,
duplicated, inconsistently named, or technically awkward. First decide whether
it preserves a distinct business, market, consent, vendor, server-side, or
platform-optimization role. If intent is unclear, ask an owner question or mark
runtime/server/dataLayer proof required.

## Official Documentation Contract

For every meaningful tag family, identify the official implementation, website
event payload, dataLayer, or event documentation before judging payload
correctness. Treat official docs as the default source of truth for standard
events, required parameters, recommended parameters, data types, value formats,
base/event sequencing, deduplication, and validation methods unless the user
explicitly provides a different business rule.

Use `source-map.md` as the starting index for frequently consulted official
documentation URLs, then re-open or re-search the official source when current
product behavior matters. If the vendor, CMP, template, or event family is not
listed in the skill references, search the internet for that vendor's official
documentation before judging the tag, trigger, variable, or payload. Do not skip
documentation lookup just because the vendor is uncommon or absent from the
reference map.

Apply this especially to:

- GA4 recommended events, ecommerce events, official website/dataLayer payload
  format, item arrays, event-level value and currency, transaction IDs, and
  item-scoped parameters;
- Google Ads, Floodlight, Microsoft UET, and server-side Google tagging;
- Meta Pixel/CAPI, TikTok Pixel/Events API, Snapchat Pixel/CAPI, Pinterest Tag,
  LinkedIn Insight Tag/CAPI, Reddit, X/Twitter, affiliate pixels, and other
  media tags when official docs are available;
- CMP and consent documentation when consent routing depends on a vendor or CMP
  contract.

For each vendor/event family, record:

- official source checked, access date, and confidence;
- standard event name expected by the platform;
- required and recommended parameters;
- expected website/dataLayer payload structure and expected GTM Data Layer
  Variable paths when GTM reads those parameters;
- expected data types and shapes, such as number, string, ISO currency code,
  array of IDs, array of item objects, or hashed identifier;
- expected source of truth: website dataLayer/current event, tag template field,
  server event, first-party cookie, or vendor API;
- validation method, such as Tag Assistant, vendor helper, network request, event
  manager, or platform diagnostics.

Do not fill documentation gaps with guesswork. If official documentation is
unavailable or blocked after checking bundled references and searching the
internet, say so, record the search path or failed official-source lookup, use
current export/runtime evidence carefully, and lower confidence.

Do not create custom JavaScript as a shortcut when the official implementation
expects the website/dataLayer to already send the parameter. For example, if an
official ecommerce event requires an item array, value, currency, price, or
quantity from the current ecommerce action, the correct finding may be
"dataLayer event is incomplete" rather than "create a GTM variable that guesses
the value." Helper variables are appropriate only to transform a complete source
payload into the vendor-required shape, add guards, normalize names, or avoid
duplication without changing the source-of-truth contract.

For Google Analytics/event/ecommerce tracking, default to GA4/current Google tag
documentation. Classify an object as Universal Analytics only when the tag type,
property ID, explicit user instruction, or verified migration evidence proves a
UA exception.

## Deep Object Semantics

Do not treat the audit as a count-and-status exercise. For every tag, trigger,
and variable that affects consent, ecommerce, media, conversion, custom code, or
shared routing, record:

- intended business role;
- event/page context where it should run;
- vendor or destination platform;
- market, language, hostname, product line, campaign, or model scope;
- consumed variables and dataLayer paths;
- output shape: scalar, array, object, boolean, joined string, URL, ID list, or
  vendor payload object;
- expected downstream consumer and field format;
- consent/privacy dependency;
- evidence that the object is correct, questionable, or redundant.

For low-risk hygiene objects, sample then expand when patterns repeat. For
high-risk objects, inspect individually.

Every meaningful object family must have semantic status: `Keep`, `Fix`,
`Consolidate`, `Delete candidate`, `More info needed`, or `Not applicable`.
Do not mark a family complete when it has only inventory rows, dependency rows,
or code hashes.

## Semantic Model Protocol

Use `semantic-model-protocol.md` after dependency mapping for conversion,
media, ecommerce, lead, server-side, multi-market, custom-code, or complex
cleanup tasks. Build the model internally before judging optimization patterns.

At minimum, infer business objective, user action, event/context, GTM
implementation, data source, destination payload, platform use, and evidence or
blocker. Use the model to find missing business logic, such as lead type,
product category, value model, item array, deduplication ID, consent forwarding,
or market scope that the container appears to need but does not reliably
provide.

## Semantic Logic Consistency

Use `semantic-logic-checks.md` before finalizing findings or cleanup operations
for media, ecommerce, lead, conversion, custom-code, shared-variable, value, or
quantity logic.

At minimum, verify that:

- variable names, source paths, formulas, output types, event context, and
  consumers agree;
- totals, quantities, values, item arrays, content IDs, lead types, and product
  categories are not built from fixed indexes, stale dataLayer history, wrong
  field types, or unrelated events;
- a variable reused across vendors is valid for every consuming vendor field;
- trigger and tag names do not promise a business action, country, product,
  lead type, or consent state that the configuration does not enforce.

Only report the result when it changes a finding, blocker, operation, or QA
requirement. Do not expand stakeholder reports with scratch reasoning.

## Name-Based Scope Inference

Use object names as evidence of intended scope, then verify whether the
configuration enforces that scope.

Look for:

- country, market, or language codes such as `FR`, `DE`, `UK`, `CH`, `AT`,
  `BE`, `IT`, or `NL`;
- hostnames, domains, regions, currencies, or store names;
- product range, model, brand, or client-specific acronym tokens;
- campaign, audience, vendor, agency, or test suffixes;
- prefixes that may describe ownership, deployment phase, or legacy migration.

For each scoped object, compare the name to the actual trigger filters,
variables, lookup table rows, custom code conditions, and vendor payload. Flag
names that imply a country, product range, or audience that is not enforced by
the object.

When a token is unclear, do not invent the meaning. Ask the user whether it is a
product range, campaign, market, internal audience, legacy label, or something
else before treating the object as wrong or safe to consolidate.

## Mandatory Naming Standardization

Naming standardization is a mandatory cleanup step. Perform it after
semantic fixes, consolidation design, and deletion decisions are known, so the
remaining objects receive stable final names and do not need a second rename.

Read `naming-standardization.md` before producing rename recommendations,
cleanup operations, direct GTM/MCP/API writes, or importable JSON involving
names. The naming hierarchy is: user model first, inferred local convention
second, default pattern only when no reliable local convention exists. Preserve
meaningful local acronyms and official casing, but standardize semantically
equivalent object families and keep every proposed final name unique inside its
GTM layer.

## One Tag Gateway Detection

When applicable, identify whether the container uses a gateway pattern:

- a single custom HTML or template tag dispatches many vendors/events;
- one Google tag, Floodlight tag, or server-side endpoint forwards many event
  types;
- a lookup-table-driven tag chooses vendor IDs, event names, or payload fields;
- one shared loader/base tag supports many event tags;
- one server-side GTM endpoint or first-party tagging URL acts as a collection
  gateway.

For each gateway candidate, document:

- trigger coverage and consent gate;
- how event type, market, product line, vendor ID, and payload are selected;
- whether the gateway preserves vendor-required payload shape;
- whether gateway failures would break many downstream tags;
- observability and QA method;
- whether consolidation into a gateway would make current tags/triggers/variables
  obsolete.

Prefer gateway patterns only when they reduce real duplication without hiding
ownership, consent logic, QA responsibility, or vendor-specific payload rules.

## Domain Checklists

Read `audit-domain-checks.md` for governance, web implementation, custom code,
architecture, setup hygiene, consent, Google events, server-side GTM, vendor
pixels, cleanup heuristics, and scenario-specific intelligence. Use this rubric
for severity, evidence, semantic depth, and cleanup completeness; use the domain
checklists for area-specific coverage.

## Cleanup Completeness

When the user asks for cleanup, standardization, or cleanup JSON,
apply the full cleanup workflow. Do not limit the output to a small correction
patch unless the user explicitly asked for a minimal fix.

For each layer, decide what is evidence-safe to change now, what is safe only
after consolidation, and what must be deferred:

- **Tags**: payload corrections, consent routing, duplicate vendor loaders,
  repeated event tags, native/template migration candidates, sequencing, paused
  or orphaned tags, and naming/folder consistency.
- **Triggers**: exact duplicates, near duplicates, repeated country/hostname/path
  filters, repeated CMP/vendor consent rules, unused triggers, trigger groups,
  exceptions, and trigger naming.
- **Variables**: duplicate dataLayer paths, duplicate custom JS, fixed-index
  ecommerce variables, output-shape helpers, lookup/regex table candidates,
  unused variables, and variables made obsolete by tag/trigger consolidation.
- **Custom code**: repeated snippets, missing guards, unsafe hardcoding,
  incorrect serialization/escaping, stale dataLayer reads, and custom HTML that
  should become native/template tags.
- **Folders and naming**: unused or misleading folders, mixed naming axes,
  names that encode a scope not enforced by configuration, and final names for
  new reusable helpers. Naming standardization is not optional in a cleanup; if
  it is not applied, document why and provide the target convention.

For importable GTM JSON, the generated file should include all evidence-safe
cleanup from these layers. The change log must separately list
deferred items with the exact blocker, such as unclear business scope, missing
CMP/legal decision, missing runtime evidence, or vendor-platform validation
needed.

Custom code cleanup cannot be reduced to one generic row when custom-code
objects exist. The plan must include object-level semantic review and cleanup
decisions, or explicitly defer the affected objects with blockers.

Before delivery, self-audit the generated cleanup artifact as a fresh container
export. The self-audit must confirm:

- every layer has changes, findings, or a documented reason for no change;
- no active GA4/current Google mapping relies on UA Enhanced Ecommerce paths
  without verified mapper evidence;
- naming standardization is applied or object-level blockers are listed;
- trigger/tag/variable names match actual logic and scope;
- references resolve, IDs are unique, and no new missing references exist;
- exact duplicates, unused objects, and consolidation-obsolete objects are
  resolved or documented as intentional residuals;
- residual blockers are listed before calling the JSON import-ready.

## Consolidation Review Order

Use this order before proposing cleanup:

1. Map current dependencies and exact consumers.
2. Understand dataLayer event schemas and vendor payload expectations.
3. Identify exact duplicates.
4. Identify similar objects that can be consolidated without changing semantics.
5. Design final helper variables, trigger patterns, and tag payload contracts.
6. Decide final naming before new objects are proposed.
7. Recompute obsolete triggers and variables after the consolidation design.
8. Split deletion candidates into currently unused and consolidation-obsolete.
9. Validate final names against final logic so a `form_submit`, `purchase`,
   country, product-range, or consent-vendor name cannot point to unrelated
   conditions.

Do not start by deleting every unused object if those objects may help explain
the existing pattern or serve as references for the consolidation design.
