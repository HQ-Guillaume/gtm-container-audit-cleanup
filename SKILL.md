---
name: gtm-container-audit-cleanup
description: GTM cleanup intelligence for Google Tag Manager web or server-side containers from exported container JSON, GTM API/UI evidence, Tag Assistant observations, runtime/network evidence, or implementation screenshots. Use when an agent is asked to produce deep cleanup plans, deterministic hygiene findings, semantic business hygiene checks, custom HTML/JavaScript/code optimization, measurement logic validation, GA4/ecommerce and media payload cleanup, consent/server routing review, naming/consolidation/obsolete-object cleanup, runtime QA, change logs, cleaned importable JSON, or approved GTM mutations. Compatible with Codex, Claude Code, Gemini, and other agents that can read Markdown. Build a source model first, use three independent cleanup lenses, mutate only after explicit approval, and never publish or create GTM versions unless explicitly requested.
---

# GTM Cleanup Intelligence

Use this skill to produce useful, execution-ready GTM cleanup. Act as a
GTM-focused web analyst, but keep cleanup usefulness as the product center:
find mechanical hygiene issues, semantic measurement issues, and custom-code
technical issues separately, then reconcile them into clear cleanup operations.
Treat this Markdown folder as an agent-neutral operating guide: no step depends
on Codex-only behavior, hidden memory, or a specific runtime.

## Analyst North Star

Diagnose whether the GTM container supports the business measurement objectives
correctly and whether the container is clean enough to maintain safely. Cleanup
is the remediation format. Before proposing renames, deletions, consolidation,
helper variables, custom-code rewrites, JSON patches, or direct GTM mutations,
establish the measurement intent:

- site/business model and primary decision outcomes;
- conversion hierarchy: primary conversion, micro-conversion, engagement,
  audience, remarketing, utility, or server-forwarding signal;
- vendor/platform role: reporting, bidding, attribution, audience, exclusion,
  enhanced matching, CRM, affiliate, publisher ads, or server routing;
- expected data contract: event name, trigger context, value, currency, ID,
  item/object shape, lead/form type, consent, market, and deduplication.

Do not clean first and analyze later. If the business or measurement role of a
meaningful object is unclear, record the owner question or runtime/server
blocker before deciding whether to keep, fix, consolidate, rename, or delete.
The final cleanup plan must still say what is expected after cleanup and what
exact next action is safe.

## Operating Modes

- **Audit only**: inspect evidence and findings. Default when writes are not approved.
- **Cleanup plan**: convert findings into an ordered roadmap with risks and QA.
- **Approved cleanup**: modify GTM only after explicit approval, a dedicated
  workspace, rollback export, and `mutation-playbook.md`.
- **Importable JSON cleanup**: generate a GTM-compatible `.json`; same-container
  import is conflict-sensitive.
- **Runtime QA/reporting**: plan QA or produce audits, plans, reports, and
  change logs. If writes are not approved, stay in audit/planning mode.

## Route-Specific Cleanup Strategy

Choose the mutation strategy before creating operations: direct GTM/MCP/API
with a new workspace, manual same-container JSON merge following
`import-json-policy.md`, or overwrite/new-container JSON when conflict
resolution is not a constraint. If JSON mode is unspecified, assume manual
same-container merge. Use `operation-schema.md` for operation tables.

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

Naming standardization is mandatory in every cleanup plan/run unless the user
excludes it or safe naming tokens are blocked. Follow
`references/03-rules/naming-standardization.md`; the visible plan must include a
naming/architecture row, and final names must be unique within each layer.

Treat GTM internal/system references as normal evidence, not anomalies:
recognize `{{_event}}` in Custom Event filters and high-range system trigger IDs
such as `2147479553`/`2147479573`; do not raise missing-reference findings for
them.

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

Use a contract-driven three-lens architecture: raw export/API evidence ->
source model navigation map only -> `deterministic_findings.json`,
`semantic_findings.json`, `technical_code_findings.json` ->
`reconciled_operations.json` -> user-facing plan plus hidden proof tabs. Each
lens must verify raw evidence independently before reconciliation.
The source model cannot create, suppress, downgrade, or summarize findings; it
only tells each lens where raw objects, fields, references, and edges are.

## Mandatory Completion Ledger

For every audit, cleanup plan, cleanup run, JSON run, handoff, or change log,
maintain the ledger defined in `completion-gates.md`. Rows must be `Done`,
`Deferred`, `Not applicable`, or `User-excluded`; `Deferred` requires affected
objects, blocker, required evidence, risk, and next action.

