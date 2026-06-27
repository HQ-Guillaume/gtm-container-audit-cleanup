# Semantic Model Protocol

Use this reference after inventory and dependency mapping. It defines the
internal model an agent should build before judging cleanup, consolidation, or
business-logic correctness. The model is a reasoning tool, not a required
stakeholder-facing report section.

## Contents

- Purpose
- Measurement Diagnosis Gate
- Model Layers
- Inference Rules
- Business Defect Taxonomy
- Missing Logic Detection
- Semantic Model Checks
- Reporting Discipline

## Purpose

Model the container as a measurement system:

```text
business objective -> user action -> event/context -> GTM objects
                   -> data source/formula -> destination payload
                   -> platform use -> QA evidence/blocker
```

This prevents superficial cleanup from hiding business defects. A duplicate tag
can be harmless, while a technically valid conversion tag can train bidding on
the wrong action or send a nonsensical value.

## Measurement Diagnosis Gate

Before cleanup decisions, build a short internal diagnosis for the container or
for each meaningful object family:

- business model: ecommerce, lead generation, media/publisher, SaaS, school,
  marketplace, appointment, content, support, or utility;
- decision outcomes: sale, qualified lead, application, appointment, download,
  content monetization, subscription, retention, audience, exclusion, or
  attribution;
- conversion hierarchy: primary conversion, micro-conversion, engagement,
  remarketing, server-forwarding event, or technical helper;
- platform role: reporting, bidding optimization, audience building, enhanced
  matching, CRM/affiliate handoff, server routing, or operational QA;
- expected contract: event name, trigger context, value/currency, item/object
  shape, lead/form type, user or event ID, market/product scope, consent, and
  deduplication.

Do not compile cleanup operations for a meaningful object when this diagnosis is
missing. If the export cannot prove intent, use a precise owner question,
runtime QA requirement, or server/dataLayer blocker.

## Model Layers

Build these layers for meaningful object families:

| Layer | Questions |
| --- | --- |
| Business objective | What business outcome does this object appear to support: sale, lead, appointment, brochure, content engagement, ad revenue, retention, audience, attribution, or utility? |
| User action | What user behavior or backend outcome should trigger the signal? |
| Event/context | Which page, event, form, product, market, language, consent state, or server route is required? |
| GTM implementation | Which tags, triggers, variables, templates, custom code, folders, setup/teardown, and built-ins implement it? |
| Data source | Is the source current dataLayer, previous dataLayer history, DOM, URL, cookie, constant, lookup/regex table, server container, or platform-side mapping? |
| Payload contract | What event name, value, currency, item/object shape, ID, lead type, consent, and dedup fields should be sent? |
| Platform use | Is the signal for bidding, reporting, audience, exclusion, attribution, enhanced matching, consent modeling, or server forwarding? |
| Evidence | Is correctness proven by export, official docs, runtime QA, vendor platform, owner decision, or still blocked? |

## Inference Rules

Infer intent from names, folders, tag types, vendor fields, triggers, variables,
official documentation, website context, and repeated patterns. Then verify the
configuration enforces the inferred intent.

Do not silently assume:

- a tag named `Lead` is a qualified lead;
- a thank-you page belongs to one form type;
- a country/product/campaign token is enforced by a trigger;
- a shared variable has the same meaning for all vendors;
- a static value is acceptable for every conversion;
- a server-side route preserves the same consent and payload semantics.

If intent is plausible but unproven, create a blocker or owner question only
when it affects a cleanup decision, mutation safety, QA, or measurement quality.

## Business Defect Taxonomy

Actively search for defects that are invisible in a superficial object cleanup:

- a final conversion tag fires on a low-intent click, form start, shared
  thank-you page, or generic pageview;
- media bidding tags receive micro-conversions or audience events as if they
  were primary business outcomes;
- purchase, lead, value, quantity, item, product, or category variables use
  wrong paths, stale dataLayer history, fixed indexes, scalar fields, or
  incompatible output types;
- vendors tracking the same business action receive different values, currency,
  IDs, event names, item sets, or deduplication fields without a clear reason;
- consent or server-side routing is judged only from browser-side triggers even
  though consent or vendor routing may be forwarded to a server container;
- names imply a market, product range, campaign, form type, or qualified lead
  but trigger filters, variables, or payloads do not enforce that meaning;
- reusable variables, triggers, or helpers are shared across incompatible
  business contexts;
- a cleanup proposal would remove a technically messy object that actually
  preserves a distinct business, consent, market, or vendor-platform role.

For each defect, prefer a finding, owner question, website/dataLayer blocker, or
runtime QA step over a guessed GTM-side fix.

## Missing Logic Detection

After mapping the implemented objects, infer likely missing pieces from the
container's own design:

- A lead-generation site has form-submit tags but no lead type, form name,
  program, campus, or value differentiation.
- Ecommerce conversion tags exist but no reliable item array, transaction ID,
  currency, discount, tax, shipping, or quantity source exists.
- Media conversion tags exist but no event ID or deduplication key exists where
  browser/server duplicates are plausible.
- A product/category naming pattern exists but triggers or variables do not
  enforce the product/category scope.
- A server-side endpoint exists but the web container does not forward the
  fields needed for server transformations, consent enforcement, or vendor
  routing.
- Several vendors track the same apparent business event but receive different
  trigger timing, IDs, values, currency, or item payloads without rationale.

Treat inferred missing logic as `More info needed` or a website/dataLayer/server
blocker unless the export/runtime evidence proves the defect.

## Semantic Model Checks

Before producing cleanup operations, verify:

- the measurement diagnosis gate is complete for every affected meaningful
  object or family;
- every high-risk tag has one inferred business objective or a documented
  ambiguous objective;
- every conversion/media/ecommerce tag has a source-of-truth path for the values
  it sends or a blocker;
- every reusable trigger/variable keeps compatible semantics across consumers;
- every proposed consolidation preserves scope, ownership, consent, and vendor
  payload shape;
- every proposed deletion has been re-evaluated after consolidation design;
- missing pieces of an inferred business flow are recorded as blockers or
  optional future work, not as fake GTM-side fixes.

## Reporting Discipline

Do not add a large semantic-model dump to normal cleanup plans or change logs.
Use the model to improve:

- finding evidence;
- operation reason and blocker;
- QA method;
- owner questions;
- deferred website/dataLayer/server work;
- confidence level.

Create a dedicated semantic traceability tab only when the user asks for deep
review evidence or when a high-risk decision would otherwise be opaque.
