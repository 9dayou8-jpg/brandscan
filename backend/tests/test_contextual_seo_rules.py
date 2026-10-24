from backend.app.prioritizer import build_issues


def test_suspicious_canonical_and_duplicate_h1_are_not_confirmed_errors():
    technical = {
        "title": "서비스",
        "description": "설명",
        "headings": {"h1": ["브랜드 진단", "서비스 안내"], "h2": [], "h3": []},
        "canonical": "https://other.example/canonical",
        "canonical_host_matches": False,
        "robots": None,
        "json_ld_types": [],
        "images": {"total": 0, "missing_alt": 0},
        "internal_links": 0,
    }
    issues = build_issues(
        technical,
        {"tools": {}},
        {"has_question_heading": True, "has_explanatory_content": True, "has_faq_schema": True},
    )

    canonical = next(issue for issue in issues if issue["id"] == "seo-canonical-suspicious")
    h1 = next(issue for issue in issues if issue["id"] == "seo-h1-structure")

    assert canonical["diagnosis_status"] == "error_suspected"
    assert canonical["issue_confirmed"] is False
    assert h1["diagnosis_status"] == "error_suspected"
    assert h1["issue_confirmed"] is False
