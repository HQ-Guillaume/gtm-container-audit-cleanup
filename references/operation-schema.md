# Operation Schema And Scenario Intelligence

Use this reference to turn audit findings into route-aware cleanup operations.
It exists to keep agents from mixing audit depth, cleanup aggressiveness, and
execution route.

## Contents

- Cleanup Aggressiveness
- Route Decision Matrix
- Operation Object Schema
- Operation Compiler
- Scenario Playbooks
- Cleanup Intelligence Rules
- Batch And QA Gates
- Regression Checks

## Cleanup Aggressiveness

Audit depth and mutation aggressiveness are separate decisions.

| Level | Use when | Allowed changes | Requires explicit approval |
| --- | --- | --- | --- |
| Conservative | User asks for minimal risk, production is fragile, evidence is thin. | Clear broken references, no-trigger tags, obvious payload mistakes, documentation of risks. | Deletes, broad renames, consolidation, consent behavior changes. |
| Standard | Default execution level after a complete audit. | In-place fixes, safe naming, obvious unused candidates after dependency sweep, single-member trigger-group flattening, low-risk duplicate cleanup. | Consent model changes, vendor payload redesign, major gateway refactor. |
| Deep | User approves full cleanup and evidence is strong. | Cross-layer consolidation, helper variables, reusable triggers, broad naming, obsolete-object deletion after QA, custom-code hardening. | Transformational architecture changes or business-semantic changes. |
| Transformational | Container needs redesign, migration, or server-side/gateway architecture change. | New gateway pattern, ecommerce data contract redesign, server-side migration, market architecture changes. | Always requires a signed-off plan and staged execution. |

Default to a complete deep audit. Default direct execution to `Standard` unless
the user approves `Deep` or `Transformational`. Never reduce audit coverage just
because a specific change is blocked.

## Route Decision Matrix

| User need | Preferred route | Why |
| --- | --- | --- |
| Modify existing objects in place | Direct GTM/MCP/API | Preserves IDs and workspace history. |
| Broad naming standardization | Direct GTM/MCP/API | GTM JSON merge is name-conflict based and can show add/delete churn. |
| Delete obsolete objects | Direct GTM/MCP/API or overwrite/new-container JSON | Same-container merge JSON cannot reliably delete omitted existing objects. |
| Human-readable GTM View Changes | Direct GTM/MCP/API, or name-preserving same-container JSON | Rename-heavy JSON is not readable. |
| Portable manual artifact | Importable JSON | Useful when no live access exists. |
| New-container migration | Full importable JSON | Existing-object conflict behavior is not a constraint. |
| Rollback / backup | Export JSON | Do not treat backup as a cleanup artifact. |

If the route is direct GTM/MCP/API, create a new workspace first. If workspace
creation is blocked by a limit, stop and alert the user before writing.

If the route is JSON for same-container View Changes, preserve existing names
and explain that naming standardization is deferred to direct cleanup or a
separate final-state artifact.

## Operation Object Schema

Represent every proposed or executed cleanup as a structured operation:

| Field | Required meaning |
| --- | --- |
| `change_id` | Stable unique ID, such as `GTM-OP-001`. |
| `aggressiveness` | Conservative, Standard, Deep, or Transformational. |
| `route` | Direct GTM/MCP/API, Same-container JSON, Overwrite JSON, New-container JSON, Report-only. |
| `layer` | Workspace, Tag, Trigger, Variable, Built-in variable, Folder, Template, Server-side object, Website/dataLayer. |
| `action` | Add, Update, Rename, Delete, Replace, Flatten, Consolidate, Defer, Document exception. |
| `object_id` | GTM ID/path when available. |
| `before_name` | Required for existing objects. |
| `after_name` | Required for rename, replace, or new object. |
| `semantic_role` | Vendor/event/business purpose. |
| `reason` | Finding, official-doc contract, dependency issue, or user decision. |
| `official_doc_basis` | Source title/URL or `Not applicable`. |
| `dependencies` | Consumers, trigger groups, setup/teardown, variables, folders, templates, custom-code refs. |
| `risk` | Data, consent, privacy, performance, release, rollback, or owner risk. |
| `qa_method` | Preview/debug, Tag Assistant, network, vendor helper, export diff, API readback, owner validation. |
| `rollback` | Exact rollback object/export/version or direct reversal. |
| `status` | Proposed, Approved, Applied, Verified, Deferred, Rejected. |
| `blocker` | Required when deferred or rejected. |

Do not execute an operation table that lacks dependencies, QA method, rollback,
or route for any mutation.

## Operation Compiler

Compile audit findings into operations in this order:

1. Normalize inventory and dependency facts.
2. Attach official documentation contracts to GA4 and vendor-event findings.
3. Classify findings by business impact and risk.
4. Choose cleanup aggressiveness.
5. Choose execution route.
6. Generate operations with route-specific mutation style.
7. Validate dependencies and blockers.
8. Batch operations for execution.
9. Run post-batch readback and update statuses.

For direct GTM/MCP/API, prefer `Update` or `Rename` on existing IDs. Use
`Replace` only when a new reusable concept is needed or the API/tool behavior
makes in-place mutation unsafe.

For same-container JSON, use `Update` only when GTM can match the existing name.
Use `Replace` with old-to-new mapping when conflict behavior makes in-place
import unreliable.

## Scenario Playbooks

### Ecommerce Accuracy

Use when GA4, Ads, Meta, affiliate, or remarketing tags depend on product/order
data.

- Map current website/dataLayer payload for each ecommerce event.
- Verify official GA4 and vendor event contracts.
- Validate core ecommerce variables before tag fields.
- Fix dataLayer-readiness issues before inventing GTM-side helpers.
- Test empty, one-item, multi-item, missing currency, missing quantity, and
  missing product ID cases.

### Consent And CMP

Use when Didomi, OneTrust, Cookiebot, Axeptio, Consent Mode, or regional rules
affect firing.

- Identify default state, update state, CMP-ready events, and region logic.
- Separate legal/business decisions from technical implementation.
- Align pageview/base tags for the same vendor unless a documented reason
  exists.
- Never collapse consent triggers if timing changes are not proven safe.

### SPA Or PWA

Use when the website changes route without full page reload.

- Identify history-change, route, virtual pageview, and dataLayer events.
- Check duplicate pageviews and stale ecommerce data after navigation.
- Require runtime browser evidence; JSON alone cannot prove route behavior.

### Multi-Market Or Multi-Language

Use when names, hostnames, paths, currencies, or variables contain market codes.

- Verify that market names are enforced by trigger/filter/dataLayer logic.
- Ask about unclear product or campaign tokens before consolidating.
- Prefer lookup/regex tables only when ownership and QA remain clear.

### One-Tag Gateway

Use when many tags differ only by vendor ID, event name, market, or payload
mapping.

- Identify dispatcher, loader, lookup-table, server endpoint, or custom HTML
  gateway candidates.
- Prefer gateway consolidation only when it improves maintainability without
  hiding consent, ownership, or vendor-specific payload rules.
- Treat gateway failure blast radius as a risk.

### Server-Side GTM

Use when server container evidence exists or migration is requested.

- Inventory clients, tags, transformations, consent forwarding, endpoint domain,
  and monitoring.
- Validate browser-to-server and server-to-vendor payload contracts separately.
- Check event deduplication IDs for browser/server dual tracking.

### Emergency Fix

Use when the user asks for a fast production repair.

- Limit the operation table to the critical issue.
- Document skipped cleanup scope explicitly.
- Preserve a rollback export and recommend a full audit afterward.

## Cleanup Intelligence Rules

- A currently unused object is not automatically safe to delete; consolidation
  design can change deletion candidates.
- A similar object is not automatically a duplicate; market, consent, product,
  or ownership scope can justify separation.
- A scalar product ID is suspect when a vendor expects an array or object.
- A helper that reads old dataLayer history is suspect when the event context
  requires the current ecommerce action.
- A name that says a country, product, consent vendor, or event must be enforced
  by configuration or renamed/deferred.
- A custom HTML tag that only defines a function is a probable no-op unless
  runtime evidence proves an external caller.
- A JSON artifact is not complete until it is self-audited as a fresh export.

## Batch And QA Gates

Use small batches for direct cleanup:

1. Workspace and rollback snapshot.
2. Helper variables and lookup/regex tables.
3. Consent and scoping triggers.
4. Vendor/event-family tag updates.
5. Trigger-group flattening and consumer remapping.
6. Obsolete-object deletion after verification.
7. Final naming and folder placement.
8. Fresh export/readback and report update.

Do not mix consent-routing changes, payload changes, and broad naming in one
batch unless the container is tiny and the user approves the combined risk.

## Regression Checks

Before delivering any generated artifact or executed cleanup summary, check:

- No missing trigger, variable, folder, setup-tag, teardown-tag, or custom
  template references.
- Built-in variables are preserved when import JSON is used.
- Custom template layers are complete when `cvt_...` types are present.
- Same-container View Changes JSON has no broad rename churn.
- Direct cleanup operations target the approved workspace only.
- Single-member trigger groups are flattened or route-limited with deletion
  instructions.
- Change log columns match the required template.
- Residual blockers are explicit and owner-actionable.
