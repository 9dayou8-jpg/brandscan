# BrandScan Data Specification v1.0

## 목적

BrandScan의 기존 단일 URL 진단 결과를 브랜드 시드, SEO/GEO 인텔리전스, 콘텐츠 Gap, 추천 엔진으로 확장하기 위한 공통 데이터 계약이다.

## 공통 규칙

- 모든 분석은 `analysis_scope=single_url`로 시작하며 `site_wide_inference=false`를 기본값으로 둔다.
- 관찰 사실(`evidence_status`), 진단 상태(`diagnosis_status`), 문제 확정(`issue_confirmed`), 확신도(`confidence`), 비즈니스 영향 측정 상태(`business_impact_status`)를 분리한다.
- 모든 객체는 `source`, `confidence`, `collected_at`, `version`을 가능한 경우 저장한다.
- AI 추정 키워드·추천·경쟁사 후보는 `suggested` 또는 `candidate` 상태로 저장하고 자동 확정하지 않는다.
- 실제 검색량·순위·트래픽·AI 인용 성과는 외부 검증 데이터가 없으면 `not_measured`로 저장한다.
- 공개 HTML·브라우저 런타임 요청 외 개인정보와 인증 정보는 수집하지 않는다.

## BrandProfile

```json
{
  "id": "brand-001",
  "name": "BrandScan",
  "website_url": "https://example.com",
  "industry": "unknown",
  "products": [],
  "audience": null,
  "market": null,
  "language": "ko",
  "objective": "acquisition",
  "aliases": [],
  "product_categories": [],
  "field_evidence": {
    "name": [{"evidence_id": "title-001", "source_url": "...", "quote": "..."}]
  },
  "field_confidence": {
    "name": "medium",
    "industry": "low"
  },
  "needs_user_confirmation": ["industry", "products"],
  "source_analysis_id": "analysis-001",
  "version": "1.0.0"
}
```

필수 사용자 입력은 `website_url`, `name`, `industry`, `products`지만 URL 분석에서 자동 초안을 먼저 만들고 사용자가 확인·수정한다.

## KeywordSeed

```json
{
  "id": "keyword-001",
  "brand_id": "brand-001",
  "keyword": "브랜드 웹사이트 진단",
  "keyword_type": "category",
  "search_intent": "informational",
  "topic_cluster": "website_diagnosis",
  "priority": null,
  "source": "page_content",
  "confidence": "medium",
  "measurement_status": "not_measured",
  "version": "1.0.0"
}
```

## PromptSet

```json
{
  "id": "prompt-001",
  "brand_id": "brand-001",
  "keyword_ids": ["keyword-001"],
  "prompt_text": "브랜드 웹사이트 진단 도구를 고를 때 확인할 기준은 무엇인가요?",
  "intent": "informational",
  "funnel_stage": "top",
  "language": "ko",
  "market": "KR",
  "source": "generated",
  "status": "candidate"
}
```

## PageContent

기존 `technical_seo` 결과를 확장한다.

```json
{
  "id": "page-001",
  "brand_id": "brand-001",
  "url": "https://example.com/service",
  "canonical_url": "https://example.com/service",
  "page_type": "service",
  "title": "...",
  "meta_description": "...",
  "headings": {"h1": [], "h2": [], "h3": []},
  "body_text": "...",
  "entities": [],
  "schema_types": [],
  "internal_links": [],
  "external_links": [],
  "author": null,
  "published_at": null,
  "updated_at": null,
  "fetched_at": "...",
  "source_method": ["server_http_fetch", "html_parser"],
  "version": "0.1.0"
}
```

## CompetitorProfile

경쟁사 후보는 반드시 근거와 후보 상태를 가진다.

```json
{
  "id": "competitor-001",
  "brand_id": "brand-001",
  "competitor_name": "Candidate",
  "domain": "https://candidate.example",
  "competitor_type": "search_competitor",
  "products": [],
  "positioning": null,
  "evidence_urls": [],
  "status": "candidate",
  "confidence": "low"
}
```

## AIResponse

```json
{
  "id": "response-001",
  "prompt_id": "prompt-001",
  "model_provider": "not_connected",
  "model_name": null,
  "executed_at": null,
  "raw_response": null,
  "mentioned_brands": [],
  "citation_urls": [],
  "execution_status": "not_measured",
  "error_message": null
}
```

## ContentGap

```json
{
  "id": "gap-001",
  "brand_id": "brand-001",
  "topic": "FAQ 구조",
  "related_keywords": [],
  "related_prompts": [],
  "existing_pages": [],
  "gap_type": "missing_faq",
  "evidence": [],
  "severity": "medium",
  "recommendation": "...",
  "confidence": "medium"
}
```

## Recommendation

```json
{
  "id": "recommendation-001",
  "brand_id": "brand-001",
  "issue_type": "technical_seo",
  "title": "...",
  "description": "...",
  "evidence": [],
  "impact": 2,
  "urgency": 2,
  "ease": 3,
  "priority_score": 17,
  "priority_calculation": {
    "formula_version": "0.3.0",
    "weights": {"impact": 4, "urgency": 3, "ease": 1},
    "score_reason": "..."
  },
  "recommended_actions": [],
  "related_urls": [],
  "confidence": "medium"
}
```

## Phase 1~4 MVP 저장 전략

현재 프로젝트에는 DB가 없으므로 1주 MVP에서는 API 응답과 JSON evidence artifact를 우선 사용한다. 재실행·이력 저장이 필요해지는 시점에 SQLite 또는 기존 배포 환경과 호환되는 저장소를 별도 승인 후 선택한다.