A completed full audit or cleanup plan must include a Semantic Object Matrix,
Custom Code Semantic Review when code objects exist, and operation packets or an
equivalent `reconciled_operations` table behind every visible cleanup row.
User-facing plans should surface only findings, blockers, operations, expected
outcomes, QA, and representative summaries.

Before final delivery, run the final coverage check from
`completion-gates.md`. If a report or workbook includes a reconciliation table,
validate it with `scripts/gtm_audit_gate_check.py`. If any mandatory gate fails,
label the deliverable `Incomplete / blocked` and list failed workstreams,
affected objects, blockers, risk, required evidence, and next action.

## Next-Step Discipline

End every audit, plan, cleanup, JSON, QA, or handoff with one concrete next
action: missing evidence/decision/access if blocked, or the next executable
approval, QA, route, workspace, JSON, change-log, or publish-readiness step.

## Agent Portability Contract

Follow these rules in Codex, Claude Code, Gemini CLI, or any similar agent:
read `SKILL.md` first; load only needed references; use available local, browser,
GTM API/MCP, or manual evidence; prefer exported JSON for reproducibility; report
large inventories as counts, IDs, dependencies, and snippets; mark assumptions,
confidence, and missing evidence; keep recommendations reversible unless the
user asks for final execution.

## Resource Routing

Load only the files required by scope:

| Need | Read/use |
| --- | --- |
| Skill purpose, users, questions resolved, inputs, outputs, acceptance criteria, non-goals | `references/01-skill/purpose.md`, `references/01-skill/users-and-questions.md`, `references/01-skill/inputs-outputs.md`, `references/01-skill/acceptance-criteria.md`, `references/01-skill/non-goals.md` |
| Every full audit, cleanup plan, cleanup run, JSON artifact, handoff, or change log | `references/03-rules/protected-audit-pipeline.md`, `references/03-rules/completion-gates.md`, `references/03-rules/execution-assurance.md`, `references/03-rules/audit-rubric.md`, `references/03-rules/audit-domain-checks.md`, `references/03-rules/policy-register.md` |
| Explicitly quick, sample, narrow, or limited audit | `references/03-rules/limited-audit-protocol.md` |
| GA4/current Google tag, ecommerce, standard variables, missing events | `references/03-rules/audit-ga4-ecommerce.md`, `references/03-rules/source-map.md`, `references/03-rules/vendor-playbooks.md` |
| CMP, consent mode, browser-to-server transport, server-side caution | `references/03-rules/audit-consent-server.md`, `references/02-commands/runtime-qa-templates.md` |
| Media/vendor pixels, affiliate, publisher ads, payload quality | `references/03-rules/audit-media-vendors.md`, `references/03-rules/vendor-playbooks.md`, `references/03-rules/source-map.md` |
| Exported JSON source model, dependency graph, and scalable source tables | `references/03-rules/container-json-guide.md`, `scripts/gtm_source_model.py`, `scripts/gtm_export_inspect.py` |
| Semantic business logic and object-depth evidence | `references/03-rules/semantic-model-protocol.md`, `references/03-rules/semantic-object-matrix.md`, `references/03-rules/semantic-logic-checks.md` |
| Naming review, rename map, case/acronym rules, rename QA | `references/03-rules/naming-standardization.md` |
| Cleanup patterns, route choice, aggressiveness, operations, mutation, JSON | `references/03-rules/optimization-patterns.md`, `references/03-rules/operation-schema.md`, `references/03-rules/import-json-policy.md`, `references/03-rules/mutation-playbook.md` |
| Client-facing severity, reports, workbooks, cleanup plans | `references/03-rules/severity-calibration.md`, `references/03-rules/human-problem-taxonomy.md`, `references/03-rules/report-templates.md`, `references/03-rules/workbook-architecture.md` |
| Semantic summaries, proof tabs, cleanup-plan readability | `references/03-rules/summary-quality.md`, `references/03-rules/workbook-architecture.md` |
| Change logs | `references/03-rules/change-log-template.md` |
| Validation commands, forward-testing, and runtime QA | `references/02-commands/validation-commands.md`, `references/02-commands/forward-test-prompts.md`, `references/02-commands/runtime-qa-templates.md` |

