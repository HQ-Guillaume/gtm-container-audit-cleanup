# Audit Rubric

Use this reference for the complete human and technical audit. It is designed to
work from exported GTM JSON, GTM API reads, GTM UI screenshots, Tag Assistant,
page source, crawl output, or stakeholder-provided evidence.

## Contents

- Severity Model
- Evidence Sources
- Inventory Checklist
- Audit Completeness Contract
- Official Documentation Contract
- Deep Object Semantics
- Name-Based Scope Inference
- Mandatory Naming Standardization
- One Tag Gateway Detection
- Governance
- Web Container Implementation
- Security And Custom Code
- Architecture And Organization
- Setup Hygiene
- Consent And Privacy
- Google Event Classification Baseline
- Official GA4 DataLayer And Event Payload Contract
- GA4 And Google Tags
- Mandatory Standard Ecommerce Variable Checks
- Server-Side GTM
- Vendor Pixels And Marketing Tags
- Cleanup Heuristics
- Scenario-Specific Intelligence
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

For every audit, cover:

- all tags, triggers, variables, folders, templates, consent settings, and
  built-in variables;
- exact duplicates and near duplicates across tags, triggers, variables, custom
  code, templates, folders, and naming patterns;
- currently unused objects and objects that become obsolete after consolidation;
- object semantics, consumer dependencies, output shape, and trigger context for
  every high-risk or shared object;
- standard ecommerce variables and all consuming tags;
- custom HTML/JavaScript reference safety;
- gateway and consolidation opportunities where repeated patterns exist.

Sampling is allowed only to explain repeated low-risk hygiene patterns in the
report. It is not a reason to skip dependency mapping or cleanup eligibility
checks for the full container.

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

If the user has a house convention, follow it. Otherwise use this default:

| Layer | Required pattern | Examples |
| --- | --- | --- |
| Tags | `Vendor - Event/role - Scope/detail` | `GA4 - purchase`, `GA4 - Config`, `Meta - AddToCart - IGGI`, `Google Ads - Purchase - FR`, `Pinterest - Base` |
| Triggers | `Utility/type - Event or condition - Scope/detail` | `CE - purchase`, `PV - All Pages`, `Consent - Meta Granted`, `Block - No Marketing Consent`, `Group - purchase + Google Consent` |
| Variables | `Type acronym - Variable name/source` | `DLV - ecommerce.purchase.products`, `CJS - Purchase total quantity`, `LT - Hostname to currency`, `RT - Product range from path`, `URL - Hostname` |
| Folders | `Vendor` or `Domain / Function` | `GA4`, `Meta`, `Google Ads`, `Ecommerce helpers`, `Consent` |

Use these variable type acronyms unless a house style exists:

- `DLV`: Data Layer Variable.
- `CJS`: Custom JavaScript variable.
- `LT`: Lookup Table.
- `RT`: Regex Table.
- `URL`: URL variable.
- `1P`: first-party cookie.
- `JS`: JavaScript variable.
- `Const`: constant.
- `Util`: utility/helper when the source is mixed or abstract.

Rules:

- Put the vendor/platform first for tags, because tags are destination-owned.
- Put the trigger utility/type first for triggers, because triggers are reused by
  firing mechanics: `CE`, `PV`, `Click`, `Form`, `Timer`, `Consent`, `Block`,
  `Group`, or another clear utility.
- Put the variable implementation/source type first for variables, because
  users need to know whether they are reading dataLayer, transforming data,
  looking up a value, or parsing the URL.
- Use the official event name for standard events where applicable, such as
  `purchase`, `add_to_cart`, `ViewContent`, `AddToCart`, or `Purchase`.
- Put market, country, language, product range, campaign, pixel ID suffix, or
  consent detail after the event/role, not before it.
- Every proposed final name must be unique inside its GTM layer. Before
  delivering an audit plan, cleanup operation table, rename map, or generated
  JSON, group proposed names by layer and resolve collisions. Do not propose the
  same final tag name for multiple tags just because they share a vendor and
  event role.
