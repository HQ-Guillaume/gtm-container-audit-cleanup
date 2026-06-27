# Audit Domain Checks

Use this reference after the general rubric when a full GTM audit needs
domain-by-domain coverage.

## Contents

- Governance
- Web Container Implementation
- Security And Custom Code
- Architecture And Organization
- Setup Hygiene
- Consent And Privacy
- Google Events
- Server-Side GTM
- Vendor Pixels And Marketing Tags
- Cleanup Heuristics
- Scenario-Specific Intelligence

## Governance

Check permissions, agency/vendor access, service accounts, 2-step verification,
workspace/release process, default workspace usage, version descriptions, and
rollback clarity. Flag unknown users, excessive publish/admin permissions,
weak release history, and repeated default-workspace work.

## Web Container Implementation

Check representative page types and environments for GTM script placement,
`noscript`, missing templates, multiple containers, duplicate loads, CSP
blocking, dataLayer initialization order, SPA/PWA caveats, and events firing
before GTM is ready. Use `runtime-qa-templates.md` when browser or network
evidence is required.

## Security And Custom Code

Check Custom HTML, Custom JavaScript, and custom templates for hardcoded
credentials/PII, unsafe script injection, brittle DOM selectors, fixed array
indexes, unguarded numeric parsing, accidental hardcoding, missing invocation,
escaping/serialization issues, consent assumptions, and safer native/template
alternatives.

For every active, referenced, risky, or cleanup-relevant custom-code object,
record purpose, role category, trigger/consumer context, consent assumption,
side effects, variable references, expected output, runtime risks,
recommendation, and semantic status. Runtime QA may be deferred before mutation;
export-level code/config inspection may not.

## Architecture And Organization

Assess brand, market, domain, app/environment separation, ownership boundaries,
agency/vendor access, web versus server-side separation, release cadence, QA
process, folders, and naming. Use `naming-standardization.md` for naming
judgment.

## Setup Hygiene

Check tags without firing triggers, triggers without connected tags, paused/old
objects, duplicates and near-duplicates, redundant objects, broken regex/CSS
selectors, overly broad conditions, deprecated vendors, and Custom HTML where a
native/template option is safer.

Use three cleanup buckets:

- `Currently unused`: no current consumers after a full dependency sweep.
- `Consolidation obsolete`: currently used, but replaced by approved refactor.
- `Deferred validation`: appears redundant/fragile, but evidence or ownership is
  missing.

Do not finalize deletion from the first orphan scan; consolidation can make more
objects obsolete later.

## Consent And Privacy

Read `audit-consent-server.md`. Minimum outcome: every meaningful vendor family
has consent status, evidence, risk, and blocker or no-change decision.

## Google Events

Read `audit-ga4-ecommerce.md`. Treat ambiguous Google analytics/ecommerce
objects as GA4/current Google tag candidates unless evidence proves a UA
exception. Minimum outcome: GA4/current Google versus UA exceptions are explicit,
official dataLayer payload shape is checked, and ecommerce value/item/quantity
logic is validated before cleanup decisions.

## Server-Side GTM

Read `audit-consent-server.md` when server-side GTM, first-party endpoints,
media-named Google event tags, or forwarding signals appear. Without server
container export/API evidence, network traces, or platform logs, classify
uncertain transport tags as `server-container validation needed` rather than
mutating IDs, consent triggers, or paused state.

## Vendor Pixels And Marketing Tags

Read `audit-media-vendors.md`, `vendor-playbooks.md`, and `source-map.md`.
Minimum outcome: event role, consent, sequencing, payload shape, value/currency,
IDs, deduplication, and platform optimization use are checked or deferred with
blockers.

## Cleanup Heuristics

Prioritize privacy/consent consistency, conversion accuracy, GA4 ecommerce
payload correctness, maintainability, performance, and release safety. Prefer
consolidation when repeated tags, triggers, custom JS, consent rules, variables,
or vendor payload construction can be safely represented by reusable helpers.
Avoid over-consolidation that hides ownership, creates a risky mega-tag, or
makes QA harder.

## Scenario-Specific Intelligence

Select scenarios from evidence and mark absent patterns `Not applicable`:

| Scenario | Signals | Extra checks |
| --- | --- | --- |
| Ecommerce accuracy | GA4 ecommerce, Ads conversions, media/affiliate product fields. | Current event payload, item arrays, value/currency, transaction IDs, multi-item handling, vendor field shape. |
| Consent/CMP | CMP objects, native consent settings, Consent Initialization triggers. | Default/update timing, regional rules, pageview/base consistency, legal-owner blockers. |
| SPA/PWA | History triggers, route variables, virtual pageview tags. | Runtime route changes, duplicate pageviews, stale dataLayer state, async ecommerce pushes. |
| Multi-market/language | Country codes, hostnames, currencies, languages, market IDs. | Scope enforcement, unclear token clarification, lookup/regex consolidation. |
| One-tag gateway | Dispatcher HTML, lookup routing, shared loaders, server endpoint. | Blast radius, observability, consent routing, vendor payload preservation. |
| Server-side GTM | Server container, first-party endpoint, transformations, CAPI tags. | Browser-to-server payload, server-to-vendor payload, consent forwarding, deduplication IDs, monitoring. |
| Emergency fix | Fast repair or production breakage. | Limit mutation scope, record skipped cleanup, recommend full follow-up audit. |
