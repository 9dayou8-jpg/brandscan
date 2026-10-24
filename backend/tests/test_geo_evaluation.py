from backend.app.extractors.geo import extract_geo_facts
from backend.app.geo_evaluator import evaluate_geo


HTML = """
<html><body>
<h1>BrandScan 브랜드 진단</h1>
<h2>자주 묻는 질문</h2>
<p>BrandScan은 브랜드 웹사이트의 SEO와 마케팅 측정 구조를 진단하고 개선 방향을 제안하는 서비스입니다. 사용자는 공개 URL을 입력해 문제와 우선순위를 확인할 수 있습니다.</p>
<script type="application/ld+json">{"@type":"FAQPage","mainEntity":[]}</script>
</body></html>
"""


def test_geo_evaluation_links_each_criterion_to_page_evidence():
    facts = extract_geo_facts(HTML)
    result = evaluate_geo(facts)

    assert result["geo_readiness"]["status"] in {"ready", "partial"}
    assert result["ai_search_performance"] == {"status": "not_measured", "value": None}
    assert len(result["criteria"]) >= 3
    assert all(item["criterion_id"] and item["evidence_refs"] for item in result["criteria"])


def test_same_page_produces_identical_geo_evaluation():
    first = evaluate_geo(extract_geo_facts(HTML))
    second = evaluate_geo(extract_geo_facts(HTML))

    assert first == second
