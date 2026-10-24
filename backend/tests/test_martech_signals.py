from backend.app.extractors.martech import detect_martech


def test_detects_first_party_and_vendor_runtime_script_signals():
    html = """
    <script src="/static/analytics-client/public/analytics-client.min.js"></script>
    <script src="https://js-agent.newrelic.com/nr-loader.js"></script>
    <script src="https://c.go-mpulse.net/api/config.json"></script>
    """

    result = detect_martech(html)

    assert result["tools"]["first_party_analytics"]["status"] == "confirmed"
    assert result["tools"]["new_relic"]["status"] == "confirmed"
    assert result["tools"]["akamai_mpulse"]["status"] == "confirmed"
    platforms = {item["platform"] for item in result["media_inventory"]}
    assert {"First-party analytics", "New Relic", "Akamai mPulse"} <= platforms
