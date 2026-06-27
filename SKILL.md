---
name: gtm-container-audit-cleanup
description: Audit, clean, and standardize Google Tag Manager web or server-side containers from exported container JSON, GTM API/UI evidence, Tag Assistant observations, runtime/network evidence, or implementation screenshots. Use when an agent is asked to review GTM governance, container installation, one tag gateway patterns, consent mode, GA4/ecommerce, marketing pixels, server-side tagging, custom HTML/JavaScript, semantic business logic, variable formula sanity, business objective modeling, naming conventions, duplicate or consolidatable tags/triggers/variables, obsolete elements, runtime QA, change logs, cleaned importable container JSON, or cleanup plans. Compatible with Codex, Claude Code, Gemini, and other agents that can read Markdown. Default to a complete deep audit; mutate only after explicit user approval; never publish or create GTM versions unless explicitly requested.
---

# GTM Container Audit Cleanup

Use this skill to audit and clean a Google Tag Manager container with a
repeatable, evidence-based workflow. Treat this Markdown folder as an
agent-neutral operating guide: no step depends on Codex-only behavior, hidden
memory, or a specific runtime.

## Operating Modes

- **Audit only**: inspect evidence, semantics, findings, and consolidation
  opportunities. Default when writes are not approved.
- **Cleanup plan**: convert findings into an ordered roadmap with risks and QA.
- **Approved cleanup**: modify GTM only after explicit approval, a dedicated
  workspace, rollback export, and `mutation-playbook.md`.
- **Importable JSON cleanup**: generate a GTM-compatible container `.json`, not
  a Markdown/code-block JSON. Manual same-container import is conflict-sensitive.
- **Runtime QA**: plan or run Tag Assistant, browser, network, CMP, server-side,
  and vendor validation.
- **Report generation**: produce audits, stakeholder reports, cleanup plans, or
  change logs. If writes are not approved, stay in audit/planning mode.

## Route-Specific Cleanup Strategy

Choose the mutation strategy before creating operations:

- **Direct GTM/MCP/API**: create a new workspace, then update existing objects
  in place when safe. Follow `POL-106` and `POL-107`.
- **Manual same-container JSON merge**: follow `import-json-policy.md`,
  especially `POL-202` through `POL-208`.
- **Overwrite/new-container JSON**: full cleaned exports may update/delete
  objects because same-container conflict resolution is not the constraint.

If JSON mode is unspecified, assume manual same-container merge and document the
conflict strategy. Use `operation-schema.md` for all operation tables and
`import-json-policy.md` for JSON artifacts.

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

Use `references/naming-standardization.md` for naming hierarchy, local
convention detection, case rules, uniqueness, blockers, and rename QA. Every
proposed final name must be unique within its GTM object layer.

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

Semantic review and runtime proof are separate. Complete required D1-D3 from
export/API/source evidence during the audit; only D4 runtime proof may be
deferred. Missing D1-D3 work is `Incomplete / blocked`, and "review code",
"check variables", or "validate trigger logic" are audit tasks, not cleanup
operations.

## Mandatory Completion Ledger

For every audit, cleanup plan, cleanup run, importable JSON run, final handoff,
or change log, maintain a completion ledger. Read
`references/completion-gates.md` for the required workstreams, phase model,
definition of done, reconciliation counts, and failed-gate handling. Do not rely
on an implied checklist.

Each ledger row must be marked `Done`, `Deferred`, `Not applicable`, or
`User-excluded`. `Deferred` requires affected objects, exact blocker, required
evidence, risk, and next action. Do not mark a workstream complete just because
one example or one vendor family was checked.

Maintain backing evidence artifacts for semantic coverage. A completed full
audit or cleanup plan must include or generate a Semantic Object Matrix and, when
custom HTML, Custom JavaScript, or custom templates exist in scope, a Custom Code
Semantic Review table. These artifacts prove the review happened; the
user-facing plan should surface only findings, blockers, operations, and
representative family summaries.

Before final delivery, run the final coverage check from
`completion-gates.md`. If a report or workbook includes a reconciliation table,
validate it with `scripts/gtm_audit_gate_check.py`. If any mandatory gate fails,
label the deliverable `Incomplete / blocked` and list failed workstreams,
affected objects, blockers, risk, required evidence, and next action.

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

Load only the files required by scope:

