#!/usr/bin/env python3
"""Shared GTM taxonomy patterns for audit helper scripts."""

from __future__ import annotations

import json
import re
from typing import Any

ECOM_RE = re.compile(
    r"ecommerce|revenue|value|price|quantity|qty|currency|tax|shipping|"
    r"transaction|product|item|sku|category|coupon",
    re.I,
)
LEGACY_UA_ECOM_RE = re.compile(
    r"ecommerce\.(purchase\.actionField|purchase\.products|add\.products|"
    r"detail\.products|checkout\.products|checkout\.actionField|"
    r"remove\.products|impressions|currencyCode)",
    re.I,
)
HIGH_IMPACT_RE = re.compile(
    r"consent|cmp|didomi|onetrust|cookie|ga4|google|ads|adwords|"
    r"floodlight|doubleclick|meta|facebook|pixel|tiktok|snap|pinterest|"
    r"linkedin|microsoft|bing|criteo|awin|affiliate|piano|gam|adserver|"
    r"server|s2s|purchase|checkout|cart|lead|form|conversion|ecommerce|"
    r"transaction|revenue|value|price|quantity|item|product|page.?view",
    re.I,
)
SERVER_SIDE_RE = re.compile(
    r"server_container_url|transport_url|first.?party|server.?side|s2s|"
    r"gateway|gtm server|server container",
    re.I,
)

VENDOR_PATTERNS = [
    ("GA4 / Google tag", re.compile(r"\bga4\b|google analytics|measurement id|G-[A-Z0-9]+", re.I)),
    ("Google Ads", re.compile(r"google ads|adwords|aw-|conversion linker", re.I)),
    ("Floodlight", re.compile(r"floodlight|doubleclick|dc-[0-9]|activity", re.I)),
    ("Meta", re.compile(r"\bmeta\b|facebook|fbq|pixel id|content_ids|contents", re.I)),
    ("TikTok", re.compile(r"tiktok|ttq|tik tok", re.I)),
    ("Snapchat", re.compile(r"snapchat|snap pixel|snaptr", re.I)),
    ("Pinterest", re.compile(r"pinterest|pintrk", re.I)),
    ("Microsoft Ads", re.compile(r"microsoft ads|bing|uet", re.I)),
    ("LinkedIn", re.compile(r"linkedin|insight tag|lintrk", re.I)),
    ("Criteo", re.compile(r"criteo|onetag", re.I)),
    ("Awin", re.compile(r"\bawin\b|zanox", re.I)),
    ("Effinity", re.compile(r"effinity|effiliation", re.I)),
    ("Didomi", re.compile(r"didomi", re.I)),
    ("OneTrust", re.compile(r"onetrust|optanon", re.I)),
    ("Piano Analytics", re.compile(r"\bpiano\b|pa\.|page\.display|click\.action", re.I)),
    ("Google Ad Manager", re.compile(r"\bgam\b|googletag|publisher tag|gpt", re.I)),
]
ECOM_ROLE_PATTERNS = [
    ("purchase", re.compile(r"purchase|order|transaction|confirmation|sale", re.I)),
    ("add_to_cart", re.compile(r"add.?to.?cart|ajout.?panier", re.I)),
    ("remove_from_cart", re.compile(r"remove.?from.?cart|retrait.?panier", re.I)),
    ("begin_checkout", re.compile(r"checkout|basket|panier", re.I)),
    ("view_item", re.compile(r"product.?detail|fiche.?produit|view.?item", re.I)),
    ("view_item_list", re.compile(r"list|category|page.?liste|view.?item.?list", re.I)),
    ("page_view", re.compile(r"page.?view|all.?pages|homepage|home.?page", re.I)),
]


def object_text(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False)


def searchable_text(obj: dict[str, Any]) -> str:
    return " ".join(str(part or "") for part in (obj.get("name"), obj.get("type"), object_text(obj)))


def detect_vendor(obj: dict[str, Any]) -> str:
    text = searchable_text(obj)
    for vendor, pattern in VENDOR_PATTERNS:
        if pattern.search(text):
            return vendor
    return "Unclassified"


def detect_ecommerce_role(obj: dict[str, Any]) -> str | None:
    text = searchable_text(obj)
    for role, pattern in ECOM_ROLE_PATTERNS:
        if pattern.search(text):
            return role
    return None


def is_high_impact(obj: dict[str, Any]) -> bool:
    return bool(HIGH_IMPACT_RE.search(searchable_text(obj)))


def has_server_side_signal(obj: dict[str, Any]) -> bool:
    return bool(SERVER_SIDE_RE.search(searchable_text(obj)))
