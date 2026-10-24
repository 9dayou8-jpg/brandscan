from backend.app.network_media import classify_runtime_requests


def test_preserves_omnibug_style_tag_ids_and_tag_types():
    urls = [
        "https://www.google-analytics.com/g/collect?v=2&tid=G-QTVTHYLBQS&en=page_view",
        "https://www.google-analytics.com/g/collect?v=2&tid=G-Q142L8EL30&en=misc_payload",
        "https://www.googleadservices.com/pagead/conversion/AW-346256273/?label=abc",
        "https://bat.bing.com/action/0?ti=4024470&Ver=2",
        "https://static.criteo.net/js/ld/ld.js?account=5129",
        "https://www.facebook.com/tr?id=351314038378023&ev=PageView",
    ]

    result = classify_runtime_requests(urls)
    inventory = {item["platform"]: item for item in result["media_inventory"]}

    assert inventory["Google"]["identifiers"] == ["G-QTVTHYLBQS", "G-Q142L8EL30", "AW-346256273"]
    assert inventory["Google"]["tag_types"] == ["Google Analytics", "Google Ads"]
    assert inventory["Microsoft Ads"]["identifiers"] == ["4024470"]
    assert inventory["Criteo"]["identifiers"] == ["5129"]
    assert inventory["Meta"]["identifiers"] == ["351314038378023"]
