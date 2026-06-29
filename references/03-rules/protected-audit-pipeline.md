# Protected Audit Pipeline

Use this file for every full audit, cleanup plan, approved cleanup, generated
JSON artifact, and post-cleanup change log. It protects basic cleanup findings
from being lost when semantic review becomes complex.

## Contents

- Principle
- Required Stages
- Source Model Navigation Map
- Deterministic Baseline
- Custom-Code Fact Layer
- Independent Semantic Source Scan
- Semantic Enrichment
- Finding Reconciliation
- Operation Packet Contract
- User-Facing Compilation
- Final Gates

## Principle

The skill has three independent cleanup lenses:

1. **Deterministic cleanup baseline**: mechanical facts that should be found the
   same way every time.
2. **Semantic business cleanup**: analyst judgment that explains business
   purpose, payload meaning, risk, owner blockers, and cleanup impact.
3. **Technical custom-code optimization**: code-health, code-security, and
   simplification facts for Custom HTML, Custom JavaScript, and custom
   templates.

All cleanup lenses share a source model map, but source evidence remains the
source of truth:

```text
source export/API evidence
-> source model navigation map only
-> deterministic_findings.json
-> semantic_findings.json
-> technical_code_findings.json
-> reconciled_operations.json
-> compact user-facing cleanup plan with hidden proof tabs
```

The source model tells lenses where to look. Raw export/API/config/code/runtime
evidence tells them what is true. Semantic review may confirm, enrich,
downgrade, or document exceptions to deterministic findings, but it must not
silently remove them or depend only on summarized artifacts. Technical custom
code review may classify code risk or simplification candidates, but business
meaning is decided in the semantic lens and the final action is decided only in
reconciliation.

The source model cannot create, suppress, downgrade, or summarize findings. Each
lens must read or verify the raw source evidence directly, even when the package
builder creates all artifacts in one command.

## Required Artifacts

A complete cleanup plan must preserve these artifacts or equivalent workbook
tabs:

| Artifact | Required role |
| --- | --- |
| `source_model.json` | Navigation map only: IDs, names, types, fields, edges, consumers, unresolved references, and recognized GTM system references. |
| `deterministic_findings.json` | Mechanical hygiene findings and zero-finding proof rows from raw source. |
| `semantic_findings.json` | Independent semantic source scan and object-diagnosis seeds from raw source. |
| `technical_code_findings.json` | Custom-code technical facts, health, security, and optimization candidates from raw source. |
| `reconciled_operations.json` | Object-matched operation packets that combine scan outputs and resolve conflicts. |

Preferred export-based package command:

```powershell
python scripts/gtm_audit_package_build.py container.json --out-dir audit-package --pretty
```

The visible cleanup plan must be generated from `reconciled_operations.json` or
an equivalent operation-packet table. Do not generate the visible cleanup plan
directly from baseline rows, semantic rows, custom-code rows, or an inventory
summary.

## Required Stages

Run the stages in this order for full audits and cleanup plans:

1. Inventory.
2. Source model navigation map and coverage gate.
3. Deterministic baseline from the source JSON/API evidence, using the source
   model for traversal only.
4. Custom-code fact extraction and technical code review from the source JSON/API
   evidence.
5. Independent semantic source scan from the source JSON/API evidence, using the
   source model for traversal only.
6. Semantic D1-D3 review.
7. Finding reconciliation and cross-layer double-check.
8. Operation-packet compiler.
9. Cleanup-plan compiler from operation packets.
10. Final gates.

Do not jump directly from inventory into semantic interpretation. Operations are
not cleanup-ready until the relevant deterministic, semantic, and technical
findings are reconciled or explicitly marked not applicable for the affected
object.

## Source Model Navigation Map

Before the three cleanup lenses, run or reproduce:

```powershell
python scripts/gtm_source_model.py container.json --pretty
```

The source model is a lossless navigation layer, not a compressed evidence
summary. It must preserve object IDs/names/types, tag fields, trigger edges,
trigger groups, setup/teardown, folder/template references, variable sources,
field-to-variable references, custom-code references, consumers, and unresolved
edges.

If source model coverage is incomplete, continue only by marking exact blockers.
Do not let deterministic, semantic, or technical checks rely on a shallow object
list. Each finding must still cite or verify the raw source evidence behind the
mapped edge.

## Deterministic Baseline

Before semantic review, run or reproduce the equivalent of:

```powershell
python scripts/gtm_baseline_audit.py container.json --pretty
```

The baseline artifact must include module rows and zero-finding proof rows. A
module cannot be silently skipped.

Minimum modules:

- inventory completeness;
- missing references;
- unused triggers, variables, folders, and custom templates;
- tags without firing triggers;
- exact duplicate names;
- exact duplicate tag, trigger, and variable configurations;
- normalized duplicate tag signatures;
- duplicate trigger logic;
- duplicate variable logic and duplicate dataLayer/source paths;
- duplicate custom-code bodies;
- outdated Universal Analytics-style setup objects across tags, triggers, and
  variables, including legacy ecommerce paths and fixed product-index paths;
