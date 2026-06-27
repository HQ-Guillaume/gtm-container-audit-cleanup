# Naming Standardization

Use this reference whenever an audit, cleanup plan, mutation, or generated JSON
includes naming review or rename operations.

## Contents

- Decision Hierarchy
- Default Patterns
- Semantic Family Rules
- Case Rules
- Uniqueness And Blockers
- Rename QA

## Decision Hierarchy

Apply naming after semantic fixes, consolidation design, and deletion decisions
are known, so remaining objects receive stable final names.

1. Follow user-provided naming models or examples.
2. If no user model exists, infer the dominant local convention: separator
   style, object order, vendor acronyms, event casing, trigger-role prefixes,
   variable type prefixes, folder grouping, and suffixes.
3. Preserve meaningful local acronyms when the configuration proves them, for
   example `PA` for Piano Analytics.
4. Standardize semantically equivalent objects within the same object layer and
   family. Do not keep mixed labels only because they already exist.
5. Use the default patterns only when no reliable local convention exists.

## Default Patterns

| Layer | Pattern | Examples |
| --- | --- | --- |
| Tags | `Vendor - Event/role - Scope/detail` | `GA4 - purchase`, `PA - page.display - Article`, `Meta - Purchase - FR` |
| Triggers | `Utility/type - Event or condition - Scope/detail` | `Event - purchase`, `PV - All Pages`, `Block - PA - Analytics consent denied`, `TG - PA - Page display ready` |
| Variables | `Type acronym - Variable name/source` | `DLV - ecommerce.items`, `CJS - Purchase total quantity`, `LT - Hostname to currency` |
| Folders | `Vendor` or `Domain / Function` | `GA4`, `PA`, `Consent`, `Ecommerce helpers` |

Variable type acronyms:

- `DLV`: Data Layer Variable.
- `CJS`: Custom JavaScript variable.
- `LT`: Lookup Table.
- `RT`: Regex Table.
- `URL`: URL variable.
- `1P`: first-party cookie.
- `JS`: JavaScript variable.
- `Const`: constant.
- `Util`: utility/helper when the source is mixed or abstract.

## Semantic Family Rules

- Put the destination/platform first for tags.
- Put the trigger utility or condition first for triggers.
- Put the implementation/source type first for variables.
- Avoid redundant layer prefixes such as `TR -`; GTM already shows the object is
  a trigger.
- Use `TG` only for trigger groups or an established trigger-group abbreviation.
- Flatten single-member trigger groups before final naming when the cleanup route
  supports deletion.
- Treat vendor/CMP names as vocabulary, not role names. If `Didomi - ...`,
  `Consent - ...`, and `Block - ...` triggers all block a vendor because consent
  is denied, standardize them under the blocking-trigger pattern. Keep `Didomi`
  only when the trigger is truly a CMP event/state trigger.
- Put market, language, product range, campaign, pixel/account ID suffix,
  consent category, sequence role, or lifecycle status after the event/role.

## Case Rules

- Preserve official event casing and technical keys, such as `page.display`,
  `click.action`, `add_to_cart`, `ViewContent`, or `Purchase`.
- Keep acronyms uppercase, such as `PA`, `GA4`, `CMP`, `DLV`, `CJS`, `URL`, and
  `JS`.
- Use one readable case for human labels, such as `Analytics consent denied` or
  `Newsletter CTA`.
- Do not mix `Page Display`, `page Display`, `PAGE DISPLAY`, and
  `page_display` for the same concept unless the destination's official event
  name requires it.

## Uniqueness And Blockers

Every proposed final name must be unique inside its GTM object layer. If a base
pattern collides, add the smallest meaningful suffix that explains why the
object remains separate: trigger event, page type, market, product range,
campaign, destination ID suffix, consent category, sequence role, or lifecycle
status such as `Legacy`, `Paused`, or `Decommission candidate`.

Use an object ID suffix only as a temporary audit placeholder when the real
business distinction is unknown. Mark the row as blocked for owner
clarification; do not treat the ID-suffixed name as a preferred final name.

Do not invent meanings for internal tokens. Ask whether unclear labels are
product ranges, campaigns, markets, agency codes, audiences, legacy labels, or
something else.

## Rename QA

Before any rename:

- define the final convention for tags, triggers, variables, folders, and
  templates when relevant;
- decide event names from official vendor documentation when applicable;
- map all consumers and dependencies;
- dependency-sweep every renamed variable across tags, triggers, variables,
  lookup tables, templates, Custom HTML, and Custom JavaScript;
- dependency-sweep every renamed trigger/tag for setup/teardown `tagName`
  references, sequencing, trigger groups, and owner references where evidence is
  available;
- record before name, after name, object ID, reason, expected behavior impact,
  QA status, and blocker if deferred.
