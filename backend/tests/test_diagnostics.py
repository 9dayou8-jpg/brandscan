from backend.app.extractors.martech import detect_martech
from backend.app.extractors.geo import extract_geo_facts
from backend.app.prioritizer import build_issues, rank_issues


HTML = """
<html><head>
<script src="https://www.googletagmanager.com/gtag/js?id=G-ABC"></script>
<script>window.dataLayer = window.dataLayer || []; fbq('init', 'META123')</script>
</head><body>
<h1>브랜드 진단</h1><h2>자주 묻는 질문</h2>
<p>우리 서비스는 브랜드 웹사이트 진단을 돕습니다.</p>
</body></html>
"""


def test_detect_martech_marks_known_tools():
    result = detect_martech(HTML)

    assert result["tools"]["ga4"]["status"] == "confirmed"
    assert result["tools"]["meta_pixel"]["status"] == "confirmed"
    assert result["tools"]["gtm"]["status"] == "unknown"


def test_extract_geo_facts_finds_question_content():
    result = extract_geo_facts(HTML)

    assert result["has_question_heading"] is True
    assert result["has_explanatory_content"] is True


def test_rank_issues_returns_top_three_with_reasons():
    technical = {"title": None, "description": None, "headings": {"h1": [], "h2": [], "h3": []}, "canonical": None, "robots": None, "json_ld_types": [], "images": {"total": 0, "missing_alt": 0}, "internal_links": 0}
    martech = {"tools": {"ga4": {"status": "unknown"}, "gtm": {"status": "unknown"}, "google_ads": {"status": "unknown"}, "meta_pixel": {"status": "unknown"}, "tiktok_pixel": {"status": "unknown"}}}
    geo = {"has_question_heading": False, "has_explanatory_content": False, "has_faq_schema": False}

    issues = rank_issues(build_issues(technical, martech, geo))

    assert len(issues) >= 3
    assert len(issues[:3]) == 3
    assert all(issue["evidence"] and issue["score_reason"] for issue in issues[:3])
    assert next(issue for issue in issues if issue["id"] == "martech-ga4")["status"] == "unknown"