| Need | Read/use |
| --- | --- |
| Every full audit, cleanup plan, cleanup run, JSON artifact, handoff, or change log | `references/completion-gates.md`, `references/execution-assurance.md`, `references/audit-rubric.md`, `references/audit-domain-checks.md`, `references/policy-register.md` |
| Explicitly quick, sample, narrow, or limited audit | `references/limited-audit-protocol.md` |
| GA4/current Google tag, ecommerce, standard variables, missing events | `references/audit-ga4-ecommerce.md`, `references/source-map.md`, `references/vendor-playbooks.md` |
| CMP, consent mode, browser-to-server transport, server-side caution | `references/audit-consent-server.md`, `references/runtime-qa-templates.md` |
| Media/vendor pixels, affiliate, publisher ads, payload quality | `references/audit-media-vendors.md`, `references/vendor-playbooks.md`, `references/source-map.md` |
| Exported JSON inventory, dependency graph, and scalable source tables | `references/container-json-guide.md`, `scripts/gtm_export_inspect.py` |
| Semantic business logic and object-depth evidence | `references/semantic-model-protocol.md`, `references/semantic-object-matrix.md`, `references/semantic-logic-checks.md` |
| Naming review, rename map, case/acronym rules, rename QA | `references/naming-standardization.md` |
| Cleanup patterns, route choice, aggressiveness, operations, mutation, JSON | `references/optimization-patterns.md`, `references/operation-schema.md`, `references/import-json-policy.md`, `references/mutation-playbook.md` |
| Client-facing severity, reports, workbooks, cleanup plans | `references/severity-calibration.md`, `references/report-templates.md`, `references/workbook-architecture.md` |
| Semantic summaries, proof tabs, cleanup-plan readability | `references/summary-quality.md`, `references/workbook-architecture.md` |
| Change logs | `references/change-log-template.md` |
| Forward-testing | `references/forward-test-prompts.md` |

Use scripts as deterministic gates or transformers:
`scripts/gtm_audit_gate_check.py` for reconciliation and `--strict-evidence`,
`scripts/gtm_audit_package_check.py <export.json> <workbook.xlsx>` for export to
workbook coverage, `scripts/gtm_diff_operations.py` for operation/change-log
diffs, `scripts/gtm_validate_artifact.py` for generated JSON/readback QA,
`scripts/gtm_make_merge_patch.py` for minimal same-container merge JSON,
`scripts/gtm_make_name_preserving_review_patch.py` for GTM View Changes review
patches, and `scripts/check_release.py` before packaging or release.

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
2. **Load the right references**. Start with `completion-gates.md`,
   `execution-assurance.md`, and `audit-rubric.md`; add JSON, semantic logic,
   sources, vendor playbooks, runtime QA, mutation, or reporting references only
   when needed.
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
6. **Build the semantic model**. Model business objective, user action,
   event/context, GTM implementation, data source, destination payload, platform
   use, and evidence/blockers for meaningful object families.
7. **Populate the semantic object matrix**. For meaningful tags, triggers,
   variables, custom templates, and custom code, assign a depth tier and record
   business role, trigger context, config/code logic, source/output type,
   consent/server status, evidence level, semantic status, blockers, and linked
   findings or operations. Use `semantic-object-matrix.md`. High-impact active
   tags and variables need object rows; repeated low-risk families may use
   family rows plus anomaly rows. A row is not complete when only the name, hash,
   or risk category is filled.
8. **Run semantic logic checks**. Build the internal graph from business action
   to trigger, tag, variable/helper, source path/formula, vendor field, consent,
   and server routing. Surface only actionable findings, blockers, operations,
   documented exceptions, or runtime QA; keep normal config details in the
   matrix, not the cleanup plan.
9. **Validate GA4 dataLayer format before variables**. Compare GA4/current
   Google events to official schemas before judging GTM variables. For ecommerce,
   verify event-level fields and `items` array shape in the current event
   context. Treat UA Enhanced Ecommerce paths as migration evidence unless a
   verified mapper proves the outgoing GA4 payload is correct.
10. **Validate standard ecommerce logic**. Always inspect common ecommerce
   variables such as revenue, total price, total quantity, tax, shipping,
   transaction ID, product IDs, names, categories, item arrays, checkout
   products, and purchase products. Confirm paths, formulas, output types,
   multi-item handling, null/`NaN` behavior, and every consuming tag field.