- When a base naming pattern collides, add the smallest meaningful suffix that
  explains why the object remains separate: trigger event, page type, form type,
  market, language, product range, campaign, destination ID suffix, pixel/account
  role, consent category, sequence role such as `Base`, `Config`, `PageView`,
  `Setup`, `Lead Event`, `Standard Event`, or lifecycle status such as
  `Legacy`, `Paused`, or `Decommission candidate`.
- Use an object ID suffix only as a temporary audit placeholder when the real
  business distinction is unknown. Mark that row as blocked for owner
  clarification instead of treating the ID-suffixed name as a preferred final
  production name.
- Keep ambiguous business tokens such as `IGGI`, `Aura`, `Smart`, or agency
  acronyms only when the user confirms their meaning or the configuration proves
  the scope.
- Do not rename a variable unless all `{{Variable Name}}` references in tags,
  triggers, variables, templates, custom HTML, and custom JavaScript have been
  mapped and validated.
- Record every rename as `before name`, `after name`, object ID, reason,
  expected behavior impact, and QA status.
- If standardization is deferred, list the exact object names, blocker, and
  proposed final pattern.

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

## Governance

Check:

- account and container user counts;
- whether users, agencies, vendors, and service accounts have appropriate
  permissions;
- whether risky roles are limited to owners who need them;
- 2-step verification and organization security controls;
- workspace/release process and whether default workspace is used for normal
  work;
- version names/descriptions and rollback clarity.

Flag:

- unknown users or broad agency access;
- excessive publish/admin permissions;
- no descriptive version history;
- repeated work in default workspace without process controls.

## Web Container Implementation

Check representative page types and environments:

- GTM script placement in the page `<head>`;
- `noscript` placement immediately after opening `<body>` where applicable;
- missing GTM on important page templates;
- multiple GTM containers and whether each has an owner/purpose;
- duplicate container loads, with SPA/PWA caveats;
- CSP or browser/security controls blocking `gtm.js`, preview mode, vendor
  scripts, or server-side endpoints;
- dataLayer initialization order and whether important events fire before GTM is
  ready.

Flag implementation checks as `More info needed` when the export alone cannot
prove website behavior.

## Security And Custom Code

Check:

- custom HTML tags, custom JavaScript variables, and custom templates;
- non-script/image pixels implemented through custom HTML instead of safer
  native/image/template options;
- outdated templates or unreviewed community templates;
- hardcoded credentials, tokens, PII, user identifiers, or endpoints;
- code that injects scripts without consent or origin checks;
- code that assumes array positions such as `items[0]` when multi-item orders
  are possible;
- code that only defines a function, listener, or helper without invoking it,
  registering it, or proving another tag/page calls it;
- brittle DOM selectors, regexes, and URL matching.

Prefer template/native tag types over custom HTML when feature parity exists and
the migration risk is acceptable.

For each custom HTML tag under review:

- identify every `{{variable}}` reference and the expected value format;
- distinguish intentional hardcoded constants from accidental hardcoding;
- confirm script/image/noscript behavior and whether it is appropriate inside
  GTM;
- confirm that a defined conversion function is actually called or registered;
  otherwise classify the tag as probable no-op/deferred-delete until runtime or
  owner evidence proves external use;
- verify escaping, quoting, JSON serialization, URL encoding, array joining, and
  null handling;
- verify that any proposed replacement preserves the original dynamic reference
  unless a semantic change is explicitly approved.

## Architecture And Organization

Assess whether the account/container structure fits:

- brands, markets, domains, apps, and environments;
- ownership boundaries and agency/vendor access;
- web vs server-side tagging separation;
- release cadence and QA process;
- naming conventions and folders.

Use the mandatory naming convention above unless a house style exists. Flag
mixed leading axes, unclear abbreviations, duplicated scopes, and names that
encode a scope not enforced by the trigger.

## Setup Hygiene

Check:

- tags without firing triggers;
- triggers with no connected tags;
- paused tags older than 5 months;
- objects edited more than 12 months ago that still power important flows;
- duplicate or near-duplicate tags, triggers, variables, templates, or folders;
- redundant objects with no known consumer;
- broken regex/CSS selectors and overly broad conditions;
- tags attached to non-pageview/non-custom-event triggers without conditions;
- stale Universal Analytics, Google Optimize, or other sunset/deprecated vendor
  tags;
