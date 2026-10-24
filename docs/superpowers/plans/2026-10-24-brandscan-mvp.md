# BrandScan MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development to implement this plan task-by-task. Each task must be verified before moving on.

**Goal:** 공개 웹페이지 URL 하나를 입력하면 근거를 추출하고, MarTech·Technical SEO·GEO 진단과 TOP 3 개선 과제를 보여주는 BrandScan MVP를 9주차 발표 가능한 수준으로 구현한다.

**Architecture:** 단일 프론트엔드와 Python FastAPI 백엔드로 구성한다. 브라우저는 URL 입력·진행 상태·결과 대시보드를 담당하고, 백엔드는 서버에서 공개 HTML을 가져와 정적 SEO/구조화 데이터/스크립트 근거를 추출한다. 초기에는 정적 HTML 분석을 기본으로 하고, 동적 페이지와 네트워크 요청은 Playwright 기반의 제한된 보강 단계로 추가한다.

**Tech Stack:** Python 3, FastAPI, httpx, BeautifulSoup4, Pydantic, pytest, vanilla HTML/CSS/JavaScript. PDF는 브라우저 인쇄 또는 Playwright PDF를 사용하고, LLM 호출은 근거 JSON을 입력으로 받는 별도 adapter로 격리한다.

**Spec:** `mvp-proposal.md`

## Global Constraints

- 분석 대상은 로그인·결제가 필요 없는 공개 단일 웹페이지 URL이다.
- 전체 도메인 대규모 크롤링과 Search Console·GA4 성과 연동은 구현하지 않는다.
- 검색 순위·트래픽·전환·AI 검색 인용 성과를 측정한 것처럼 표현하지 않는다.
- 확인할 수 없는 항목은 실패가 아니라 `unknown`/`미확인`으로 표시한다.
- 모든 진단 과제는 `problem → evidence → recommendation → priority → status`를 가진다.
- 서버 비밀키는 환경 변수로만 읽고 프론트엔드 번들 또는 결과 JSON에 넣지 않는다.

## Review Focus

- SSR/CSR 페이지: 정적 HTML에 없는 항목은 `미확인`으로 표시하고 서버 오류와 혼동하지 않는다.
- URL 안전성: http/https만 허용하고 localhost·사설 IP·리다이렉트 악용을 차단한다.
- 쿠키 동의/동적 태그: 네트워크 요청을 확인하지 못하면 설치로 단정하지 않는다.
- AI 환각: LLM 입력에 근거 목록을 포함하고 근거 없는 권고를 `추가 확인 필요`로 표시한다.
- 긴 HTML/실패 응답: 타임아웃·본문 크기 제한·상태 코드를 사용자에게 설명 가능한 오류로 변환한다.

## Data Contract

`AnalysisResult`는 다음 필드를 가진다.

- `analysis_id: str`
- `url: str`
- `analyzed_at: str`
- `areas: {martech, technical_seo, geo}`
- `issues: list[Issue]`
- `top_priorities: list[str]`
- `source_snapshot: {status_code, final_url, title}`

`Issue`는 다음 필드를 가진다.

- `id: str`
- `area: Literal["martech", "technical_seo", "geo"]`
- `title: str`
- `status: Literal["confirmed", "partial", "suspicious", "unknown"]`
- `problem: str`
- `evidence: list[Evidence]`
- `recommendation: str`
- `priority: Literal["high", "medium", "low"]`
- `score_reason: str`

`Evidence`는 `source`, `field`, `observed_value`, `expected_value`, `note`를 가진다.

## Tasks

### Task 1: 실행 기반과 URL 분석 API

**Files:**
- Create: `backend/app/main.py`
- Create: `backend/app/models.py`
- Create: `backend/app/fetcher.py`
- Create: `backend/tests/test_fetcher.py`
- Create: `backend/requirements.txt`

**Interfaces:**
- `POST /api/analyze` consumes `{ "url": str }` and produces `AnalysisResult`.
- `fetch_public_page(url: str) -> FetchedPage`.

- [ ] URL 형식·scheme·timeout·본문 크기 제한 테스트를 먼저 작성한다.
- [ ] 테스트를 실행해 실패를 확인한다.
- [ ] httpx 기반 fetcher를 구현하고 최종 URL·상태 코드·HTML을 반환한다.
- [ ] localhost와 사설 네트워크 주소를 차단한다.
- [ ] 테스트 fixture와 mock transport로 정상·리다이렉트·timeout·비정상 상태를 검증한다.

### Task 2: Technical SEO 및 구조화 데이터 추출기

**Files:**
- Create: `backend/app/extractors/technical_seo.py`
- Create: `backend/tests/test_technical_seo.py`
- Modify: `backend/app/models.py`

**Interfaces:**
- `extract_technical_seo(html: str, page_url: str) -> TechnicalSeoFacts`.

- [ ] title, description, H1~H3, canonical, robots/noindex, JSON-LD, image alt, 내부 링크 추출 테스트를 작성한다.
- [ ] 정상·누락·중복·잘못된 canonical fixture를 만든다.
- [ ] 값이 없는 항목과 파싱 실패를 구분한다.
- [ ] 추출 결과에 source와 observed value를 보존한다.

### Task 3: MarTech 탐지기

**Files:**
- Create: `backend/app/extractors/martech.py`
- Create: `backend/tests/test_martech.py`

**Interfaces:**
- `detect_martech(html: str) -> MartechFacts`.

