from fastapi.testclient import TestClient

from backend.app.fetcher import FetchedPage
from backend.app.main import app


client = TestClient(app)


def test_brand_profile_draft_endpoint_returns_editable_candidate(monkeypatch):
    def fake_fetch(url):
        return FetchedPage(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/html; charset=utf-8",
            html="<html><head><title>Acme Analytics | 서비스</title></head><body><h1>Acme Analytics</h1></body></html>",
        )

    monkeypatch.setattr("backend.app.main.fetch_public_page", fake_fetch)

    response = client.post("/api/brand-profile/draft", json={"website_url": "https://example.com"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "Acme Analytics"
    assert payload["industry"] is None
    assert "industry" in payload["needs_user_confirmation"]
    assert payload["field_evidence"]["name"]