- tags implemented with custom HTML where native GTM tags or maintained
  templates are safer.

Do not recommend deletion solely because an object is old or paused. Classify as
`Needs improvement` or `More info needed` until usage and ownership are clear.

Use three cleanup buckets:

- **Currently unused**: no current consumers after a full dependency sweep.
- **Consolidation obsolete**: currently used, but would be replaced by an
  approved consolidation/refactor.
- **Deferred validation**: appears redundant or fragile, but business ownership,
  runtime evidence, or vendor platform validation is missing.

Report currently unused candidates early, but do not finalize deletion until the
consolidation design has been reviewed. A broad refactor can make many more
objects obsolete than the first orphan scan reveals.

## Consent And Privacy

Before judging consent, identify the consent model:

- CMP vendor and events;
- consent mode basic or advanced for Google tags;
- default consent state timing;
- consent update timing;
- native GTM consent settings;
- firing/blocking triggers or trigger groups;
- regional conditions and legal basis assumptions.

Check:

- Consent Overview enabled when applicable;
- Consent Initialization tags fire before other tags;
- Google consent mode default and update calls exist where Google tags rely on
  consent mode;
- marketing/analytics tags do not fire before required consent in regulated
  regions;
- pageview/base/config tags for the same vendor use coherent consent routing;
- server-side forwarding honors the same consent and privacy rules;
- PII is not sent to GA4, Ads, Meta, or other vendors.

Flag mixed pageview consent patterns inside the same vendor family unless the
timing rationale is documented.

Common patterns:

| Pattern | Use when | Watch out for |
| --- | --- | --- |
| Firing trigger plus blocking trigger | Consent state is reliable before the event fires. | Early pageviews may slip through if CMP is late. |
| Trigger group: pageview/event plus consent-ready/granted | Event can happen before CMP resolves. | More objects to maintain. |
| Native consent settings | Google tags with correctly initialized consent mode. | Does not replace a consent banner or legal decision. |
| Direct CMP-ready firing | The tag intentionally fires once at consent resolution with stable page context. | Can miss original event context or duplicate pageviews. |

## Google Event Classification Baseline

Universal Analytics is sunset, so do not assume a Google event is UA because it
uses old event names or old ecommerce paths. Use this default:

- Treat ambiguous Google Analytics events, Google ecommerce variables, and
  Google event tags as GA4/current Google tag tracking.
- Classify as UA only when the export shows a UA tag type, a `UA-` property ID,
  an explicit legacy requirement from the user, or a verified mapper that
  intentionally converts old UA Enhanced Ecommerce pushes to GA4 payloads.
- Treat legacy event names such as `productDetailImpression`,
  `purchaseImpression`, `addToCart`, `removeFromCart`, `checkout`, or
  `checkoutOption` as migration candidates, not proof that the target should
  remain UA.
- Treat active paths such as `ecommerce.purchase.actionField.*`,
  `ecommerce.purchase.products.*`, `ecommerce.add.products.*`,
  `ecommerce.detail.products.*`, `ecommerce.checkout.products.*`, and
  `ecommerce.impressions` as high-risk legacy sources when they feed GA4 or
  media payloads without a verified mapper.
- Prefer correcting the website/dataLayer contract to GA4 event-level fields
  and `items` arrays over creating custom GTM variables that guess missing
  values from old pushes.

## Official GA4 DataLayer And Event Payload Contract

For GA4, official documentation review must cover both:

- the GA4 tag/event configuration in GTM; and
- the website event payload or dataLayer format that feeds the tag.

Do not treat a GA4 Event tag as correct merely because the event name is a
standard GA4 event. First verify that the website/dataLayer event can produce the
official GA4 payload at the outgoing GA4 boundary.

For every GA4 standard or ecommerce event in the container, create a schema map:

| Field | Required check |
| --- | --- |
| Implemented event | GTM tag event name and firing trigger event. |
| Official event | GA4 standard/recommended event name from Google docs. |
| Website/dataLayer event | Actual `dataLayer.push()` event name or runtime event source. |
| Expected parameters | Official event-level parameters, such as `value`, `currency`, `transaction_id`, `tax`, `shipping`, `coupon`, `payment_type`, `shipping_tier`, `item_list_id`, or `item_list_name`. |
| Expected items | Official `items` array of GA4 item objects. |
| Expected item fields | `item_id`, `item_name`, `item_brand`, `item_category`, `item_category2`-`item_category5`, `item_variant`, `price`, `quantity`, `discount`, `coupon`, `index`, `item_list_id`, `item_list_name`, and other official item-scoped fields when present. |
| GTM source paths | Data Layer Variable paths used by the tag, such as `ecommerce.items`, `ecommerce.value`, `ecommerce.currency`, or any house-style equivalent that maps to the same official payload. |
| Legacy path risk | Any UA Enhanced Ecommerce path used, such as `ecommerce.purchase.actionField.*`, `ecommerce.purchase.products.*`, `ecommerce.add.products.*`, `ecommerce.detail.products.*`, `ecommerce.impressions`, or `ecommerce.currencyCode`. |
| Outcome | Correct, GTM mapping fix, website/dataLayer fix required, or blocked pending Preview/debug evidence. |

GA4 ecommerce audit rules:

- Treat official GA4 event payloads as the target contract: event-level fields
  plus an `items` array of GA4 item objects.
- For GTM implementations, verify the dataLayer payload that fires the Custom
  Event trigger. The event should carry or make available the same event-context
  parameters expected by GA4.
- If the tag uses Data Layer Variables, check the exact DLV paths and expected
  output types. A GA4 item array should not be built from a scalar product ID or
  a stale product-detail path.
- Treat Universal Analytics Enhanced Ecommerce paths as migration evidence, not
  proof of GA4 correctness. They are suspect until a documented mapper or
  Preview/debug evidence proves that the outgoing GA4 payload contains official
  GA4 fields.
- Do not let UA sunset logic hide under neutral names such as `DL - Revenue`,
  `GA4 - Items`, or `DL - Product ID`. Inspect the actual dataLayer path and
  every consumer.
- Do not create custom JavaScript to invent missing GA4 event parameters that
  the website should send, such as `value`, `currency`, `transaction_id`, or
  `items`. Mark the website/dataLayer contract as missing.
- Helper variables are acceptable only when they transform a complete current
  event payload into the official shape, normalize known field names, add null
  guards, or avoid duplicated logic. They are not a substitute for missing
  source data.
- If the GA4 tag has `sendEcommerceData`/dataLayer-source behavior enabled, also
  inspect any manually added event parameters. Manual overrides can point to
  wrong old paths even when the tag is set to read ecommerce data.
- Validate in GTM Preview/Tag Assistant and GA4 DebugView. DebugView should show
  the event-level parameters and the `items` tab/array for ecommerce events.

## GA4 And Google Tags

Check:

- Google-event classification: GA4/current Google tag by default, UA only as an
  explicit, documented exception;
- Google tag / GA4 configuration implementation path;
- GA4 events fire after the required config/base behavior;
- official GA4 recommended events and ecommerce event documentation is checked
  before judging event names, dataLayer format, variables, and payloads;
- each GA4 standard/ecommerce event has a schema map comparing official
  parameters to actual dataLayer paths and outgoing GA4 payload;
- transaction IDs, item arrays, currency, value, coupon, and affiliation are
  populated consistently;
- custom dimensions/parameters do not contain PII;
- duplicate page_view or ecommerce events;
- deprecated UA tags, UA variables, and UA-only ecommerce logic;
- Google Ads conversion linker and Ads conversion tags when Ads is in scope;
- consent mode behavior for Google tags in relevant regions.

When legacy event migration is needed, validate against the actual dataLayer
before applying the starter map:

| Legacy event | GA4 candidate |
| --- | --- |
| productDetailImpression | view_item |
| product listing | view_item_list |
| addToCart | add_to_cart |
| removeFromCart | remove_from_cart |
| purchaseImpression | purchase |

Validate ecommerce payload semantics, not only event names:

- `items` should be an array of item objects for GA4 ecommerce events;
- `value`, `tax`, `shipping`, and item prices should be numeric or numeric
  strings according to the destination's accepted format;
- `currency` should be an ISO currency code and should match the event value;
- `transaction_id` should be stable and unique per purchase;
- item category, ID, name, quantity, and price should come from the same event
  context;