Use scripts as deterministic gates or transformers:
`scripts/gtm_audit_package_build.py` for the default protected evidence package,
`scripts/gtm_source_model.py` for the source-model navigation map,
`scripts/gtm_baseline_audit.py` for protected deterministic cleanup findings,
`scripts/gtm_custom_code_extract.py` for custom-code fact extraction and
technical code health/security/optimization signals,
`scripts/gtm_semantic_source_scan.py` for an independent semantic source scan
that reads the export directly instead of consuming the baseline,
`scripts/gtm_findings_reconcile.py` for three-lens finding-to-operation
reconciliation and operation-packet validation,
`scripts/gtm_audit_gate_check.py` for reconciliation and `--strict-evidence`,
`scripts/gtm_audit_package_check.py <export.json> <workbook.xlsx>` for export to
workbook coverage, `scripts/gtm_diff_operations.py` for operation/change-log
diffs, `scripts/gtm_validate_artifact.py` for generated JSON/readback QA,
`scripts/gtm_make_merge_patch.py` for minimal same-container merge JSON,
`scripts/gtm_make_name_preserving_review_patch.py` for GTM View Changes review
patches, and `scripts/check_release.py` before packaging or release.

## Intake

Ask for or infer the minimum context needed: GTM account/container/workspace or
exported version, web/server scope, domains/page types/ecommerce/app behavior,
markets, current evidence source, consent/CMP and privacy regions, naming
convention, ownership/release process, and previous audit/cleanup decisions.

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
3. **Build the source model navigation map**. Prefer `gtm_audit_package_build.py`; otherwise use `gtm_source_model.py` or equivalent direct export/API review to map objects, fields, trigger edges, variable sources, consumers, custom-code references, and unresolved edges.
4. **Gate source-model coverage**. Treat the model as a map, not the evidence source. If references or edges are unresolved, mark exact blockers before trusting cleanup lenses. Do not derive cleanup decisions from the source model alone, and do not let it suppress or downgrade findings from the three independent raw-source scans.
5. **Run the protected deterministic baseline from the source export**. Run or
   reproduce `gtm_baseline_audit.py` as a mechanical cleanup scan and preserve
   it as `deterministic_findings.json`. It must
   surface basic cleanup findings, including outdated Universal
   Analytics-style setup objects and naming/architecture standardization,
   before any summarization. It must recognize GTM internal/system references
   before missing-reference logic runs. Reconcile every finding as cleanup,
   exception, runtime blocker, owner decision, or not applicable.
6. **Extract custom-code facts and technical code health from the source
   export**. Run or reproduce `gtm_custom_code_extract.py` for Custom HTML,
   Custom JavaScript, and custom templates and preserve it as
   `technical_code_findings.json`. Use the extracted facts and technical
   health/security/optimization signals as D3 inputs and hardening candidates,
   not business-semantic judgment.
7. **Run the independent semantic source scan from the same source export**.
   Run or reproduce `gtm_semantic_source_scan.py` and preserve it as
   `semantic_findings.json`. This semantic layer must
   inspect the export directly and produce its own rows; do not feed it only
   summarized deterministic findings. Keep deterministic and semantic scan
   artifacts separate until reconciliation.
8. **Reconcile three cleanup lenses into operation packets**. Normalize
   deterministic, semantic, and technical findings by
   `layer + object_id + object_name + object_type + code/config hash`.
   Produce `reconciled_operations.json` or an equivalent table with current
   behavior, problem, why it matters, expected clean state, exact proposed
   action, preconditions, QA, rollback, confidence, blocker, priority, and
   source finding IDs from each lens. The visible cleanup plan must be compiled
   from this reconciliation layer, not directly from raw scan rows.
9. **Map official documentation contracts**. Identify every tag/vendor/event
   family and use official docs as the source of truth for standard events,
   payloads, required fields, data types, sequencing, and validation. Use bundled
   sources first; if a vendor/CMP/template/event family is missing, search
   official documentation, document failures, and lower confidence. Default
   ambiguous Google analytics/ecommerce objects to GA4/current Google tag.
10. **Build the measurement diagnosis**. Model site/business type, primary
   outcomes, conversion hierarchy, vendor/platform roles, and expected data
   contracts. This is the analyst gate before cleanup; use
   `semantic-model-protocol.md`.
11. **Build the semantic model**. Model business objective, user action,
   event/context, GTM implementation, data source, destination payload, platform
   use, and evidence/blockers for meaningful object families.
12. **Build the full D1-D3 proof queue and extract literal behavior first**. For
   a full audit, every tag, trigger, variable, custom template, and referenced
   configuration branch requires D3 export/API/config/code review. Record exact
   object-specific behavior before categorizing it: actual inputs, actual logic,
   actual output or side effect, actual consumers, and expected consumer
   meaning. Close a queue row only when this evidence is recorded in the matrix
   or custom-code review. Do not replace literal behavior with broad categories
   such as `computed value`, `browser side effect`, or `payload transformer`.
