from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_fetch_error_returns_user_readable_bad_request(monkeypatch):
    def fail_fetch(url):
        raise ValueError("페이지를 가져오지 못했습니다: 404 Not Found")

    monkeypatch.setattr("backend.app.main.fetch_public_page", fail_fetch)

    response = client.post("/api/analyze", json={"url": "https://example.com/missing"})

    assert response.status_code == 400
    assert "404 Not Found" in response.json()["detail"]
