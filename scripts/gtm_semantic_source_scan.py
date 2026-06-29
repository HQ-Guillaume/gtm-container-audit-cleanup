#!/usr/bin/env python3
"""Create an independent semantic-source scan from a GTM export.

This script does not consume the deterministic baseline. It reads the source
container JSON directly and emits review candidates that seed D1-D3 semantic
analysis: business purpose, event contract, data source, output shape, consent,
custom code, and owner/runtime blockers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from gtm_lib import container_version, refs

GOOGLE_RE = re.compile(r"\b(?:GA4|Google Analytics|Google Ads|gtag|GAds)\b", re.I)
UA_RE = re.compile(
    r"\b(?:UA-\d+(?:-\d+)+|Universal Analytics|Enhanced Ecommerce|"
    r"ecommerce\.(?:purchase|add|remove|detail|checkout|impressions)|"
    r"checkoutOption|checkout_step|addToCart|removeFromCart|productDetailImpression|"
    r"productImpression|purchaseImpression)\b",
    re.I,
)
FIXED_INDEX_RE = re.compile(
    r"\becommerce\.(?:purchase|add|remove|detail|checkout)\.products"
    r"(?:\[\d+\]|\.\d+)(?:[A-Za-z0-9_\.\[\]]*)",
    re.I,
)
ECOMMERCE_RE = re.compile(
    r"\b(?:purchase|transaction|order|cart|checkout|item|items|product|products|"
    r"value|currency|revenue|shipping|tax|coupon|add_to_cart|begin_checkout)\b",
    re.I,
)
BUSINESS_VALUE_RE = re.compile(
    r"\b(?:total|subtotal|order[_\s-]?value|revenue|amount|value|quantity|qty|"
    r"item[_\s-]?count|cart[_\s-]?size|price)\b",
    re.I,
)
ARITHMETIC_OR_INDEX_RE = re.compile(
    r"(?:\+|\*|/|parseFloat\s*\(|parseInt\s*\(|Number\s*\(|"
    r"products?(?:\.|\[)\d+|items?(?:\.|\[)\d+)",
    re.I,
)
VALUE_SOURCE_PATH_RE = re.compile(
    r"\b(?:ecommerce|items?|products?|transaction|order|cart|checkout)"
    r"(?:[A-Za-z0-9_\.\[\]]+)",
    re.I,
)
NUMERIC_OPERATION_RE = re.compile(
    r"parseFloat\s*\(|parseInt\s*\(|Number\s*\(|"
    r"(?:\{\{[^}]+\}\}|[A-Za-z0-9_\]\).]+)\s*[+*/]\s*(?:\{\{[^}]+\}\}|[A-Za-z0-9_\[(.]+)",
    re.I,
)
CONSENT_RE = re.compile(
    r"\b(?:consent|cmp|onetrust|didomi|cookiebot|cookie consent|ad_storage|"
    r"analytics_storage|ad_user_data|ad_personalization|gdpr|tcf)\b",
    re.I,
)
CUSTOM_CODE_RE = re.compile(
    r"\b(?:innerHTML|document\.write|addEventListener|localStorage|sessionStorage|"
    r"document\.cookie|fetch\(|XMLHttpRequest|sendBeacon|createElement|eval\()\b",
    re.I,
)
MEDIA_VENDOR_RE = re.compile(
    r"\b(?:Meta|Facebook|TikTok|Pinterest|LinkedIn|Microsoft|Bing|Floodlight|"
    r"DV360|CM360|Snap|Criteo|Tradedoubler|Awin|Piano|Marfeel|Hotjar)\b",
    re.I,
)
LEAD_RE = re.compile(r"\b(?:lead|form|signup|sign_up|contact|quote|newsletter)\b", re.I)
SERVER_RE = re.compile(r"\b(?:server|server-side|s2s|transport_url|first-party|gateway)\b", re.I)
IDENTITY_IGNORED = {"accountId", "containerId", "fingerprint", "path"}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def stable_payload(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_payload(value).encode("utf-8")).hexdigest()[:16]


def comparable_config(obj: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in obj.items() if key not in IDENTITY_IGNORED}


def object_id(obj: dict[str, Any], layer: str) -> str:
    keys = {
        "tag": "tagId",
        "trigger": "triggerId",
        "variable": "variableId",
        "customTemplate": "templateId",
    }
    value = obj.get(keys[layer]) or obj.get("name")
    return "" if value is None else str(value)


def object_name(obj: dict[str, Any]) -> str:
    return str(obj.get("name") or "")


def object_type(obj: dict[str, Any], layer: str) -> str:
    return str(obj.get("type") or ("customTemplate" if layer == "customTemplate" else ""))


def reconciliation_key(layer: str, obj: dict[str, Any]) -> str:
    return "|".join(
        [
            layer,
            object_id(obj, layer),
            object_name(obj),
            object_type(obj, layer),
            stable_hash(comparable_config(obj)),
        ]
    )


def topic_defaults(topic: str) -> dict[str, str]:
    defaults = {
        "google_event_contract": (
            "owner_decision_needed",
            "Google events should use the current official event name, parameters, consent state, and trigger context.",
            "Confirm official Google/GA4 contract before proposing a mapping or cleanup operation.",
            "Medium",
        ),
        "legacy_universal_analytics_setup": (
            "fix_required",
            "Current Google or vendor tracking should not depend on old Universal Analytics ecommerce structures unless a verified mapper exists.",
            "Migrate, delete, or document a legacy exception with outgoing payload proof.",
            "High",
        ),
        "fixed_index_ecommerce_logic": (
            "fix_required",
            "Ecommerce logic should use the current event item array or official order value, not one fixed product position.",
            "Fix item/value logic or mark a single-item exception with runtime proof.",
            "High",
        ),
        "ecommerce_data_contract": (
            "owner_decision_needed",
            "Revenue, item, cart, and order signals should match the destination event contract.",
            "Trace source data and consumers before fixing or documenting a blocker.",
            "Medium",
        ),
        "business_logic_sanity": (
            "fix_required",
            "Business numbers should match the real order, cart, item, lead, or content event context.",
            "Fix illogical formula/source use or block on website/dataLayer evidence.",
            "High",
        ),
        "consent_or_privacy_logic": (
            "owner_decision_needed",
            "Consent logic should match the confirmed CMP purpose/vendor mapping and timing.",
            "Confirm mapping and QA accept/refuse/update states before mutation.",
            "Medium",
        ),
        "custom_code_semantic_review": (
            "owner_decision_needed",
            "Custom code should have a clear purpose, input, output, consumer, consent assumption, and QA route.",
            "Reconcile with technical code findings before delete, harden, rebuild, or consolidate decisions.",
            "Medium",
        ),
        "media_vendor_payload": (
            "owner_decision_needed",
            "Media/vendor payloads should match the platform's intended reporting, bidding, audience, or attribution use.",
            "Compare event, identifiers, value/currency, consent, and deduplication to official/vendor expectations.",
            "Medium",
        ),
        "lead_or_form_measurement": (
            "owner_decision_needed",
            "Lead/form events should represent the intended lead quality, form type, and trigger moment.",
            "Confirm trigger scope, lead type, duplicate firing, and identifiers before cleanup.",
            "Medium",
        ),
        "server_or_gateway_routing": (
            "runtime_blocked",
            "Server/gateway routing should preserve consent, IDs, destination mapping, and deduplication.",
            "Collect server container, network, or vendor proof before mutation.",
            "Medium",
        ),
        "semantic_object_coverage": (
            "keep",
            "The object still needs a no-change or cleanup decision after D1-D3 coverage.",
            "Record literal behavior and no-change evidence or escalate if D3 reveals a problem.",
            "Low",
        ),
    }
    action, expected, implication, confidence = defaults[topic]
    return {
        "semantic_action_candidate": action,
        "expected_clean_state_seed": expected,
        "semantic_cleanup_implication": implication,
        "semantic_confidence_seed": confidence,
    }


def current_behavior_seed(
    layer: str, obj: dict[str, Any], topic: str, signal: str
) -> str:
    refs_list = sorted(refs(obj))
    refs_text = ", ".join(refs_list[:6])
    if len(refs_list) > 6:
        refs_text += f", +{len(refs_list) - 6} more"
    parts = [
        f"{layer} {object_id(obj, layer)} {object_name(obj)!r}",
        f"type {object_type(obj, layer)!r}",
        f"raised topic {topic} because {signal}",
    ]
    if refs_text:
        parts.append(f"references GTM variables {refs_text}")
    if layer == "tag":
        fires = ", ".join(str(value) for value in as_list(obj.get("firingTriggerId")))
        if fires:
            parts.append(f"fires from trigger IDs {fires}")
    return "; ".join(parts) + "."


def short_unique(pattern: re.Pattern[str], text: str, limit: int = 8) -> list[str]:
    return sorted({match.group(0) for match in pattern.finditer(text)})[:limit]


def semantic_signal_details(obj: dict[str, Any], topic: str) -> dict[str, Any]:
    text = object_name(obj) + " " + stable_payload(obj)
    fixed_paths = short_unique(FIXED_INDEX_RE, text)
    value_paths = short_unique(VALUE_SOURCE_PATH_RE, text)
    numeric_ops = short_unique(NUMERIC_OPERATION_RE, text)
    details: dict[str, Any] = {
        "observed_value_or_item_paths": value_paths,
        "observed_fixed_index_paths": fixed_paths,
        "observed_numeric_operations": numeric_ops,
    }
    if topic in {
        "business_logic_sanity",
        "fixed_index_ecommerce_logic",
        "ecommerce_data_contract",
    }:
        if fixed_paths:
            details["semantic_logic_risk"] = (
                "Fixed product-position evidence found; multi-item orders or carts may be misread."
            )
        elif numeric_ops:
            details["semantic_logic_risk"] = (
                "Numeric formula evidence found; source paths, output type, and consumer meaning must be checked together."
            )
        elif value_paths:
            details["semantic_logic_risk"] = (
                "Value/item path evidence found; compare source shape with the destination event contract."
            )
        else:
            details["semantic_logic_risk"] = (
                "Semantic topic was raised by naming/config context; exact runtime value source still needs D3 proof."
            )
    else:
        details["semantic_logic_risk"] = ""
    return details


def scan_topics(layer: str, obj: dict[str, Any]) -> list[tuple[str, str, str, str]]:
    text = object_name(obj) + " " + stable_payload(obj)
    obj_type = str(obj.get("type") or "")
    topics: list[tuple[str, str, str, str]] = []

    def add(topic: str, signal: str, issue: str, required_check: str) -> None:
        topics.append((topic, signal, issue, required_check))

    if layer == "tag" and obj_type.lower() in {"gaawe", "gaawc", "gtag"} or GOOGLE_RE.search(text):
        add(
            "google_event_contract",
            "Google/GA4-looking object",
            "This object may affect Google reporting or bidding.",
            "Check the official current Google event name, parameters, trigger context, and consent state.",
        )
    if UA_RE.search(text) or obj_type.lower() == "ua":
        add(
            "legacy_universal_analytics_setup",
            "Universal Analytics-style name, property, event, or ecommerce path",
            "This looks connected to the old Universal Analytics ecommerce format.",
            "Confirm whether it is obsolete, intentionally mapped, or still feeding a current tag incorrectly.",
        )
    if FIXED_INDEX_RE.search(text):
        add(
            "fixed_index_ecommerce_logic",
            "Fixed ecommerce product position path",
            "The setup reads one fixed product position instead of the full item list.",
            "Check whether multi-item carts and orders are measured correctly before cleanup decisions.",
        )
    if ECOMMERCE_RE.search(text):
        add(
            "ecommerce_data_contract",
            "Ecommerce, cart, order, value, item, or product signal",
            "This object may affect revenue, product, or remarketing data.",
            "Trace the source data, output type, consuming tag fields, and current vendor/GA4 item contract.",
        )
    if BUSINESS_VALUE_RE.search(text) and ARITHMETIC_OR_INDEX_RE.search(text):
        add(
            "business_logic_sanity",
            "Business value or quantity logic with arithmetic or fixed item positions",
            "This object may calculate a business number in a way that does not match the real order or cart.",
            "Check whether totals, prices, quantities, item counts, currency, and multi-item behavior are logically correct for the firing event and consuming tags.",
        )
    if CONSENT_RE.search(text):
        add(
            "consent_or_privacy_logic",
            "Consent, CMP, storage, privacy, or region signal",
            "This object may control whether tags are allowed to fire or send data.",
            "Confirm consent purpose/vendor mapping and test accept/refuse/update states before changing it.",
        )
    if layer in {"tag", "variable", "customTemplate"} and (
        obj_type.lower() in {"html", "jsm"} or layer == "customTemplate" or CUSTOM_CODE_RE.search(text)
    ):
        add(
            "custom_code_semantic_review",
            "Custom code or template logic",
            "The object can run code or transform data outside normal GTM fields.",
            "Record purpose, inputs, side effects, output, consumers, technical risk, and runtime QA need.",
        )
    if MEDIA_VENDOR_RE.search(text):
        add(
            "media_vendor_payload",
            "Marketing or analytics vendor signal",
            "This object may affect ad platform reporting, bidding, audiences, or attribution.",
            "Compare event name, identifiers, value/currency, consent, and deduplication to official vendor docs.",
        )
    if LEAD_RE.search(text):
        add(
            "lead_or_form_measurement",
            "Lead, form, signup, contact, quote, or newsletter signal",
            "This object may measure a user enquiry or lead action.",
            "Check trigger scope, form type, lead quality, duplicate firing, and required identifiers.",
        )
    if SERVER_RE.search(text):
        add(
            "server_or_gateway_routing",
            "Server-side, transport, first-party, or gateway signal",
            "This object may route browser data through another endpoint or server container.",
            "Validate routing, consent forwarding, destination IDs, and browser/server duplication risk.",
        )

    if not topics:
        add(
            "semantic_object_coverage",
            "No high-risk keyword detected in static source scan",
            "The object still needs coverage in a full audit, even if no obvious keyword appears.",
            "Record purpose, source/trigger, consumers, expected output, and cleanup decision or no-change evidence.",
        )

    return topics


def scan_export(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    cv = container_version(data)
    rows: list[dict[str, Any]] = []

    layers = (
        ("tag", as_list(cv.get("tag"))),
        ("trigger", as_list(cv.get("trigger"))),
        ("variable", as_list(cv.get("variable"))),
        ("customTemplate", as_list(cv.get("customTemplate"))),
    )
    for layer, items in layers:
        for obj in items:
            for topic, signal, issue, required_check in scan_topics(layer, obj):
                row_id = f"SEM-{len(rows) + 1:05d}"
                defaults = topic_defaults(topic)
                row = {
                    "semantic_finding_id": row_id,
                    "layer": layer,
                    "object_id": object_id(obj, layer),
                    "object_name": object_name(obj),
                    "type": object_type(obj, layer),
                    "object_identity": reconciliation_key(layer, obj),
                    "config_hash": stable_hash(comparable_config(obj)),
                    "semantic_scan_topic": topic,
                    "source_lens": "semantic",
                    "source_artifact_role": "raw_source_direct_scan",
                    "observed_signal": signal,
                    "current_behavior_seed": current_behavior_seed(layer, obj, topic, signal),
                    "plain_language_issue": issue,
                    "expected_behavior_seed": defaults["expected_clean_state_seed"],
                    "semantic_cleanup_implication": defaults["semantic_cleanup_implication"],
                    "semantic_action_candidate": defaults["semantic_action_candidate"],
                    "semantic_confidence_seed": defaults["semantic_confidence_seed"],
                    "required_semantic_check": required_check,
                    "blocker_or_next_evidence": required_check,
                    "referenced_gtm_variables": sorted(refs(obj)),
                    "operation_packet_required": topic != "semantic_object_coverage",
                    "source_independent_of_baseline": True,
                }
                row.update(semantic_signal_details(obj, topic))
                rows.append(row)

    return {
        "artifact": str(path),
        "kind": "gtm_independent_semantic_source_scan",
        "source_independent_of_baseline": True,
        "counts": {
            "tags": len(as_list(cv.get("tag"))),
            "triggers": len(as_list(cv.get("trigger"))),
            "variables": len(as_list(cv.get("variable"))),
            "customTemplates": len(as_list(cv.get("customTemplate"))),
            "semantic_source_rows": len(rows),
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path, help="Path to a GTM container export JSON")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    args = parser.parse_args()

    result = scan_export(args.export)
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
