from __future__ import annotations

from html.parser import HTMLParser
import json
from urllib.parse import urljoin, urlparse


class _SeoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: str | None = None
        self.description: str | None = None
        self.robots: str | None = None
        self.canonical: str | None = None
        self.headings = {"h1": [], "h2": [], "h3": []}
        self.images_total = 0
        self.images_missing_alt = 0
        self.internal_links: list[str] = []
        self.json_ld_types: list[str] = []
        self._active_text_tag: str | None = None
        self._text_buffer: list[str] = []
        self._json_ld_buffer: list[str] = []
        self._in_json_ld = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "title" or tag in self.headings:
            self._active_text_tag = tag
            self._text_buffer = []
        elif tag == "meta":
            name = (values.get("name") or "").lower()
            if name == "description":
                self.description = values.get("content")
            elif name == "robots":
                self.robots = values.get("content")
        elif tag == "link" and (values.get("rel") or "").lower() == "canonical":
            self.canonical = values.get("href")
        elif tag == "img":
            self.images_total += 1
            if not (values.get("alt") or "").strip():
                self.images_missing_alt += 1
        elif tag == "script" and (values.get("type") or "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._json_ld_buffer = []
        elif tag == "a" and values.get("href"):
            self.internal_links.append(values["href"])

    def handle_endtag(self, tag: str) -> None:
        if self._in_json_ld and tag == "script":
            self._in_json_ld = False
            try:
                payload = json.loads("".join(self._json_ld_buffer))
                items = payload if isinstance(payload, list) else [payload]
                for item in items:
                    if isinstance(item, dict) and isinstance(item.get("@type"), str):
                        self.json_ld_types.append(item["@type"])
            except (json.JSONDecodeError, TypeError):
                pass
            self._json_ld_buffer = []
        if self._active_text_tag == tag:
            text = " ".join("".join(self._text_buffer).split())
            if tag == "title":
                self.title = text or None
            elif tag in self.headings and text:
                self.headings[tag].append(text)
            self._active_text_tag = None
            self._text_buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld:
            self._json_ld_buffer.append(data)
        elif self._active_text_tag:
            self._text_buffer.append(data)


def extract_technical_seo(html: str, page_url: str) -> dict[str, object]:
    parser = _SeoParser()
    parser.feed(html)
    base_host = urlparse(page_url).netloc
    internal_links = 0
    for href in parser.internal_links:
        target = urlparse(urljoin(page_url, href))
        if target.scheme in {"http", "https"} and target.netloc == base_host:
            internal_links += 1
    return {
        "title": parser.title,
        "description": parser.description,
        "headings": parser.headings,
        "canonical": parser.canonical,
        "robots": parser.robots,
        "json_ld_types": sorted(set(parser.json_ld_types)),
        "images": {"total": parser.images_total, "missing_alt": parser.images_missing_alt},
        "internal_links": internal_links,
    }
