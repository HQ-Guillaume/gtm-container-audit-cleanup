# Policy Register

Use this file as the stable source for repeated GTM audit and cleanup rules.
Other references may cite these policy IDs instead of restating the full rule.

## Contents

- Core Audit Policies
- Cleanup And Mutation Policies
- JSON Import Policies
- Reporting Policies

## Core Audit Policies

| ID | Policy |
| --- | --- |
| POL-001 | Default to a complete deep audit unless the user explicitly requests a limited scope. A limited execution mode never reduces audit thinking unless scope is explicitly excluded. |
| POL-002 | Do not publish, submit, or create GTM versions unless the user explicitly requests that exact action. |
| POL-003 | Maintain a completion ledger for every audit, cleanup plan, cleanup run, importable JSON run, final handoff, or change log. Failed mandatory gates make the deliverable `Incomplete / blocked`. |
| POL-004 | Use official GA4, GTM, CMP, and vendor documentation as the source of truth for standard event names, dataLayer/event payload format, required/recommended parameters, data types, sequencing, and validation method. If bundled references do not include the vendor, search official documentation. |
| POL-005 | Build a semantic model for meaningful conversion, media, ecommerce, lead, custom-code, server-side, multi-market, or consolidation candidates before judging correctness or optimization. |
| POL-006 | Treat ambiguous Google analytics/event/ecommerce objects as GA4/current Google tag candidates unless evidence proves a UA exception. UA Enhanced Ecommerce paths are migration evidence, not GA4 correctness. |
| POL-007 | Do not accept a variable, helper, custom code block, or media payload as correct merely because it resolves. Its name, event context, source path, formula, output type, and consumers must make logical sense. |
| POL-008 | Names must match behavior. Country, product, campaign, consent, purchase, lead, or form-submit names require matching configuration or a blocker/rename. |
| POL-009 | Export-level semantic review cannot be deferred to cleanup execution. Runtime proof may be deferred before mutation, but audited tags, variables, triggers, custom code, and templates must have semantic evidence or an `Incomplete / blocked` status. |
| POL-010 | Required D1-D3 depth must be completed from available export/API/source evidence. Only D4 runtime proof may be deferred; missing D1-D3 work keeps the audit unresolved/incomplete. |
| POL-011 | Cleanup is downstream of measurement diagnosis. Diagnose business model, decision outcome, conversion hierarchy, platform role, and expected data contract before judging meaningful objects or compiling cleanup operations. |

## Cleanup And Mutation Policies

| ID | Policy |
| --- | --- |
| POL-101 | Cleanup includes every evidence-safe improvement across tags, triggers, variables, folders, templates, consent routing, ecommerce payloads, custom code, naming, unused objects, exact duplicates, and consolidatable patterns. |
| POL-102 | Naming standardization is mandatory in cleanup unless the user excludes it or business tokens are unclear. Follow the user's model first; otherwise infer the dominant local convention and preserve meaningful acronyms/case while standardizing semantic families within each object layer. Proposed names must be unique within each GTM object layer. |
| POL-103 | Stage deletion decisions: separate currently unused objects from objects that become obsolete only after approved consolidation. |
| POL-104 | Do not delete tags, triggers, variables, folders, or templates based on age alone. Complete dependency sweeps must cover triggers, trigger groups, setup/teardown, templates, variables, and custom code references. |
| POL-105 | Flatten single-member trigger groups when the route supports deletion. When it does not, document the route-limited deletion path. |
| POL-106 | Direct GTM/MCP/API cleanup must happen in a new workspace unless the user explicitly accepts a different path after being warned. Stop when workspace quota blocks a safe route. |
| POL-107 | Direct GTM/MCP/API cleanup should preserve and update existing objects in place when safe. Use replacement objects only for new reusable concepts, safer staged migrations, or tool/API constraints. |
| POL-108 | Do not change consent behavior, dataLayer semantics, or vendor payload shape without identifying privacy/business impact and QA. |
| POL-109 | Do not invent GTM-side custom JavaScript to bypass missing official website/dataLayer fields. Mark the website/dataLayer contract as blocked instead. |
| POL-110 | Do not rewrite custom HTML by replacing GTM variable references with hardcoded values unless the user explicitly approved that semantic change. |
| POL-111 | Do not create cleanup operations whose primary action is `review custom code`, `perform line-level review`, `check variables`, or `validate trigger logic`; those are audit tasks, not cleanup actions. |
| POL-112 | Do not propose renames, deletions, consolidation, helper variables, custom-code rewrites, JSON patches, or direct GTM mutations for meaningful objects whose business/measurement role is unclear. Use an owner question, runtime QA requirement, or website/dataLayer/server blocker instead. |

