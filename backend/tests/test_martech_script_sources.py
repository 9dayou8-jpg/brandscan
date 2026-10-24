from backend.app.extractors.martech import detect_martech


def test_detects_script_source_urls_separately_from_vendor_signals():
    html = """
    <script src="/static/analytics-client/public/analytics-client.min.js"></script>
    <script src="https://js-agent.newrelic.com/nr-loader.js"></script>
    <script>window.unrelated = true</script>
    """

    result = detect_martech(html)

    assert result["script_sources"] == [
        "/static/analytics-client/public/analytics-client.min.js",
        "https://js-agent.newrelic.com/nr-loader.js",
    ]