11. **Audit missing standard events and dataLayer readiness**. For GA4 and each
   vendor with official event documentation, identify missing useful standard
   events and whether the website/dataLayer already provides the required
   event, item, value, currency, ID, and consent data. Treat missing dataLayer
   readiness as a blocker before creating tags.
12. **Infer naming scope carefully**. Use object names to detect country, market,
   language, product range, campaign, or audience scope, but do not assume
   unclear tokens are understood. Ask the user about ambiguous labels such as
   product-range or internal campaign prefixes before judging correctness.
13. **Define the naming convention**. If the user provides a house style or
   examples, follow them. Otherwise, infer the container's dominant convention
   from existing names before using the default patterns. Preserve meaningful
   local acronyms and casing when they are consistently used and semantically
   clear, but standardize inconsistent labels inside the same semantic family.
   Use `naming-standardization.md`; decide final names before creating helpers,
   reusable triggers, or replacement tags, and validate proposed names for
   uniqueness within each layer before publishing artifacts.
14. **Detect gateway and consolidation patterns**. Identify whether the container
   uses a one tag gateway, server-side gateway, lookup-table gateway, shared
   vendor loader, or repeated one-tag-per-market/event pattern. Cluster exact
   duplicates, single-member trigger groups, and similar objects that could be
   consolidated safely.
15. **Select optimization patterns**. Use `optimization-patterns.md` to evaluate
   hygiene, structural, semantic, and strategic optimization ideas without
   flattening business meaning or over-consolidating.
16. **Classify client-to-server transport tags before judging Google IDs or
   consent triggers**. Server URLs, first-party endpoints, S2S naming,
   placeholder IDs, or consent/routing parameters make Google tags possible
   browser-to-server transport tags. Require server-container validation before
   editing IDs, blocking triggers, paused state, or destination assumptions.
17. **Audit by risk area**. Review governance, implementation, security,
   organization, setup hygiene, privacy/consent, GA4, server-side GTM, vendor
   pixels, and Google Ads.
18. **Prioritize**. Rank findings by business impact, data quality impact,
   privacy risk, operational risk, performance impact, and cleanup complexity.
19. **Stage cleanup decisions**. Separate objects that are currently unused from
   objects that become obsolete only after an approved consolidation. Do not
   present the first orphan list as the final cleanup list.
20. **Compile operations**. Convert findings into structured operations with
   route, aggressiveness, dependencies, QA method, rollback, and blockers. Use
   `operation-schema.md`; do not jump from findings directly to writes.
21. **Build the full cleanup set**. For cleanup or importable JSON,
   include every evidence-safe correction, consolidation, deletion candidate,
   naming/folder improvement, trigger cleanup, variable cleanup, tag
   payload fix, and custom code hardening. Do not stop at the first high-risk
   family.
22. **Flatten single-member trigger groups before final naming**. For each
   trigger group with exactly one child trigger, update consuming tags to use the
   child trigger directly, then delete the group in direct GTM/API or
   overwrite/new-container JSON. In same-container merge JSON, document that the
   merge patch can remap consumers but cannot reliably delete omitted existing
   objects; provide a direct/overwrite deletion path.
23. **Apply naming last when behavior changes exist**. After payload fixes,
   consolidation, deletion, and folder moves are decided, rename remaining
   objects according to the final convention and produce a before/after naming
   map. Re-scan all `{{Variable Name}}` references, especially inside custom HTML
   and custom JavaScript, plus setup/teardown `tagName` references after tag
   renames.
24. **Recommend next actions**. Separate no-write recommendations,
   user/business decisions, consolidation candidates, and approved mutation
   candidates.
25. **Confirm execution route**. When the user approves cleanup, ask whether
   they want direct GTM execution through available
   tools/MCP/API or a GTM-compatible import JSON file they can import manually.
26. **Select route-specific cleanup strategy**. For direct GTM/MCP/API cleanup,
   preserve and modify existing objects in place when safe. For manual
   same-container import JSON, use a conflict-aware replacement/additive strategy
   when it reduces GTM import conflicts, emit only changed objects in the import
   file, and document old-to-new decommission mapping. For overwrite/new-container
   JSON, direct object updates/deletions may be appropriate.
27. **Stop before writes**. If mutation is requested, read
   `mutation-playbook.md`, prepare a plan, and ask for explicit approval unless
   approval has already been given for the exact operations.