13. **Trace recursively and build the synergy graph**. Build the internal graph
   from business action to trigger, tag, variable/helper, source path/formula,
   custom-code side effect, vendor field, destination, consent, and server
   routing. Do not stop at `tag uses variable X`: trace every tag field,
   trigger filter, variable reference, lookup input, custom-code placeholder,
   and template field to its terminal source or a D4-only runtime blocker. Use
   the graph to detect contradictions, duplicate/similar conditions,
   shared-variable misuse, loader overlap, consent inconsistency,
   browser/server duplication, and consolidation opportunities. Cleanup
   operations are not allowed until the relevant graph path is understood or
   explicitly blocked.
14. **Run semantic logic and sibling-field checks**. Compare resolved sibling
   fields and sibling objects by source, condition, return type, consumer
   meaning, and official/vendor/business expectation. Surface every actionable
   object-level finding, blocker, operation, documented exception, or runtime QA;
   keep normal config details in compact proof rows, not the cleanup plan.
15. **Validate GA4 dataLayer format before variables**. Compare Google events to
    official schemas and treat UA Enhanced Ecommerce paths as migration evidence
    unless a verified mapper proves the outgoing GA4 payload.
16. **Validate standard ecommerce logic**. Inspect revenue, value, quantity,
    transaction, item/product, checkout, purchase, formulas, output types,
    multi-item behavior, null/`NaN`, and every consuming tag field.
17. **Audit missing standard events and dataLayer readiness**. Identify useful
    missing standard events only after confirming the website/dataLayer can
    provide required event, item, value, currency, ID, and consent data.
18. **Infer naming scope carefully**. Use names as clues for market, language,
    product, campaign, or audience scope, but ask about unclear tokens before
    judging correctness.
19. **Define the naming convention and route architecture**. Follow user style
    first; otherwise infer the dominant local convention, preserve meaningful
    acronyms/case, and decide whether to normalize the local convention or use
    the integrated default. If no reliable local convention exists, use the
    default: tags `Vendor - Event - Scope`, triggers `CE/PV/LC/FORM/Block/TG -
    event_or_condition`, variables `DLV/cJS/LT/RT/Util - name`, folders by
    area. Include the selected policy, confidence, examples, and rename/route
    blockers in the cleanup plan, with detailed candidates in hidden proof tabs.
20. **Detect gateway and consolidation patterns**. Identify whether the container
   uses a one tag gateway, server-side gateway, lookup-table gateway, shared
   vendor loader, or repeated one-tag-per-market/event pattern. Cluster exact
   duplicates, single-member trigger groups, and similar objects that could be
   consolidated safely.
21. **Select optimization patterns**. Use `optimization-patterns.md` to evaluate
   hygiene, structural, semantic, and strategic optimization ideas without
   flattening business meaning or over-consolidating.
22. **Classify client-to-server transport tags before judging Google IDs or
   consent triggers**. Server URLs, first-party endpoints, S2S naming,
   placeholder IDs, or consent/routing parameters make Google tags possible
   browser-to-server transport tags. Require server-container validation before
   editing IDs, blocking triggers, paused state, or destination assumptions.
23. **Audit by risk area**. Review governance, implementation, security,
   organization, setup hygiene, privacy/consent, GA4, server-side GTM, vendor
   pixels, and Google Ads.
24. **Prioritize**. Rank findings by business impact, data quality impact,
   privacy risk, operational risk, performance impact, and cleanup complexity.
25. **Stage cleanup decisions**. Separate objects that are currently unused from
   objects that become obsolete only after an approved consolidation. Do not
   present the first orphan list as the final cleanup list.
26. **Compile operations**. Convert reconciled findings into structured
   operations with route, aggressiveness, dependencies, QA method, rollback, and
   blockers. Use `operation-schema.md`; do not compile cleanup operations for
   meaningful objects whose business/measurement role has not been diagnosed.
   Do not emit a visible cleanup row unless an operation packet backs it or the
   row is explicitly a blocked investigation item.
27. **Build the full cleanup set**. For cleanup or importable JSON,
   include every evidence-safe correction, consolidation, deletion candidate,
   naming/folder improvement, trigger cleanup, variable cleanup, tag
   payload fix, and custom code hardening. Do not stop at the first high-risk
   family.
