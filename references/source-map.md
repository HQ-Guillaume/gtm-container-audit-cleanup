# Source Map And Freshness Rules

Use this reference to keep the skill maintainable as Google Tag Manager, GA4,
consent mode, and server-side tagging evolve. Verify current official docs when
the finding depends on product behavior, legal/privacy-sensitive configuration,
or a deprecated/sunset product.

## Official Sources To Prefer

Use these as fast entry points, not as frozen truth. Re-open the official page or
search the official documentation site again when payload correctness, consent,
deprecation, or a formal client report depends on the current rule.

## Frequently Consulted Documentation Index

This index is a shortcut for common audits. `Access checked` means the URL was
reviewed as an official or vendor-owned entry point for this skill; it does not
mean the page content should be treated as permanently current.

| Area | Official/vendor source | URL | Access checked |
| --- | --- | --- | --- |
| GTM API | Google Tag Manager API overview | <https://developers.google.com/tag-platform/tag-manager/api/v2> | 2026-06-26 |
| GTM API | Google Tag Manager API developer guide | <https://developers.google.com/tag-platform/tag-manager/api/v2/devguide> | 2026-06-26 |
| GTM import | Container export and import | <https://support.google.com/tagmanager/answer/6106997> | 2026-06-26 |
| GTM dataLayer | The data layer | <https://developers.google.com/tag-platform/tag-manager/datalayer> | 2026-06-26 |
| GA4 ecommerce | Measure ecommerce | <https://developers.google.com/analytics/devguides/collection/ga4/ecommerce> | 2026-06-26 |
| GA4 events | Recommended events | <https://developers.google.com/analytics/devguides/collection/ga4/reference/events> | 2026-06-26 |
| Meta Pixel | Pixel reference | <https://developers.facebook.com/docs/meta-pixel/reference/> | 2026-06-26 |
| Meta Pixel | Conversion tracking | <https://developers.facebook.com/docs/meta-pixel/implementation/conversion-tracking/> | 2026-06-26 |
| Meta CAPI | Custom data parameters | <https://developers.facebook.com/documentation/ads-commerce/conversions-api/parameters/custom-data> | 2026-06-26 |
| TikTok | API for Business documentation | <https://business-api.tiktok.com/portal/docs> | 2026-06-26 |
| TikTok | Standard events and parameters | <https://ads.tiktok.com/help/article/standard-events-parameters> | 2026-06-26 |
| Microsoft Ads | Universal Event Tracking | <https://learn.microsoft.com/en-us/advertising/guides/universal-event-tracking?view=bingads-13> | 2026-06-26 |
| Pinterest | Pinterest Tag conversion tracking | <https://developers.pinterest.com/docs/track-conversions/pinterest-tag/> | 2026-06-26 |
| Snapchat | Snap Pixel | <https://developers.snap.com/marketing-api/Ads-API/snap-pixel> | 2026-06-26 |
| LinkedIn | Insight Tag conversion tracking | <https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversion-tracking> | 2026-06-26 |
| Criteo | OneTag events and parameters | <https://help.criteo.com/kb/guide/en/all-criteo-onetag-events-and-parameters-vZbzbEeY86/Steps/775825> | 2026-06-26 |
| Didomi | GTM integration | <https://developers.didomi.io/cmp/web-sdk/third-parties/tags-management/tag-managers/google-tag-manager> | 2026-06-26 |
| OneTrust | GTM Cookie Consent integration | <https://my.onetrust.com/s/article/UUID-301b21c8-a73a-05e8-175a-36c9036728dc> | 2026-06-26 |
| OneTrust | Google Consent Mode integration | <https://my.onetrust.com/s/article/UUID-d81787f6-685c-2262-36c3-5f1f3369e2a7> | 2026-06-26 |
| Cookiebot | GTM deployment | <https://support.cookiebot.com/hc/en-us/articles/360003793854-Google-Tag-Manager-deployment> | 2026-06-26 |
| Cookiebot | Google Consent Mode | <https://support.cookiebot.com/hc/en-us/articles/360016047000-Implementing-Google-Consent-Mode> | 2026-06-26 |
| Axeptio | GTM integration | <https://support.axeptio.eu/en/articles/273991-integrate-axeptio-via-google-tag-manager> | 2026-06-26 |
| Google CMP setup | OneTrust CMP in GTM | <https://support.google.com/tagmanager/answer/14545200> | 2026-06-26 |
| Google CMP setup | Axeptio CMP in GTM | <https://support.google.com/tagmanager/answer/14705891> | 2026-06-26 |
| GTM consent | Consent mode support | <https://support.google.com/tagmanager/answer/10718549> | 2026-06-26 |

For vendors not listed here, search official vendor documentation first. If a
vendor has no official setup or event reference, document the search path and
lower confidence.

### Google Tag, GTM, GA4, Ads, And Floodlight

