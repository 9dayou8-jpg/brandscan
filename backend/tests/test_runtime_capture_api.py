from fastapi.testclient import TestClient

from backend.app.fetcher import FetchedPage
from backend.app.main import app


client = TestClient(app)


def test_runtime_capture_enriches_media_inventory(monkeypatch):
    def fake_fetch(url):
        return FetchedPage(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/html; charset=utf-8",
            html="<html><title>Runtime page</title></html>",
        )

    def fake_runtime(url, wait_ms=5000):
        return {
            "status_code": 200,
            "final_url": url,
            "request_urls": [
                "https://analytics.twitter.com/1/i/adsctp?events=%5B%5B%22page_view%22%5D%5D",
                "https://www.facebook.com/tr/?ev=PageView",
            ],
            "capture_method": "playwright_network_request",
        }

    monkeypatch.setattr("backend.app.main.fetch_public_page", fake_fetch)
    monkeypatch.setattr("backend.app.main.capture_runtime_requests", fake_runtime)

    response = client.post("/api/analyze", json={"url": "https://example.com", "capture_runtime": True})

    assert response.status_code == 200
    payload = response.json()
    assert payload["martech"]["runtime_capture"]["capture_method"] == "playwright_network_request"
    platforms = {item["platform"] for item in payload["martech"]["media_inventory"]}
    assert "X (Twitter)" in platforms
    assert "Meta" in platforms
