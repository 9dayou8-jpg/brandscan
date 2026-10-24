from __future__ import annotations

import json
import re
from urllib.parse import parse_qs, urlparse


def _events_from_query(parsed) -> list[str]:
    query = parse_qs(parsed.query)
    events: list[str] = []
    for key in ("en", "ev", "event", "event_name"):
        events.extend(value for value in query.get(key, []) if value)
    raw_events = query.get("events", [])
    for raw in raw_events:
        try:
            payload = json.loads(raw)
            for group in payload if isinstance(payload, list) else []:
                if isinstance(group, list) and group and isinstance(group[0], str):
                    events.append(group[0])
        except json.JSONDecodeError:
            continue
    return list(dict.fromkeys(events))


def _identifiers_from_request(parsed) -> list[str]:
    query = parse_qs(parsed.query)
    identifiers: list[str] = []
    for key in ("tid", "id", "ti", "account", "pixel_id", "conversion_id"):
        identifiers.extend(value for value in query.get(key, []) if value)
    identifiers.extend(re.findall(r"(?:AW-|G-)[A-Z0-9-]+", parsed.path, flags=re.IGNORECASE))
    return list(dict.fromkeys(identifiers))


def _tag_types_for_request(parsed, platform: str) -> list[str]:
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if platform == "Google":
        types: list[str] = []
        if "google-analytics.com" in host or "analytics.google.com" in host or "/g/collect" in path:
            types.append("Google Analytics")
        if "googleadservices.com" in host or "doubleclick.net" in host or "/pagead/" in path or "aw-" in parsed.path.lower():
            types.append("Google Ads")
        if "googletagmanager.com" in host:
            types.append("Google Tag Manager")
        return types
    return {"Microsoft Ads": ["Bing Ads"], "Criteo": ["Criteo OneTag"], "Meta": ["Facebook Pixel"]}.get(platform, [])


def _platform_for_url(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()
    if "twitter.com" in host or host == "t.co" or "p_id=twitter" in query:
        return "X (Twitter)"
    if "google-analytics.com" in host or "analytics.google.com" in host or "googletagmanager.com" in host or "googleadservices.com" in host or "doubleclick.net" in host or ("/collect" in path and "google" in host) or "/pagead/" in path and "google" in host:
        return "Google"
    if "facebook.com" in host or "connect.facebook.net" in host:
        return "Meta"
    if "tiktok" in host:
        return "TikTok"
    if "analytics.nike.com" in host or "clickstream.halfpipe.nike.com" in host or "/static/analytics-client/" in path:
        return "First-party analytics"
    if "nr-data.net" in host or "newrelic.com" in host or "newrelic" in path:
        return "New Relic"
    if "go-mpulse.net" in host or "akamai" in host or "boomerang" in path:
        return "Akamai mPulse"
    if "naver" in host:
        return "Naver"
    if "kakao" in host:
        return "Kakao"
    if "linkedin" in host:
        return "LinkedIn"
    if "snapchat" in host or "sc-static.net" in host:
        return "Snapchat"
    if "criteo" in host:
        return "Criteo"
    if "bing" in host or "microsoft" in host:
        return "Microsoft Ads"
    if "daangn" in host or "karrot" in host:
        return "당근"
    if "toss" in host:
        return "토스"
    return None


def classify_runtime_requests(urls: list[str]) -> dict[str, object]:
    grouped: dict[str, dict[str, object]] = {}
    unclassified: list[str] = []
    for url in urls:
        platform = _platform_for_url(url)
        if platform is None:
            unclassified.append(url)
            continue
        parsed = urlparse(url)
        item = grouped.setdefault(platform, {"platform": platform, "status": "confirmed", "events": [], "identifiers": [], "tag_types": [], "evidence": []})
        item["events"] = list(dict.fromkeys([*item["events"], *_events_from_query(parsed)]))
        item["identifiers"] = list(dict.fromkeys([*item["identifiers"], *_identifiers_from_request(parsed)]))
        item["tag_types"] = list(dict.fromkeys([*item["tag_types"], *_tag_types_for_request(parsed, platform)]))
        evidence = f"{parsed.netloc}{parsed.path}"
        if evidence not in item["evidence"]:
            item["evidence"].append(evidence)
    return {
        "request_count": len(urls),
        "media_inventory": list(grouped.values()),
        "unclassified_requests": unclassified,
    }
