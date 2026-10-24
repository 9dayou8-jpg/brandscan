from backend.app.prioritizer import adjust_impact, build_issues, rank_issues


def test_marketing_objective_adjusts_issue_impact():
    assert adjust_impact("seo-description", 2, "brand_awareness") == 2
    assert adjust_impact("seo-description", 2, "acquisition") == 3
    assert adjust_impact("geo-question", 2, "lead_generation") == 3


def test_same_issues_can_rank_differently_by_objective():
    technical = {
        "title": "서비스",
        "description": None,
        "headings": {"h1": ["서비스"], "h2": [], "h3": []},
        "canonical": "https://example.com",
        "robots": None,
        "json_ld_types": [],
        "images": {"total": 0, "missing_alt": 0},
        "internal_links": 0,
    }
    martech = {"tools": {"ga4": {"status": "unknown"}, "gtm": {"status": "unknown"}, "google_ads": {"status": "unknown"}, "meta_pixel": {"status": "unknown"}, "tiktok_pixel": {"status": "unknown"}}}
    geo = {"has_question_heading": False, "has_explanatory_content": True, "has_faq_schema": False}

    awareness = rank_issues(build_issues(technical, martech, geo, marketing_objective="brand_awareness"))
    acquisition = rank_issues(build_issues(technical, martech, geo, marketing_objective="acquisition"))

    assert awareness[0]["priority_calculation"]["marketing_objective"] == "brand_awareness"
    assert acquisition[0]["priority_calculation"]["marketing_objective"] == "acquisition"
    assert awareness[0]["score"] != acquisition[0]["score"] or awareness[0]["id"] != acquisition[0]["id"]
