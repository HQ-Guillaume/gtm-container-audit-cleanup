# Limited Audit Protocol

Use this reference when the user explicitly asks for a quick audit, sample,
single vendor, single risk area, narrow layer, or minimal cleanup plan.

## Required Boundary

Before starting, state the boundary in operational terms:

- included evidence sources;
- included layers and object families;
- excluded layers and object families;
- whether runtime/browser QA is included;
- whether cleanup planning is included;
- whether naming standardization is included;
- whether the result may be used for cleanup execution.

If the user gives no explicit boundary, default to the complete audit workflow.

## Minimum Safety Floor

Even in a limited audit, never skip these for the objects in scope:

- evidence freshness and source identification;
- inventory and IDs/names for scoped objects;
- dependency map for scoped objects and their consumers;
- measurement diagnosis for scoped meaningful objects;
- consent/privacy impact when scoped objects can fire tags or send data;
- official documentation basis for scoped vendor/event payload judgments;
- semantic validation for scoped objects;
- blocker rows for any required evidence not available;
- no deletion recommendation without dependency sweep;
- no production mutation without explicit approval and mutation playbook.

## Ledger Handling

Use these statuses:

- `Done`: phase completed for included scope.
- `Deferred`: included scope requires missing evidence.
- `Not applicable`: genuinely not relevant to the selected scope.
- `User-excluded`: explicitly outside the user-approved boundary.

Do not mark excluded full-audit workstreams as `Done`. Mark them
`User-excluded` and include the scope boundary in the report.

## Report Label

Limited outputs must include:

```text
Audit mode: Limited audit
Scope boundary:
Excluded workstreams:
Completion gate result: Complete for limited scope | Incomplete / blocked
Not a full-container audit: Yes
```

Use `Complete for limited scope` only when all included workstreams pass their
completion gates. Do not use `Complete full-container review` unless the full
audit gates pass.

## Cleanup Planning From Limited Audits

A cleanup plan from a limited audit can recommend actions only for scoped
objects. It must say:

- dependencies checked;
- dependencies not checked because they are out of scope;
- residual risk from excluded layers;
- whether a full audit is required before execution.

For destructive changes, broad renaming, consent changes, ecommerce payload
changes, or cross-layer consolidation, require a full dependency sweep and full
measurement diagnosis plus semantic validation of affected families before
execution.
