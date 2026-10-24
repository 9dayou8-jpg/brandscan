from backend.app.network_media import classify_runtime_requests


def test_classifies_runtime_requests_by_platform_and_event():
    urls = [
        "https://analytics.twitter.com/i/adsct?events=%5B%5B%22auto_long_site_dwell%22%5D%5D",
        "https://t.co/i/adsct?event_id=abc&integration=advertiser&p_id=Twitter",
        "https://www.google-analytics.com/g/collect?v=2&tid=G-ABC&en=page_view",
        "https://www.facebook.com/tr/?id=123&ev=PageView",
    ]

    result = classify_runtime_requests(urls)
    inventory = {item["platform"]: item for item in result["media_inventory"]}

    assert inventory["X (Twitter)"]["status"] == "confirmed"
    assert inventory["X (Twitter)"]["events"] == ["auto_long_site_dwell"]
    assert inventory["Google"]["events"] == ["page_view"]
    assert inventory["Meta"]["events"] == ["PageView"]
    assert result["request_count"] == 4


def test_unknown_runtime_requests_are_preserved_as_unclassified_evidence():
    result = classify_runtime_requests(["https://tracker.example/collect?event=custom_event"])

    assert result["media_inventory"] == []
    assert result["unclassified_requests"] == ["https://tracker.example/collect?event=custom_event"]
