from backend.app.extractors.martech import detect_martech


HTML = """
<html><head>
<script src="https://www.googletagmanager.com/gtag/js?id=G-ABC"></script>
<script src="https://connect.facebook.net/en_US/fbevents.js"></script>
<script src="https://analytics.tiktok.com/i18n/pixel/events.js"></script>
<script src="https://wcs.naver.net/wcslog.js"></script>
<script>kakaoPixel('123'); pintrk('load', '456'); lintrk('track'); snaptr('init', '789'); criteo_q.push({event:'viewItem'}); uetq.push('event'); daangnPixel('1'); tossads.track('view')</script>
</head></html>
"""


def test_martech_returns_detected_media_inventory_with_evidence():
    result = detect_martech(HTML)

    inventory = {item["platform"]: item for item in result["media_inventory"]}

    assert inventory["Google"]["status"] == "confirmed"
    assert inventory["Meta"]["status"] == "confirmed"
    assert inventory["TikTok"]["status"] == "confirmed"
    assert inventory["Naver"]["status"] == "confirmed"
    assert inventory["Kakao"]["status"] == "confirmed"
    assert inventory["Pinterest"]["status"] == "confirmed"
    assert inventory["LinkedIn"]["status"] == "confirmed"
    assert inventory["Snapchat"]["status"] == "confirmed"
    assert inventory["Criteo"]["status"] == "confirmed"
    assert inventory["Microsoft Ads"]["status"] == "confirmed"
    assert inventory["당근"]["status"] == "confirmed"
    assert inventory["토스"]["status"] == "confirmed"
    assert all(item["evidence"] for item in inventory.values())
    assert all(item["operating_inference"] == "likely" for item in inventory.values())


def test_media_inventory_does_not_claim_campaign_or_spend_activity():
    result = detect_martech("<html><script src='https://connect.facebook.net/en_US/fbevents.js'></script></html>")

    meta = next(item for item in result["media_inventory"] if item["platform"] == "Meta")

    assert "campaign_status" not in meta
    assert "spend" not in meta
    assert "성과" in meta["note"]
