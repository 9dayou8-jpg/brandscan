from fastapi.testclient import TestClient

from backend.app.fetcher import FetchedPage
from backend.app.main import app


client = TestClient(app)


def test_analyze_accepts_marketing_objective_and_page_type_override(monkeypatch):
    def fake_fetch(url):
        return FetchedPage(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/html; charset=utf-8",
            html="<html><head><title>Service</title></head><body><h1>Service</h1></body></html>",
        )

    monkeypatch.setattr("backend.app.main.fetch_public_page", fake_fetch)

    response = client.post(
        "/api/analyze",
        json={
            "url": "https://example.com/services/brand-a",
            "marketing_objective": "lead_generation",
            "page_type": "landing",
        },
    )

    assert response.status_code == 200
    metadata = response.json()["analysis_metadata"]
    assert metadata["analysis_scope"] == "single_url"
    assert metadata["marketing_objective"] == "lead_generation"
    assert metadata["page_type"]["predicted"] == "service"
    assert metadata["page_type"]["selected"] == "landing"
    assert metadata["page_type"]["source"] == "user"
