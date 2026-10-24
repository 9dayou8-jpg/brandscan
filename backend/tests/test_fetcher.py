import pytest

from backend.app.fetcher import FetchedPage, fetch_public_page, validate_public_url


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://192.168.1.10",
        "not-a-url",
    ],
)
def test_validate_public_url_rejects_unsafe_or_invalid_urls(url):
    with pytest.raises(ValueError):
        validate_public_url(url)


def test_validate_public_url_accepts_public_http_url():
    assert validate_public_url("https://example.com") == "https://example.com"


def test_fetch_public_page_returns_html_metadata():
    class FakeResponse:
        status_code = 200
        url = "https://example.com/final"
        headers = {"content-type": "text/html; charset=utf-8"}
        content = b"<html><title>Example</title><body>Hello</body></html>"

        def raise_for_status(self):
            return None

    class FakeClient:
        def get(self, url, follow_redirects, timeout, headers):
            assert url == "https://example.com"
            assert follow_redirects is True
            return FakeResponse()

    result = fetch_public_page("https://example.com", client=FakeClient())

    assert isinstance(result, FetchedPage)
    assert result.final_url == "https://example.com/final"
    assert result.status_code == 200
    assert result.html.startswith("<html>")
