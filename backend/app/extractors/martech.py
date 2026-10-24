from __future__ import annotations


def _tool_status(html: str, markers: tuple[str, ...]) -> str:
    lowered = html.lower()
    return "confirmed" if any(marker in lowered for marker in markers) else "unknown"


def detect_martech(html: str) -> dict[str, object]:
    return {
        "tools": {
            "ga4": {"status": _tool_status(html, ("gtag(", "googletagmanager.com/gtag/js", "google-analytics.com"))},
            "gtm": {"status": _tool_status(html, ("googletagmanager.com/gtm.js", "gtm-"))},
            "google_ads": {"status": _tool_status(html, ("googleadservices.com", "google_conversion_id", " aw-"))},
            "meta_pixel": {"status": _tool_status(html, ("fbq(", "fbevents.js", "connect.facebook.net"))},
            "tiktok_pixel": {"status": _tool_status(html, ("ttq.", "analytics.tiktok.com", "tiktok-pixel"))},
        }
    }