28. **Self-QA generated outputs**. Before delivering an importable JSON, inspect
   the generated file as if it were a fresh export: run inventory, dependency,
   duplicate, unused, naming, GA4 dataLayer, and residual-issue checks. This is
   a self-audit gate, not an external workspace/export check.
29. **Reconcile completion gates**. Before final delivery, check the ledger
   against `completion-gates.md` and `execution-assurance.md`; run the package
   and gate validators when their inputs exist. If a gate fails, label the
   deliverable `Incomplete / blocked` with failed rows, blockers, risk, required
   evidence, and next action.
30. **Apply summary-quality discipline**. Use `summary-quality.md` before
   delivering Semantic Object Matrix rows, Custom Code Review rows, cleanup
   plans, change logs, or handoffs. Proof summaries must say category,
   source/input, logic/action, output or side effect, and judgment. User-facing
   plans should show only what the user needs to decide, approve, debug, or QA.
31. **Optimize workbook information architecture**. For XLSX cleanup plans,
   default to the compact human view: one visible executive decision summary
   tab and one visible cleanup action plan tab. Add extra visible tabs only when
   the user asks, the workflow truly needs them, or the file is a technical
   appendix rather than an approval plan. Hide proof/technical tabs with normal
   Excel `hidden` state, not `veryHidden`, so validators, future agents, and
   expert reviewers can unhide them. Consolidate findings, roadmap, operations,
   blockers, runtime QA, route, and naming into the action plan. Remove or hide
   duplicated, constant, blank, or validator-only columns from user-facing
   views. Hidden tabs must also be information-clean: remove or hide blank and
   constant proof-only columns where the schema allows it, and rewrite columns
   with repeated text so each retained field has a distinct purpose. Keep
   required proof columns in backing tabs only when validators or cross-agent
   handoff require the schema, and never use that exception to leave duplicate
   human-facing content unchanged.
32. **State the next step**. After each completed audit or workflow phase,
   state the concrete next step, including whether the user must approve a
   route, decide an owner/business question, provide evidence, or allow
   execution.
33. **Report clearly**. Use `report-templates.md` and provide a reproducible
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
- Do not accept a variable formula, helper output, or media payload as correct
  merely because it resolves. Its name, event context, source path, formula,
  output type, and every consuming vendor field must make logical sense.
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
- Do not defer export-level custom-code review to cleanup execution. For every
  active, referenced, risky, or cleanup-relevant Custom HTML tag, Custom
  JavaScript variable, or custom template, inspect the exported code/config
  during audit and record purpose, inputs, outputs, side effects, consent
  assumption, consumers, semantic status, and blocker. Runtime QA may be
  deferred before mutation; code/config inspection may not.
- Do not mark a required D3 object as semantically validated unless source/code
  logic was actually inspected and summarized. `D3 required`, `static scan`,
  `review later`, or `D3/D4 blocked` wording is not completion.
- Do not put a cleanup operation in the plan whose primary work is to "perform
  line-level review", "review custom code", "check the variable config", or
  "validate trigger logic". If that analysis was not performed, mark the audit
  `Incomplete / blocked` for the affected objects instead of presenting it as a
  future cleanup operation.
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
- Do not deliver an importable cleanup JSON until generated-file self-QA passes
  or every failed check is listed as a residual blocker.
- In importable JSON patches, avoid custom template churn, include referenced
  folders, preserve enabled built-in variables, and satisfy GTM validation for
  any included `cvt_*` tag or variable types. Never include unchanged templates
  in a same-container patch unless required for validation; if a
  `customTemplate` layer is required, follow `mutation-playbook.md` and warn
  about possible template delete/add noise.
- Do not treat legal/privacy advice as final. Flag legal-dependent decisions for
  the user's privacy/legal owner.

## Output Expectations

Use `report-templates.md`, `workbook-architecture.md`,
`change-log-template.md`, and `summary-quality.md` for output schemas and
wording. Keep cleanup plans and change logs end-user facing; put matrices,
raw code/config, validator traces, and scratch reasoning in proof artifacts.
Expose evidence freshness, coverage, semantic status, blockers, QA, route,
rollback/publish status, deferred decisions, and a concrete `Recommended next
step`. End audit and cleanup handoffs with the change-log question.
