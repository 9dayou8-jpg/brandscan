from fastapi.testclient import TestClient

from backend.app.fetcher import FetchedPage
from backend.app.main import app


client = TestClient(app)


def test_analyze_returns_page_snapshot(monkeypatch):
    def fake_fetch(url):
        return FetchedPage(
            requested_url=url,
            final_url="https://example.com/final",
            status_code=200,
            content_type="text/html; charset=utf-8",
            html="<html><title>Example</title></html>",
        )

    monkeypatch.setattr("backend.app.main.fetch_public_page", fake_fetch)

    response = client.post("/api/analyze", json={"url": "https://example.com"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["url"] == "https://example.com"
    assert payload["technical_seo"]["title"] == "Example"
    assert "martech" in payload
    assert "geo" in payload
    assert "issues" in payload
    assert "confirmed_issues" in payload
    assert "additional_review_items" in payload
    assert len(payload["top_priorities"]) == len(payload["confirmed_issues"])
    assert all(item["issue_confirmed"] for item in payload["top_priorities"])
    assert all(item["evidence"] and item["recommendation"] for item in payload["issues"])


def test_analyze_rejects_missing_url():
    response = client.post("/api/analyze", json={})

    assert response.status_code == 422
