from backend.app.extractors.technical_seo import extract_technical_seo


SAMPLE_HTML = """
<html>
<head>
  <title>BrandScan 테스트</title>
  <meta name="description" content="진단용 페이지입니다.">
  <meta name="robots" content="index,follow">
  <link rel="canonical" href="https://example.com/test">
  <script type="application/ld+json">{"@type":"Organization","name":"Example"}</script>
</head>
<body>
  <h1>브랜드 진단</h1><h2>서비스 소개</h2><h3>자주 묻는 질문</h3>
  <img src="hero.jpg" alt="브랜드 소개 이미지">
  <img src="missing-alt.jpg">
  <a href="/about">소개</a><a href="https://other.example/about">외부</a>
</body>
</html>
"""


def test_extracts_core_seo_facts_and_evidence():
    result = extract_technical_seo(SAMPLE_HTML, "https://example.com/test")

    assert result["title"] == "BrandScan 테스트"
    assert result["description"] == "진단용 페이지입니다."
    assert result["headings"] == {"h1": ["브랜드 진단"], "h2": ["서비스 소개"], "h3": ["자주 묻는 질문"]}
    assert result["canonical"] == "https://example.com/test"
    assert result["robots"] == "index,follow"
    assert result["json_ld_types"] == ["Organization"]
    assert result["images"] == {"total": 2, "missing_alt": 1}
    assert result["internal_links"] == 1


def test_missing_fields_are_explicitly_unknown():
    result = extract_technical_seo("<html><body><h1>Only heading</h1></body></html>", "https://example.com")

    assert result["title"] is None
    assert result["description"] is None
    assert result["canonical"] is None
    assert result["robots"] is None
    assert result["json_ld_types"] == []
    assert result["images"] == {"total": 0, "missing_alt": 0}
