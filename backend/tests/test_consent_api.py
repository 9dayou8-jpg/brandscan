from fastapi.testclient import TestClient

from backend.app.fetcher import FetchedPage
from backend.app.main import app


client = TestClient(app)


def test_runtime_consent_state_is_exposed_without_auto_accepting(monkeypatch):
    def fake_fetch(url):
        return FetchedPage(url, url, 200, "text/html", "<html><title>Runtime page</title></html>")

    def fake_runtime(url, wait_ms=5000):
        return {
            "status_code": 200,
            "final_url": url,
            "request_urls": [],
            "capture_method": "playwright_network_request",
            "consent_status": "present_not_interacted",
            "consent_signals": ["#cookie-banner"],
            "consent_note": "자동으로 동의하지 않았습니다.",
        }

    monkeypatch.setattr("backend.app.main.fetch_public_page", fake_fetch)
    monkeypatch.setattr("backend.app.main.capture_runtime_requests", fake_runtime)

    response = client.post("/api/analyze", json={"url": "https://example.com", "capture_runtime": True})

    assert response.status_code == 200
    consent = response.json()["martech"]
    assert consent["consent_status"] == "present_not_interacted"
    assert consent["consent_signals"] == ["#cookie-banner"]
    assert "자동으로 동의하지" in consent["consent_note"]
