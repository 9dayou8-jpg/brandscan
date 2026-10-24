from backend.app.prioritizer import build_issues, deduplicate_issues


def test_unverified_findings_are_separated_from_confirmed_issues():
    technical = {
        "title": "서비스",
        "description": "설명",
        "headings": {"h1": ["서비스"], "h2": [], "h3": []},
        "canonical": "https://example.com",
        "robots": None,
        "json_ld_types": [],
        "images": {"total": 0, "missing_alt": 0},
        "internal_links": 0,
    }
    martech = {"tools": {"ga4": {"status": "unknown"}, "gtm": {"status": "unknown"}, "google_ads": {"status": "unknown"}, "meta_pixel": {"status": "unknown"}, "tiktok_pixel": {"status": "unknown"}}}
    geo = {"has_question_heading": False, "has_explanatory_content": True, "has_faq_schema": False}

    issues = deduplicate_issues(build_issues(technical, martech, geo))
    ga4 = next(issue for issue in issues if issue["id"] == "martech-ga4")
    geo_issue = next(issue for issue in issues if issue["id"] == "geo-question")

    assert ga4["evidence_status"] == "unverified"
    assert ga4["diagnosis_status"] == "additional_review"
    assert ga4["issue_confirmed"] is False
    assert ga4["confidence"] == "low"
    assert ga4["business_impact_status"] == "not_measured"
    assert geo_issue["issue_confirmed"] is False