- [ ] GA4, GTM, Google Ads, Meta Pixel, TikTok Pixel fixture를 만든다.
- [ ] script 감지와 실제 네트워크 요청 확인을 별도 상태로 표현한다.
- [ ] script가 없거나 동적 로딩일 때 `unknown`을 반환하는 테스트를 작성한다.
- [ ] 탐지된 ID는 일부 마스킹 또는 공개 식별자만 반환하고 비밀값은 저장하지 않는다.

### Task 4: GEO 기준과 규칙 기반 우선순위

**Files:**
- Create: `backend/app/extractors/geo.py`
- Create: `backend/app/prioritizer.py`
- Create: `backend/tests/test_prioritizer.py`

**Interfaces:**
- `extract_geo_facts(html: str) -> GeoFacts`.
- `build_issues(facts: AllFacts) -> list[Issue]`.
- `rank_issues(issues: list[Issue]) -> list[Issue]`.

- [ ] FAQ/Q&A, 설명형 heading, 핵심 정보의 구조화 여부를 근거 기반 규칙으로 정의한다.
- [ ] `impact * urgency * effort`의 점수와 각 점수 이유를 저장한다.
- [ ] 같은 입력에 같은 우선순위가 나오는 결정성 테스트를 작성한다.
- [ ] 검색 순위·트래픽·AI 인용 성과를 주장하는 문구가 생성되지 않는 테스트를 작성한다.

### Task 5: 대시보드 UI와 핵심 흐름

**Files:**
- Create: `frontend/index.html`
- Create: `frontend/app.js`
- Create: `frontend/styles.css`
- Create: `frontend/fixtures/sample-result.json`
- Create: `frontend/tests/dashboard.spec.js`

**Interfaces:**
- `analyzeUrl(url)` calls `POST /api/analyze`.
- `renderResult(result)` renders summary cards, TOP 3, tabs, evidence detail, and status labels.

- [ ] URL 입력·분석 중·성공·실패 상태를 먼저 구현한다.
- [ ] MarTech·Technical SEO·GEO 요약 카드를 구현한다.
- [ ] TOP 3 카드를 클릭하면 해당 evidence와 recommendation을 보여준다.
- [ ] 상태를 색상만으로 전달하지 않고 텍스트 라벨과 아이콘을 병기한다.
- [ ] fixture JSON으로 백엔드 없이 UI를 검증한다.

### Task 6: 근거 기반 AI 개선안 adapter

**Files:**
- Create: `backend/app/recommender.py`
- Create: `backend/tests/test_recommender.py`
- Modify: `backend/app/main.py`

**Interfaces:**
- `recommend_from_issues(issues: list[Issue]) -> list[Recommendation]`.

- [ ] 기본값은 규칙 기반 템플릿으로 동작하게 한다.
- [ ] LLM adapter를 선택적으로 연결하되, 입력에는 evidence와 status를 함께 전달한다.
- [ ] 출력 schema 검증을 추가한다.
- [ ] 근거가 없는 성과 예측과 확정 표현을 필터링한다.
- [ ] LLM 장애 시 규칙 기반 결과로 graceful fallback한다.

### Task 7: PDF와 발표 시연 시나리오

**Files:**
- Create: `backend/app/report.py`
- Create: `frontend/demo.html`
- Create: `docs/demo-script.md`
- Create: `backend/tests/test_report.py`

**Interfaces:**
- `GET /api/analysis/{analysis_id}/report.pdf` returns a PDF containing URL, timestamp, summaries, TOP 3, evidence, and recommendations.

- [ ] 샘플 결과로 PDF 생성 테스트를 작성한다.
- [ ] 핵심 결과가 PDF에 포함되는지 텍스트 또는 페이지 수로 검증한다.
- [ ] 정상 페이지·누락 페이지·의심 페이지를 각각 시연하는 fixture를 만든다.
- [ ] 발표 시나리오를 `URL 입력 → 분석 → 근거 확인 → TOP 3 → PDF`로 고정한다.

### Task 8: 통합 검증과 배포 가능한 실행 명령

**Files:**
- Create: `README.md`
- Create: `.env.example`
- Create: `backend/tests/test_api.py`
- Modify: `backend/app/main.py`

- [ ] FastAPI TestClient로 정상·timeout·unknown·AI fallback API를 검증한다.
- [ ] 브라우저에서 데스크톱과 좁은 화면의 핵심 흐름을 확인한다.
- [ ] 비밀정보 검색, 로컬 참조, 외부 URL 정책을 검사한다.
- [ ] `uvicorn backend.app.main:app --reload`로 로컬 실행한다.
- [ ] README에 설치·실행·fixture 테스트·환경 변수·제한사항을 기록한다.

## Milestones

- 1~2주차: Task 1~2, URL fetch와 SEO 추출 결과 반환
- 3주차: Task 3, MarTech 탐지와 unknown 상태
- 4주차: Task 4, GEO 규칙과 TOP 3 우선순위
- 5~6주차: Task 5, 실제 대시보드 핵심 흐름
- 7주차: Task 6, 근거 기반 개선안
- 8주차: Task 7, PDF와 시연 데이터
- 9주차: Task 8, 통합 검증·발표 리허설

## Definition of Done

- 샘플 URL 3종에서 분석 결과가 생성된다.
- 세 진단 영역과 TOP 3 우선순위가 근거와 함께 표시된다.
- 미확인 항목을 실패로 오판하지 않는다.
- 개선안이 진단 근거와 연결된다.
- PDF 리포트가 다운로드된다.
- 테스트와 로컬 실행 명령이 README에 재현 가능하게 적혀 있다.
