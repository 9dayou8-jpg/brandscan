from __future__ import annotations

import re
from urllib.parse import urlparse


def _clean_name(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = re.split(r"\s*[|·—-]\s*", value.strip(), maxsplit=1)[0].strip()
    return cleaned or None


def build_brand_profile_draft(*, website_url: str, technical_facts: dict[str, object]) -> dict[str, object]:
    evidence: list[dict[str, object]] = []
    og_name = technical_facts.get("meta_og_site_name")
    h1_values = technical_facts.get("headings", {}).get("h1", [])
    title = technical_facts.get("title")
    name = _clean_name(og_name if isinstance(og_name, str) else None)
    if name:
        evidence.append({"source": "og:site_name", "source_url": website_url, "quote": name})
        name_confidence = "high"
    elif h1_values:
        name = _clean_name(h1_values[0])
        evidence.append({"source": "h1", "source_url": website_url, "quote": h1_values[0]})
        name_confidence = "medium"
    else:
        name = _clean_name(title if isinstance(title, str) else None)
        if name:
            evidence.append({"source": "title", "source_url": website_url, "quote": title})
        name_confidence = "medium" if name else "low"

    return {
        "id": None,
        "name": name,
        "website_url": website_url,
        "industry": None,
        "products": [],
        "audience": None,
        "market": None,
        "language": "ko",
        "objective": "acquisition",
        "aliases": [],
        "product_categories": [],
        "field_evidence": {"name": evidence},
        "field_confidence": {"name": name_confidence, "industry": "low", "products": "low"},
        "needs_user_confirmation": ["industry", "products"],
        "source_analysis_id": None,
        "source_host": urlparse(website_url).netloc,
        "version": "1.0.0",
    }
