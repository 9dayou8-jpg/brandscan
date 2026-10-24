from __future__ import annotations

from dataclasses import dataclass
import ipaddress
from urllib.parse import urlparse

import httpx


DEFAULT_TIMEOUT_SECONDS = 15.0
DEFAULT_MAX_BYTES = 2_000_000


@dataclass(frozen=True)
class FetchedPage:
    requested_url: str
    final_url: str
    status_code: int
    content_type: str
    html: str


def validate_public_url(url: str) -> str:
    """Validate the MVP's public HTTP(S) URL boundary."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL이 필요합니다.")

    candidate = url.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("http 또는 https URL만 분석할 수 있습니다.")

    hostname = parsed.hostname.rstrip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"} or hostname.endswith(".localhost"):
        raise ValueError("로컬 주소는 분석할 수 없습니다.")

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None

    if address is not None and (address.is_private or address.is_loopback or address.is_link_local or address.is_reserved):
        raise ValueError("사설 네트워크 주소는 분석할 수 없습니다.")

    return candidate


def fetch_public_page(
    url: str,
    *,
    client: httpx.Client | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> FetchedPage:
    requested_url = validate_public_url(url)
    own_client = client is None
    http_client = client or httpx.Client()
    try:
        response = http_client.get(
            requested_url,
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": "BrandScan/0.1 (+public-page-analysis)"},
        )
        response.raise_for_status()
        content = response.content
        if len(content) > max_bytes:
            raise ValueError("분석 가능한 페이지 크기(2MB)를 초과했습니다.")
        encoding = getattr(response, "encoding", None) or "utf-8"
        return FetchedPage(
            requested_url=requested_url,
            final_url=str(response.url),
            status_code=response.status_code,
            content_type=response.headers.get("content-type", ""),
            html=content.decode(encoding, errors="replace"),
        )
    except httpx.TimeoutException as exc:
        raise ValueError("페이지 응답 시간이 초과되었습니다.") from exc
    except httpx.HTTPError as exc:
        raise ValueError(f"페이지를 가져오지 못했습니다: {exc}") from exc
    finally:
        if own_client:
            http_client.close()
