from __future__ import annotations

from urllib.parse import urlparse

from backend.app.analysis_context import PAGE_TYPES


def infer_page_type(url: str, *, title: str | None = None, headings: dict[str, list[str]] | None = None) -> str:
    path = urlparse(url).path.lower().strip("/")
    segments = set(path.split("/")) if path else set()
    if not path:
        return "homepage"
    if segments & {"services", "service", "solutions"}:
        return "service"
    if segments & {"products", "product", "shop", "store"}:
        return "product"
    if segments & {"blog", "posts", "news"}:
        return "blog"
    if segments & {"article", "articles", "guide"}:
        return "article"
    if segments & {"landing", "campaign", "event"}:
        return "landing" if "landing" in segments else "campaign"
    context = " ".join([title or ""] + (headings or {}).get("h1", [])).lower()
    if any(word in context for word in ("서비스", "service", "솔루션", "solution")):
        return "service"
    return "unknown"
