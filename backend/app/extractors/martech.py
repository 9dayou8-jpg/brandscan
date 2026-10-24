from __future__ import annotations

import re


def _script_sources(html: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r'''<script\b[^>]*?\bsrc=["']([^"']+)["']''', html, flags=re.IGNORECASE)))


def _matches(html: str, markers: tuple[str, ...]) -> list[str]:
    lowered = html.lower()
    return [marker for marker in markers if marker.lower() in lowered]


def _tool_status(html: str, markers: tuple[str, ...]) -> str:
    return "confirmed" if _matches(html, markers) else "unknown"


def _media_item(html: str, platform: str, category: str, markers: tuple[str, ...]) -> dict[str, object] | None:
    evidence = _matches(html, markers)
    if not evidence:
        return None
    return {
        "platform": platform,
        "category": category,
        "status": "confirmed",
        "operating_inference": "likely",
        "evidence": evidence,
        "note": "공개 HTML에서 해당 매체의 태그 단서가 확인됨. 실제 캠페인 운영·광고비·성과는 측정하지 않음.",
    }


def detect_martech(html: str) -> dict[str, object]:
    tools = {
        "ga4": {"status": _tool_status(html, ("gtag(", "googletagmanager.com/gtag/js", "google-analytics.com"))},
        "gtm": {"status": _tool_status(html, ("googletagmanager.com/gtm.js", "gtm-"))},
        "google_ads": {"status": _tool_status(html, ("googleadservices.com", "google_conversion_id", " aw-"))},
        "meta_pixel": {"status": _tool_status(html, ("fbq(", "fbevents.js", "connect.facebook.net"))},
        "tiktok_pixel": {"status": _tool_status(html, ("ttq.", "analytics.tiktok.com", "tiktok-pixel"))},
        "first_party_analytics": {"status": _tool_status(html, ("analytics-client", "analytics.nike.com", "clickstream.halfpipe.nike.com"))},
        "new_relic": {"status": _tool_status(html, ("newrelic", "nr-data.net", "insights-collector.newrelic.com"))},
        "akamai_mpulse": {"status": _tool_status(html, ("go-mpulse.net", "boomerang", "akamai"))},
    }
    inventory: list[dict[str, object]] = []
    for item in (
        _media_item(html, "Google", "analytics_and_ads", ("gtag(", "googletagmanager.com", "google-analytics.com", "googleadservices.com")),
        _media_item(html, "Meta", "paid_media", ("fbq(", "fbevents.js", "connect.facebook.net")),
        _media_item(html, "TikTok", "paid_media", ("ttq.", "analytics.tiktok.com", "tiktok-pixel")),
        _media_item(html, "Naver", "paid_media", ("wcs.naver.net", "wcs_add", "naver.com/ad")),
        _media_item(html, "Kakao", "paid_media", ("kakaopixel", "kakaoPixel", "track.kakao.com")),
        _media_item(html, "Pinterest", "paid_media", ("pintrk(", "pinimg.com/ct", "pinterest")),
        _media_item(html, "LinkedIn", "paid_media", ("lintrk(", "snap.licdn.com", "linkedin_insight")),
        _media_item(html, "Snapchat", "paid_media", ("snaptr(", "sc-static.net", "snapchat")),
        _media_item(html, "Criteo", "paid_media", ("criteo_q", "criteo.com", "criteo")),
        _media_item(html, "Microsoft Ads", "paid_media", ("bat.bing.com", "uetq.push", "microsoftadvertising")),
        _media_item(html, "당근", "paid_media", ("daangn", "karrot", "daangnPixel")),
        _media_item(html, "토스", "paid_media", ("tossads", "ads.toss.im", "toss.im/ads")),
        _media_item(html, "First-party analytics", "first_party_analytics", ("analytics-client", "analytics.nike.com", "clickstream.halfpipe.nike.com")),
        _media_item(html, "New Relic", "observability", ("newrelic", "nr-data.net", "insights-collector.newrelic.com")),
        _media_item(html, "Akamai mPulse", "performance_analytics", ("go-mpulse.net", "boomerang", "akamai")),
    ):
        if item is not None:
            inventory.append(item)
    return {"tools": tools, "media_inventory": inventory, "script_sources": _script_sources(html)}