- single-member trigger groups;
- name hygiene;
- naming and route architecture standardization, including the selected naming
  policy when user convention is absent;
- recognized GTM internal/system references so `_event` and system trigger IDs
  are not misreported as missing objects.

Each nonzero finding must include:

- `module_name`
- `module_status`
- `objects_scanned`
- `finding_id`
- `finding_type`
- `object_type`
- `object_ids`
- `object_names`
- `signature_key`
- `deterministic_evidence`
- `default_action`
- `required_resolution`

The baseline is not the cleanup plan. It is the proof layer that semantic review
must consume.

## Custom-Code Fact Layer

Before semantic interpretation, extract deterministic facts for Custom HTML
tags, Custom JavaScript variables, and custom templates:

```powershell
python scripts/gtm_custom_code_extract.py container.json --pretty
```

Capture code hash, referenced GTM variables, dataLayer reads/writes, cookies,
localStorage/sessionStorage, DOM access, event listeners, external scripts,
network calls, return type, side effects, consumers, whether export evidence is
enough, whether runtime QA is required, and purely technical code health,
security, and optimization signals.

Technical code review is not business-semantic validation. It answers:

- is the code unnecessarily large or hard to maintain;
- does it use risky browser APIs such as text-as-code execution, direct HTML
  insertion, unguarded cross-window messages, dynamic script sources, unencrypted
  URLs, or browser storage;
- can the code likely be shortened, moved to a template, consolidated, or
  replaced with native GTM features.

Do not write `custom code inspected` unless this fact layer or an equivalent
manual extraction exists. Technical rows must keep technical code health
separate from business semantics and must include an action candidate:
`fix_required`, `consolidate_candidate`, `delete_candidate`, `keep`,
`runtime_blocked`, or `owner_decision_needed`.

For every non-keep technical row, include execution-grade fields:

- current behavior in plain language;
- expected clean state;
- exact proposed technical action, not a vague category such as `simplify code`;
- preconditions or owner evidence needed before mutation;
- QA steps that compare before/after behavior;
- rollback note;
- handoff packet with object ID/name, identity/hash, referenced variables,
  external scripts, and side effects.

Examples of acceptable technical actions:

- replace fixed product-position ecommerce access with item-array handling;
- remove duplicate script loaders so one event creates one expected vendor
  request;
- move a small helper into a built-in variable, lookup table, regex table, or
  one canonical cJS variable after sample outputs match;
- add a message origin check or remove the listener;
- replace unencrypted endpoints with approved HTTPS endpoints.

## Independent Semantic Source Scan

Before D1-D3 semantic judgment, run or reproduce:

```powershell
python scripts/gtm_semantic_source_scan.py container.json --pretty
```

This scan must read the same source export/API evidence directly. It must not
consume only deterministic baseline rows, duplicate groups, or a previous
cleanup plan. Its purpose is to seed semantic coverage for Google/GA4 events,
legacy Universal Analytics migration signals, ecommerce contracts, consent,
media vendors, lead/form measurement, custom code, server/gateway routing, and
generic object coverage.

The semantic source scan is still not the final semantic judgment. It is a proof
input that prevents basic object families from disappearing when deterministic
findings are summarized too aggressively.

Semantic source rows for actionable or blocked objects must seed object
diagnosis, not only topic labels. Include current behavior, expected behavior or
contract, cleanup implication, blocker, confidence, and the same reconciliation
identity fields used by other lenses.

## Semantic Enrichment

Run D1-D3 after the baseline, custom-code extraction, and independent semantic
source scan. Semantic review must:

- explain literal behavior;
- infer business purpose;
- trace referenced variables, triggers, custom code, and template fields;
- compare sibling objects and similar families;
- identify bad data types, field mappings, consent mappings, trigger scopes,
  ecommerce paths, formula logic, or duplicate behavior;
- distinguish confirmed issues from runtime-only blockers;
- decide whether deterministic findings are true cleanup items or documented
  exceptions.

Script output, hashes, URL lists, and duplicate groups are evidence inputs, not
semantic validation.

Semantic rows for actionable or blocked objects must include these operation
seeds:

- current behavior in plain language;
- expected clean behavior or expected data contract;
- cleanup implication: delete, fix, consolidate, harden, rebuild, defer, or
  document exception;
- exact blocker when the action cannot be decided from export/API evidence;
- linked deterministic and technical source finding IDs where applicable.

The semantic object matrix must be built from the source JSON/API/config/code
and the semantic source scan, then reconciled with deterministic findings. If a
semantic conclusion only repeats a baseline summary and does not inspect the
source object itself, the semantic layer is incomplete.

## Finding Reconciliation

Every deterministic, semantic, and technical finding must end as exactly one of:

- `cleanup_operation`
- `documented_exception`
- `runtime_blocker`
- `owner_decision_needed`
- `not_applicable`

Object matching must use the most stable available identity:

```text
layer + object_id + object_name + object_type + code/config hash
```

