from backend.app.network_media import classify_runtime_requests


def test_classifies_first_party_and_vendor_runtime_analytics_requests():
    urls = [
        "https://www.nike.com/static/analytics-client/public/analytics-client.min.js",
        "https://analytics.nike.com/v1/t",
        "https://clickstream.halfpipe.nike.com/TrackEvent",
        "https://bam.nr-data.net/1/abc",
        "https://insights-collector.newrelic.com/v1/accounts/123/events",
        "https://c.go-mpulse.net/api/config.json",
    ]

    result = classify_runtime_requests(urls)
    inventory = {item["platform"]: item for item in result["media_inventory"]}

    assert inventory["First-party analytics"]["status"] == "confirmed"
    assert inventory["New Relic"]["status"] == "confirmed"
    assert inventory["Akamai mPulse"]["status"] == "confirmed"
    assert result["request_count"] == 6
