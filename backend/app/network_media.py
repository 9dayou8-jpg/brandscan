from __future__ import annotations

import json
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


def _platform_for_url(url: str) -> str | None:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()
    if "twitter.com" in host or host == "t.co" or "p_id=twitter" in query:
        return "X (Twitter)"
    if "google-analytics.com" in host or "googletagmanager.com" in host or "/collect" in path and "google" in host:
        return "Google"
    if "facebook.com" in host or "connect.facebook.net" in host:
        return "Meta"
    if "tiktok" in host:
        return "TikTok"
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
        item = grouped.setdefault(platform, {"platform": platform, "status": "confirmed", "events": [], "evidence": []})
        item["events"] = list(dict.fromkeys([*item["events"], *_events_from_query(parsed)]))
        evidence = f"{parsed.netloc}{parsed.path}"
        if evidence not in item["evidence"]:
            item["evidence"].append(evidence)
    return {
        "request_count": len(urls),
        "media_inventory": list(grouped.values()),
        "unclassified_requests": unclassified,
    }