- fixed-index variables such as product `0` or `1` are suspect for multi-item
  carts unless the vendor requires a single item and the business accepts that
  limitation.
- variables that read UA Enhanced Ecommerce paths are suspect for GA4 until the
  audit proves a valid mapping to official GA4 event-level and item-scoped
  fields.
- if an active Google tag or Google-named variable still reads a UA path after
  cleanup, mark the cleanup incomplete unless the report includes the mapper,
  outgoing payload proof, and owner-approved UA exception.

Optional GA4 cleanup opportunity: identify missing standard or recommended events that
would be useful for the business, such as ecommerce funnel events. Before
proposing tag creation, verify whether the website/dataLayer already emits the
needed event and parameters. If the dataLayer is not ready, report the missing
event/dataLayer contract as the prerequisite instead of creating a tag that
cannot send valid data.

## Mandatory Standard Ecommerce Variable Checks

Always review standard and frequently reused ecommerce variables, even when the
container has many custom tags. These variables often power several vendors, so
small logic errors can corrupt analytics, advertising, affiliate, and remarketing
payloads at the same time.

At minimum, identify variables for:

- transaction ID, order ID, affiliation, coupon, currency, revenue, value, tax,
  shipping, discount, subtotal, and total price;
- total quantity, item count, cart size, and product quantity;
- product/item IDs, SKUs, names, brands, categories, variants, prices,
  quantities, images, URLs, and list positions;
- `items`, `products`, checkout products, purchase products, add-to-cart
  products, remove-from-cart products, and impression products;
- derived helper variables used by Meta, TikTok, Pinterest, Google Ads,
  Floodlight, affiliates, feeds, or custom HTML tags.

For each standard ecommerce variable, check:

- the dataLayer path or source event, including whether it reads the current
  event or searches stale dataLayer history;
- the expected output type: number, numeric string, scalar ID, array, object,
  array of objects, JSON string, joined string, or boolean;
- logical formula correctness, including whether total quantity reads quantity
  fields instead of price fields and whether total price avoids duplicated
  indexes or missing items;
- multi-item support, including dynamic item loops instead of fixed product
  `0`, `1`, `2` indexes when the destination expects all items;
- null, missing value, empty array, parsing, and `NaN` handling;
- currency/value consistency and whether price totals multiply unit price by
  quantity where required;
- every consuming tag field and whether that destination expects the same shape.

Surface concrete logic errors as their own findings when they affect revenue,
conversion, or remarketing quality. State the affected consumers and the logical
consequence, for example: "total quantity sums one quantity and two prices, so
the consuming vendor tag receives a quantity that can be larger than the number
of cart items."

## Server-Side GTM

Only audit server-side GTM if in scope or visible in the evidence.

Check:

- tagging server URL uses a same-origin or first-party custom domain where
  appropriate;
- endpoint is reachable and receives browser events;
- CSP, firewall, or ad-blocking behavior blocks the endpoint;
- production mode, server count/redundancy, monitoring, and alerting;
- clients, tags, transformations, and forwarding rules;
- consent and privacy configuration across browser-to-server and server-to-vendor
  flows;
- non-GA4/vendor-specific parameters are excluded or transformed before being
  sent to GA4;
- templates, clients, and server container runtime are current.

Flag the old Google Optimize/server-side mixed check as obsolete. Optimize is a
sunset product and should be handled as deprecated tag cleanup, not as a current
server-side endpoint validation rule.

## Vendor Pixels And Marketing Tags

For Meta, LinkedIn, TikTok, Pinterest, Reddit, X/Twitter, affiliates, and other
vendors:

- identify base/config/loaders separately from event-specific conversion tags;
- check that base tags fire before dependent events when required;
- check duplicate pageview/conversion events;
- do not preserve a page-specific duplicate `PageView` as a substitute for a
  real funnel/conversion event. If checkout, lead, signup, or payment intent is
  needed, use the vendor's official event when the dataLayer can support it; if
  not, mark dataLayer/event readiness as the blocker.
- prefer native tags or maintained templates where feasible;
- verify consent gating and regional rules;
- inspect payload fields for PII, incorrect value/currency, missing IDs, or
  hardcoded product assumptions;