- Google Tag Platform overview:
  <https://developers.google.com/tag-platform/devguides>
- Analyze existing Google tag configurations:
  <https://developers.google.com/tag-platform/devguides/existing>
- GTM data layer:
  <https://developers.google.com/tag-platform/tag-manager/datalayer>
- GTM with Content Security Policy:
  <https://developers.google.com/tag-platform/security/guides/csp>
- Consent mode overview:
  <https://developers.google.com/tag-platform/security/concepts/consent-mode>
- Set up consent mode on websites:
  <https://developers.google.com/tag-platform/security/guides/consent>
- Troubleshoot consent mode with Tag Assistant:
  <https://developers.google.com/tag-platform/security/guides/consent-debugging>
- Consent APIs for GTM templates:
  <https://developers.google.com/tag-platform/tag-manager/templates/consent-apis>
- GA4 events setup:
  <https://developers.google.com/analytics/devguides/collection/ga4/events>
- GA4 recommended events:
  <https://developers.google.com/analytics/devguides/collection/ga4/reference/events>
- GA4 recommended events by business vertical:
  <https://developers.google.com/analytics/devguides/collection/ga4/reference/recommended-events>
- GA4 ecommerce measurement:
  <https://developers.google.com/analytics/devguides/collection/ga4/ecommerce>
- GA4 purchase event setup:
  <https://developers.google.com/analytics/devguides/collection/ga4/set-up-ecommerce>
- GA4 ecommerce validation:
  <https://developers.google.com/analytics/devguides/collection/ga4/validate-ecommerce>
- GA4 event parameters:
  <https://developers.google.com/analytics/devguides/collection/ga4/event-parameters>
- GA4 Measurement Protocol:
  <https://developers.google.com/analytics/devguides/collection/protocol/ga4>
- Google Ads conversions with GTM:
  <https://support.google.com/tagmanager/answer/6105160>
- Conversion linker:
  <https://support.google.com/tagmanager/answer/7549390>
- Floodlight in GTM:
  <https://support.google.com/campaignmanager/answer/3183388>
- Floodlight Google tag format:
  <https://support.google.com/campaignmanager/answer/7554821>
- Floodlight dataLayer values in GTM:
  <https://support.google.com/campaignmanager/answer/4599566>
- Server-side tagging overview:
  <https://developers.google.com/tag-platform/tag-manager/server-side>
- Server-side custom domain / same-origin guidance:
  <https://developers.google.com/tag-platform/tag-manager/server-side/custom-domain>
- Send data to server-side Tag Manager:
  <https://developers.google.com/tag-platform/tag-manager/server-side/send-data>
- Universal Analytics sunset:
  <https://support.google.com/analytics/answer/10089681>
- Google Optimize sunset:
  <https://support.google.com/analytics/answer/12979939>

### Common Media And Advertising Vendors

- Meta Pixel reference:
  <https://developers.facebook.com/docs/meta-pixel/reference/>
- Meta Pixel conversion tracking:
  <https://developers.facebook.com/docs/meta-pixel/implementation/conversion-tracking/>
- Meta Conversions API:
  <https://developers.facebook.com/documentation/ads-commerce/conversions-api>
- Meta Conversions API parameters:
  <https://developers.facebook.com/documentation/ads-commerce/conversions-api/parameters>
- TikTok API for Business documentation:
  <https://business-api.tiktok.com/portal/docs>
- TikTok standard events and parameters:
  <https://ads.tiktok.com/help/article/standard-events-parameters>
- TikTok parameter reference:
  <https://ads.tiktok.com/help/article/about-parameters>
- Pinterest Tag conversion tracking:
  <https://developers.pinterest.com/docs/track-conversions/pinterest-tag/>
- Pinterest conversions API:
  <https://developers.pinterest.com/docs/track-conversions/track-conversions-in-the-api/>
- Pinterest Tag Helper:
  <https://developers.pinterest.com/docs/api-features/tag-helper/>
- Snap Pixel:
  <https://developers.snap.com/marketing-api/Ads-API/snap-pixel>
- Snap Conversions API:
  <https://developers.snap.com/marketing-api/Conversions-API/Introduction>
- Snap Conversions API parameters:
  <https://developers.snap.com/marketing-api/Conversions-API/Parameters>
- Microsoft Advertising UET:
  <https://learn.microsoft.com/en-us/advertising/guides/universal-event-tracking?view=bingads-13>
- Microsoft Advertising UET setup:
  <https://learn.microsoft.com/en-us/advertising/msa-help/hlp_ba_conc_uet_setup_master>
- Microsoft Advertising Conversions API:
  <https://learn.microsoft.com/en-us/advertising/guides/uet-conversion-api-integration?view=bingads-13>
- LinkedIn Insight Tag conversion tracking:
  <https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/conversion-tracking>
- LinkedIn Conversions API use cases:
  <https://learn.microsoft.com/en-us/linkedin/marketing/conversions/conversions-usecase>