When IDs are absent, use name plus type plus a normalized config/code hash and
mark confidence lower. Do not duplicate one object into multiple cleanup rows
just because each lens used different labels.

Before compiling the visible plan, double-check for mismatches:

- deterministic findings with no semantic row or resolution;
- semantic issues with no visible operation, blocker, or documented no-change
  decision;
- technical custom-code findings with no exact delete, consolidate, harden,
  rebuild, document-exception, runtime-QA, owner-decision, or handoff outcome;
- legacy UA-style setup objects that disappeared after semantic summarization;
- custom-code technical risks that have no exact fix/consolidation action,
  handoff evidence, or runtime QA blocker;
- fixed product-index ecommerce logic that was accepted without item-array or
  multi-item review.

Use these conflict rules:

- `deterministic delete candidate` + `semantic maybe useful` -> owner decision
  or runtime blocker; do not delete directly.
- `technical risk` + `semantic unused/no consumer` -> prefer delete candidate
  if no external business consumer exists; otherwise harden or rebuild.
- `semantic issue` + `deterministic clean` -> create semantic fix/defer
  operation; do not downgrade to no issue.
- `technical simplification` + `semantic active business dependency` ->
  consolidate/rebuild only after QA proves equivalent output and timing.
- `three lenses agree on duplicate/unused/obsolete` -> cleanup operation may be
  high confidence, still with rollback and QA.

Validate deterministic reconciliation with:

```powershell
python scripts/gtm_findings_reconcile.py deterministic_baseline.json cleanup_resolution.xlsx
```

The resolution file may be a CSV, JSON, or XLSX workbook. It must expose source
finding IDs in a column such as `finding_id`, `source_finding_id`, or
`source_finding_ids`, and a resolution/status column using one of the accepted
resolution values.

Validate the full three-lens operation packet layer with:

```powershell
python scripts/gtm_findings_reconcile.py deterministic_findings.json reconciled_operations.json --operation-packets
```

When semantic or technical finding files are available, pass them too:

```powershell
python scripts/gtm_findings_reconcile.py deterministic_findings.json reconciled_operations.json --operation-packets --semantic semantic_findings.json --technical technical_code_findings.json
```

## Operation Packet Contract

Every visible cleanup-plan row must be backed by one operation packet, except
for pure summary rows whose immediate detail rows each have packets. Required
fields:

- `operation_id`;
- `affected_objects`;
- `object_identity`;
- `source_lenses`;
- `current_behavior`;
- `problem`;
- `why_it_matters`;
- `expected_clean_state`;
- `exact_proposed_action`;
- `preconditions`;
- `qa_steps`;
- `rollback`;
- `confidence`;
- `blocker`;
- `priority`;
- `resolution_status`;
- `source_finding_ids`.

When `source_lenses` includes `technical`, the packet must also carry
`technical_handoff_packet` or an equivalent handoff field with object identity,
code/config hash, referenced variables, external scripts, side effects, and the
evidence needed for another analyst or agent to continue safely.

If a field cannot be completed, the packet is a blocker/investigation item, not
a cleanup-ready operation. Avoid generic action words. `Simplify`,
`consolidate`, `harden`, or `fix` must be followed by the exact intended state
or by the exact decision/evidence blocker.

## User-Facing Compilation

The cleanup plan should remain compact and human-readable. Compactness must not
hide concrete findings.

Write visible rows for non-specialists: what is wrong, why it matters, what is
expected after cleanup, what should be done next, and how to QA it. Define jargon
in plain words, for example "old Universal Analytics ecommerce format" instead
of only "UA Enhanced Ecommerce".

Allowed:

- summary rows with immediate detail rows for distinct object-level findings;
- one-line batches for generic hygiene actions when evidence, action, QA, and
  rollback are identical;
- hidden proof tabs for inventory, baseline, D3, custom code, and validation.

Not allowed:

- vague rows like `review tags` or `review custom code`;
- cleanup rows without source finding IDs;
- cleanup rows without a hidden operation packet or equivalent reconciled
  operation;
- rows whose main action is `simplify`, `consolidate`, `harden`, or `fix`
  without saying what exact object state should change or what decision blocks
  that change;
- family summaries that hide distinct duplicate, risky, or blocked objects;
- real change logs before cleanup execution.

## Final Gates

The audit or cleanup plan is incomplete when:

- any mandatory stage is missing;
- inventory counts do not reconcile;
- a deterministic baseline module is missing;
- custom-code objects lack extraction/proof rows;
- semantic review skips objects or families;
- deterministic findings are unreconciled;
- semantic or technical findings in scope are missing from the reconciliation
  layer;
- visible cleanup rows are not backed by operation packets;
- cleanup plan rows are not linked to source findings;
- final output claims completion despite unresolved blockers.

Run the workbook/package gates where applicable:

```powershell
python scripts/gtm_audit_gate_check.py --strict-evidence workbook.xlsx
python scripts/gtm_audit_package_check.py container.json workbook.xlsx
```