- validate event ordering with Tag Assistant/network evidence when possible.

For media/vendor payloads, verify field-level shape:

- product IDs, content IDs, item IDs, categories, and item lists often need
  arrays or objects, not one scalar dataLayer variable;
- when the vendor expects an array/object, require a custom JS/helper variable or
  template field that builds that shape from the current event's products/items;
- verify the helper variable returns the expected type for empty carts, one item,
  multiple items, missing fields, and special characters;
- confirm IDs, names, categories, values, quantities, and currency all come from
  the same ecommerce event context;
- check that custom JS variables do not accidentally return `undefined`, `NaN`,
  `[object Object]`, comma-joined values where arrays are expected, or stale data
  from a previous dataLayer push.

For each vendor, compare the implemented event names, base/event sequencing,
required parameters, recommended parameters, and data types to official vendor
documentation when available. Missing standard vendor events can be proposed as
an optional cleanup opportunity only when the website/dataLayer can provide the required
event context and parameters. If not, make the dataLayer or site event
instrumentation the prerequisite.

Meta-specific checks:

- base code is not mixed with `noscript` in a custom HTML tag unless there is a
  documented reason;
- PageView and base/init behavior are clearly separated or intentionally
  combined;
- event tags do not fire before the base/init dependency;
- browser pixel and Conversions API/server-side duplicates use deduplication IDs
  where applicable.

## Cleanup Heuristics

Prioritize changes that improve:

- privacy compliance and consent consistency;
- revenue/conversion accuracy;
- GA4 ecommerce payload correctness;
- maintainability through reusable variables and triggers;
- performance by reducing duplicate vendors, redundant loaders, and custom HTML;
- release safety through naming, folders, workspaces, and version descriptions.

Prefer consolidation when:

- multiple tags differ only by ID, market, or vendor parameter and can use lookup
  tables safely;
- repeated custom JS logic appears in several tags;
- trigger conditions can be represented by a reusable helper variable;
- multiple consent triggers express the same rule with slightly different names.
- many market/page/event triggers share the same event plus one hostname, path,
  language, or product-line condition;
- several variables read sibling paths from the same ecommerce array and could be
  replaced by one typed helper object or item-array transformer;
- vendor tags repeat the same payload construction and differ only by event name
  or vendor ID.

Avoid over-consolidation when it hides business ownership, creates a single risky
mega-tag, or makes QA harder.

## Scenario-Specific Intelligence

Before finalizing findings, decide whether any of these scenarios apply. If yes,
load `operation-schema.md` and include the scenario in the cleanup plan.

| Scenario | Signals | Extra audit checks |
| --- | --- | --- |
| Ecommerce accuracy | GA4 ecommerce, Ads conversions, Meta/TikTok/Pinterest/Criteo/affiliate product fields. | Current event payload, item arrays, value/currency, transaction IDs, multi-item handling, vendor field shape. |
| Consent/CMP | Didomi, OneTrust, Cookiebot, Axeptio, Commanders Act, native consent settings, Consent Initialization triggers. | Default/update timing, regional rules, pageview/base consistency, legal-owner blockers. |
| SPA/PWA | History triggers, route variables, virtual pageview tags, frontend framework URLs. | Runtime route changes, duplicate pageviews, stale dataLayer state, async ecommerce pushes. |
| Multi-market/language | Country codes, hostnames, currencies, language folders, market-specific IDs. | Whether scope is enforced by triggers/variables, unclear token clarification, lookup/regex consolidation feasibility. |
| One-tag gateway | Dispatcher custom HTML, lookup-table routing, shared loaders, server endpoint. | Blast radius, observability, consent routing, vendor-specific payload preservation. |
| Server-side GTM | Server container, first-party endpoint, GA4 client, transformations, CAPI tags. | Browser-to-server payload, server-to-vendor payload, consent forwarding, deduplication IDs, monitoring. |
| Emergency fix | User asks for fast repair or production breakage. | Limit mutation scope, record skipped cleanup, recommend full follow-up audit. |

Do not force every scenario into every audit. Select scenarios from evidence and
state `Not applicable` when the pattern is absent.

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
