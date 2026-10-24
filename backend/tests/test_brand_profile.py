from backend.app.brand_profile import build_brand_profile_draft


def test_brand_profile_draft_extracts_name_with_evidence():
    result = build_brand_profile_draft(
        website_url="https://example.com",
        technical_facts={
            "title": "Acme Analytics | 브랜드 진단",
            "headings": {"h1": ["Acme Analytics"]},
            "meta_og_site_name": "Acme Analytics",
        },
    )

    assert result["website_url"] == "https://example.com"
    assert result["name"] == "Acme Analytics"
    assert result["field_confidence"]["name"] == "high"
    assert result["field_evidence"]["name"][0]["source"] == "og:site_name"
    assert "industry" in result["needs_user_confirmation"]
    assert "products" in result["needs_user_confirmation"]


def test_brand_profile_does_not_invent_industry_or_products():
    result = build_brand_profile_draft(
        website_url="https://example.com",
        technical_facts={"title": "우리 서비스", "headings": {"h1": ["서비스 소개"]}},
    )

    assert result["industry"] is None
    assert result["products"] == []
    assert result["field_confidence"]["industry"] == "low"
    assert result["field_confidence"]["products"] == "low"