28. **Flatten single-member trigger groups before final naming**. Remap consumers
    to the child trigger and delete or document route-limited deletion according
    to the selected cleanup route.
29. **Apply naming last when behavior changes exist**. After fixes and
    consolidation decisions, produce a before/after map and re-scan variable plus
    setup/teardown references, especially inside custom code.
30. **Recommend next actions**. Separate no-write recommendations,
   user/business decisions, consolidation candidates, and approved mutation
   candidates.
31. **Confirm execution route**. When the user approves cleanup, ask whether
   they want direct GTM execution through available
   tools/MCP/API or a GTM-compatible import JSON file they can import manually.
32. **Select route-specific cleanup strategy**. For direct GTM/MCP/API cleanup,
   preserve and modify existing objects in place when safe. For manual
   same-container import JSON, use a conflict-aware replacement/additive strategy
   when it reduces GTM import conflicts, emit only changed objects in the import
   file, and document old-to-new decommission mapping. For overwrite/new-container
   JSON, direct object updates/deletions may be appropriate.
33. **Stop before writes**. If mutation is requested, read
   `mutation-playbook.md`, prepare a plan, and ask for explicit approval unless
   approval has already been given for the exact operations.
34. **Self-QA generated outputs**. Before delivering an importable JSON, inspect
   the generated file as if it were a fresh export: run inventory, dependency,
   duplicate, unused, naming, GA4 dataLayer, and residual-issue checks. This is
   a self-audit gate, not an external workspace/export check.
35. **Reconcile completion gates**. Before final delivery, check the ledger
   against `completion-gates.md` and `execution-assurance.md`; run the package
   and gate validators when their inputs exist. If a gate fails, label the
   deliverable `Incomplete / blocked` with failed rows, blockers, risk, required
   evidence, and next action.
36. **Translate operations into human problem rows**. Use
   `human-problem-taxonomy.md` and `summary-quality.md` before
   delivering Semantic Object Matrix rows, Custom Code Review rows, cleanup
   plans, change logs, or handoffs. Proof summaries must say category,
   source/input, logic/action, output or side effect, and judgment. User-facing
   plans should show only what the user needs to decide, approve, debug, or QA.
37. **Optimize workbook information architecture**. Use
   `workbook-architecture.md`: default to compact visible `Summary` and
   `Cleanup Plan` tabs, with inventory, baseline, D3, custom-code, QA, and
   validation proof in hidden but readable tabs. Use parent/detail rows for
   grouped findings and never collapse distinct object issues into a vague
   family row. For a real post-cleanup change log, use a separate summary tab
   plus a detailed change log tab with one row per modified object or modified
   field/dependency.
38. **State the next step and report clearly**. Use `report-templates.md`, provide a reproducible audit trail, and name whether the user must approve a route, decide an owner/business question, provide evidence, or allow execution.

## Non-Negotiable Safety Rules

- Do not publish, submit, or create a GTM version unless the user explicitly
  requests that exact action.
- Do not delete tags, triggers, variables, or templates based on age alone.
- Do not propose or execute cleanup before diagnosing the business and
  measurement role of every meaningful affected object. If the role is unclear,
  create a blocker or owner question, not a cleanup guess.
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
- Do not let the semantic layer depend on an oversummarized deterministic
  baseline. The semantic scan must read the source JSON/API/config/code itself,
  produce its own proof rows, and only then reconcile with deterministic
  findings.
- Do not let the workbook or report builder bypass the three-lens artifacts.
  The final cleanup plan must consume reconciled operations that link back to
  deterministic, semantic, and technical source findings when those lenses are
  in scope.
- Do not combine findings by prose alone. Match objects by layer, ID, name,
  type, and code/config hash; resolve conflicts explicitly before presenting a
  cleanup action.
- Do not expose deterministic baseline rows, semantic proof rows, technical
  code scan fields, raw code, or internal agent notes as the normal cleanup plan.
  Translate them into plain-language findings, expected change outcomes,
  recommended actions, QA steps, and blockers for non-specialist stakeholders.
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

Use `human-problem-taxonomy.md`, `report-templates.md`, `workbook-architecture.md`,
`change-log-template.md`, and `summary-quality.md` for output schemas and wording.
Keep cleanup plans and change logs end-user facing; put matrices, raw code/config,
validator traces, and scratch reasoning in proof artifacts. Expose evidence freshness,
coverage, semantic status, blockers, QA, route, rollback/publish status,
deferred decisions, and a concrete next execution decision.
