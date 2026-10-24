from pathlib import Path

from backend.app.extractors.geo import extract_geo_facts
from backend.app.extractors.martech import detect_martech
from backend.app.extractors.technical_seo import extract_technical_seo

FIXTURES = Path(__file__).parents[2] / "fixtures"


def read_fixture(name):
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_normal_fixture_has_expected_signals():
    html = read_fixture("normal-page.html")
    seo = extract_technical_seo(html, "https://fixture.example/normal")
    martech = detect_martech(html)
    geo = extract_geo_facts(html)

    assert seo["title"] == "BrandScan 정상 페이지"
    assert seo["description"]
    assert seo["canonical"] == "https://fixture.example/normal"
    assert martech["tools"]["ga4"]["status"] == "confirmed"
    assert geo["has_question_heading"] is True


def test_missing_fixture_exposes_missing_evidence_without_claiming_site_failure():
    html = read_fixture("missing-page.html")
    seo = extract_technical_seo(html, "https://fixture.example/missing")
    geo = extract_geo_facts(html)

    assert seo["description"] is None
    assert seo["images"]["missing_alt"] == 1
    assert geo["has_faq_schema"] is False


def test_suspicious_fixture_exposes_conflicting_signals():
    html = read_fixture("suspicious-page.html")
    seo = extract_technical_seo(html, "https://fixture.example/suspicious")

    assert seo["canonical"] == "https://other.example/canonical"
    assert len(seo["headings"]["h1"]) == 2
    assert seo["json_ld_types"] == ["Product"]