- LinkedIn conversion deduplication:
  <https://learn.microsoft.com/en-us/linkedin/marketing/conversions/deduplication>
- Reddit Pixel installation:
  <https://business.reddithelp.com/s/article/Install-the-Reddit-Pixel-on-your-website>
- Reddit Pixel manual conversion events:
  <https://business.reddithelp.com/s/article/manual-conversion-events-with-the-reddit-pixel>
- Reddit Conversions API:
  <https://business.reddithelp.com/s/article/Conversions-API>
- Reddit event deduplication:
  <https://business.reddithelp.com/s/article/event-deduplication>
- X website conversion tracking:
  <https://business.x.com/en/help/campaign-measurement-and-analytics/conversion-tracking-for-websites>
- X Ads API web conversions:
  <https://docs.x.com/x-ads-api/measurement/web-conversions>
- Criteo OneTag events and parameters:
  <https://help.criteo.com/kb/guide/en/all-criteo-onetag-events-and-parameters-vZbzbEeY86/Steps/775825>
- Awin tracking overview:
  <https://help.awin.com/developers/docs/tracking-overview-1>
- Awin GTM client-side tracking:
  <https://help.awin.com/developers/docs/gtm-client-side>
- Awin sales tracking:
  <https://help.awin.com/developers/docs/implementing-sales-tracking>

### CMP And Consent Vendors

- Didomi GTM integration overview:
  <https://developers.didomi.io/cmp/web-sdk/third-parties/tags-management/tag-managers/google-tag-manager>
- Didomi/GTM integration:
  <https://developers.didomi.io/cmp/web-sdk/third-parties/tags-management/tag-managers/google-tag-manager/configure-the-didomi-gtm-integration>
- Didomi GTM template:
  <https://developers.didomi.io/cmp/web-sdk/third-parties/tags-management/tag-managers/google-tag-manager/didomis-gtm-template>
- Didomi Google Consent Mode:
  <https://developers.didomi.io/cmp/web-sdk/third-parties/direct-integrations/google-consent-mode>
- Didomi Web SDK events:
  <https://developers.didomi.io/cmp/web-sdk/reference/events>
- Didomi Web SDK API:
  <https://developers.didomi.io/cmp/web-sdk/reference/api>

Use official Google sources first. Use vendor documentation for non-Google
vendors such as Meta, LinkedIn, TikTok, Pinterest, Reddit, X/Twitter, affiliate
platforms, and CMPs. Use blogs only as secondary interpretation, not as the basis
for a finding.

For every vendor/event family in the container, look for official setup,
standard-event, parameter, and validation documentation. Treat official docs as
the payload contract unless the user explicitly overrides it. Use the entries in
this file first when the vendor is listed. If the vendor, CMP, template, or event
family is not listed here, search the internet for the vendor's official
documentation before judging correctness. If an official source cannot be found
after that search, document the search and lower confidence.

## Current Baseline Assumptions

As of 2026-06-26:

- GTM web installation expects the script snippet in the page `<head>` and the
  `noscript` snippet immediately after the opening `<body>` where applicable.
- GTM includes consent initialization, consent settings, and Consent Overview
  features for managing tag behavior based on consent.
- Consent mode communicates consent state to Google tags; it does not provide a
  consent banner by itself.
- Standard Universal Analytics stopped processing new data on 2023-07-01, and
  the Universal Analytics 360 processing extension ended on 2024-07-01.
- Because Universal Analytics is sunset, ambiguous Google Analytics/event and
  ecommerce tracking should be treated as GA4/current Google tag tracking by
  default. Use UA only when the export, property ID, user instruction, or
  verified migration mapper proves an explicit legacy exception.
- Google Optimize and Optimize 360 are no longer available as of 2023-09-30.
- Server-side tagging should use a first-party/same-origin or appropriate custom
  domain setup when possible, and production deployments should consider
  performance, security, monitoring, and redundancy.

## When To Re-Verify

Browse or check official docs again when:

- the user asks for the latest/current/recent guidance;
- consent mode, privacy, EEA, Ads, GA4, or CMP behavior affects the finding;
- GA4 recommended/ecommerce events, official dataLayer/event payload format, or
  vendor standard events and parameters are used to judge correctness;
- a finding depends on product deprecation, sunset, or migration status;
- server-side tagging setup, production mode, or endpoint guidance is in scope;
- a vendor template/native tag capability may have changed;
- the audit will be delivered as a formal client report.

When source freshness matters, cite the source title, URL, and access date in the
audit method or notes.

## Maintenance Notes

- Keep product-specific facts here instead of duplicating them across the skill.
- Keep the main `SKILL.md` stable and procedural.
- Move large vendor-specific rules to separate references only when repeated
  audits need them.
- Remove obsolete checks instead of preserving them as active rules. Keep sunset
  products as deprecated-tag cleanup checks.
