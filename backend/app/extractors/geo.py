from __future__ import annotations

from html.parser import HTMLParser
import json
import re


class _GeoParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.heading_text: list[str] = []
        self.heading_records: list[tuple[str, str]] = []
        self.body_text: list[str] = []
        self.json_ld: list[str] = []
        self._active_heading = False
        self._active_heading_tag: str | None = None
        self._in_json_ld = False
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"h1", "h2", "h3", "h4"}:
            self._active_heading = True
            self._active_heading_tag = tag
            self._buffer = []
        elif tag == "script" and dict(attrs).get("type", "").lower() == "application/ld+json":
            self._in_json_ld = True
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if self._in_json_ld and tag == "script":
            self.json_ld.append("".join(self._buffer))
            self._in_json_ld = False
            self._buffer = []
        elif self._active_heading and tag in {"h1", "h2", "h3", "h4"}:
            text = " ".join("".join(self._buffer).split())
            self.heading_text.append(text)
            self.heading_records.append((self._active_heading_tag or tag, text))
            self._active_heading = False
            self._active_heading_tag = None
            self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._in_json_ld or self._active_heading:
            self._buffer.append(data)
        self.body_text.append(data)


def extract_geo_facts(html: str) -> dict[str, object]:
    parser = _GeoParser()
    parser.feed(html)
    headings = " ".join(parser.heading_text).lower()
    body = " ".join(parser.body_text)
    normalized_body = " ".join(body.split())
    faq_schema = False
    for raw in parser.json_ld:
        try:
            payload = json.loads(raw)
            values = payload if isinstance(payload, list) else [payload]
            faq_schema = faq_schema or any(item.get("@type") == "FAQPage" for item in values if isinstance(item, dict))
        except json.JSONDecodeError:
            continue
    has_question_heading = bool(re.search(r"질문|faq|자주 묻는|how|why|what", headings, re.I))
    has_explanatory_content = len(normalized_body) >= 80
    evidence: list[dict[str, object]] = []
    question_record = next((record for record in parser.heading_records if re.search(r"질문|faq|자주 묻는|how|why|what", record[1], re.I)), None)
    evidence.append({"evidence_id": "heading-001", "source": "heading", "field": question_record[0] if question_record else "heading", "quote": question_record[1] if question_record else "질문형 heading 미검출"})
    evidence.append({"evidence_id": "text-001", "source": "body_text", "field": "content", "quote": normalized_body[:180] if normalized_body else "설명형 본문 미검출"})
    evidence.append({"evidence_id": "jsonld-001", "source": "json_ld", "field": "@type", "quote": "FAQPage" if faq_schema else "FAQPage 미검출"})
    return {
        "has_question_heading": has_question_heading,
        "has_explanatory_content": has_explanatory_content,
        "has_faq_schema": faq_schema,
        "evidence": evidence,
    }