## JSON Import Policies

| ID | Policy |
| --- | --- |
| POL-201 | Ask the user to choose direct GTM/MCP/API execution or importable JSON when cleanup is approved. If JSON mode is unspecified, assume manual same-container merge and state that assumption. |
| POL-202 | Same-container merge JSON is conflict-sensitive because GTM matches conflicts by name. A rename-heavy JSON can show add/delete churn instead of readable modifications. |
| POL-203 | If the user needs GTM View Changes review, create a name-preserving review patch and defer naming standardization to direct GTM/API/MCP or a separate final-state artifact. |
| POL-204 | Same-container final-state JSON may use replacement/additive objects when in-place edits would create import conflicts or empty-value errors. Provide old-to-new decommission mapping. |
| POL-205 | Omit unchanged object arrays from minimal same-container patches, but include schema dependencies needed by changed objects. |
| POL-206 | Include folder definitions referenced by `parentFolderId` in changed tags, triggers, or variables. |
| POL-207 | Include the complete intended `customTemplate` set when included tags or variables use `cvt_*` entity types and GTM needs the template layer for validation. Avoid unchanged custom template churn when no included object needs it. |
| POL-208 | Preserve the complete intended `builtInVariable` enabled set whenever the source or cleanup draft has enabled built-ins. Omitting the layer can disable Page URL, Event, Click, Form, and similar built-ins. |
| POL-209 | Validate generated JSON as a fresh export before delivery. Do not call it import-ready while reference, naming, duplicate, unused, UA-path, or residual-blocker checks are unresolved. |

## Reporting Policies

| ID | Policy |
| --- | --- |
| POL-301 | The cleanup plan is the decision source; the change log is the execution record. Keep IDs, before/after values, reason, impact, QA, owner, and status aligned. |
| POL-302 | Do not add scratch semantic reasoning to normal cleanup plans or change logs. Surface only findings, blockers, operations, QA, owner questions, and decisions. |
| POL-303 | End every completed audit, cleanup-plan phase, cleanup phase, JSON generation phase, QA phase, or handoff with a concrete recommended next step. |
| POL-304 | Keep proof artifacts separate from end-user deliverables. Cleanup plans and post-cleanup change logs must be necessary, actionable, and coherent with backing evidence, not overloaded with internal matrices, raw code/config, validator traces, or scratch reasoning. |
| POL-305 | D2/D3 proof summaries must explain category, source/input, logic/action, output or side effect, and judgment. Generic evidence signals such as `custom code inspected`, `external URL found`, `dataLayer push detected`, `no obvious browser side effect`, `see config`, or `see export` do not count as semantic proof. |
| POL-306 | Cleanup plans must expose only what the user needs to decide, approve, debug, or QA; keep raw proof, code/config dumps, dependency graphs, hashes, and validator mechanics in proof tabs or technical appendices. |
| POL-307 | XLSX cleanup plans should open on a compact decision view by default: one executive decision summary tab and one cleanup action plan tab. Keep proof/technical tabs available but normally hidden with Excel `hidden`, not `veryHidden`. Do not delete proof tabs just to simplify the workbook. |
| POL-308 | Visible workbook columns must earn their place for real human use: approval, debugging, assignment, QA, impact, or next action. Hide blank, constant, duplicate, validator-only, or raw-proof columns from the user-facing view. |
