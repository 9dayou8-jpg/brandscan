# BrandScan MVP

공개 웹페이지 URL 하나로 MarTech·Technical SEO·GEO 상태를 진단하고, 근거 기반 TOP 3 개선 과제를 보여주는 MVP입니다.

## 주요 기능

- URL 기반 공개 HTML 수집
- Technical SEO 추출: title, description, H1~H3, canonical, robots, JSON-LD, 이미지 alt, 내부 링크
- MarTech 단서 탐지: GA4, GTM, Google Ads, Meta Pixel, TikTok Pixel
- GEO 구조 점검: 질문형 heading, 설명형 콘텐츠, FAQ Schema
- 영향도 × 시급성 × 실행 난이도 기반 TOP 3 우선순위
- 문제·발견 근거·개선 방향·판정 상태 상세 표시
- 브라우저 인쇄를 통한 리포트 저장

## 실행 방법

Python 3.11 이상을 권장합니다.

```bash
python3 -m pip install -r requirements.txt
python3 -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8010
```

다른 터미널에서 프론트엔드를 실행합니다.

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

브라우저에서 다음 주소를 엽니다.

```text
http://127.0.0.1:8000/frontend/index.html
```

분석 API만 확인하려면:

```bash
curl -X POST http://127.0.0.1:8010/api/analyze \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com"}'
```

## 테스트

```bash
python3 -m pytest -q
```

현재 테스트는 URL 안전성, HTML 수집, Technical SEO, MarTech, GEO, TOP 3 우선순위, API 응답을 확인합니다.

## 환경 변수

현재 MVP는 외부 AI API 없이 규칙 기반 결과로 동작합니다. AI 개선안을 추가할 때 `.env.example`을 복사해 키를 설정합니다.

```bash
cp .env.example .env
```

## 검증 증거 생성

정상·누락·의심 fixture를 실행하고 결과 JSON과 Markdown 보고서를 생성합니다.

```bash
PYTHONPATH=. python3 scripts/generate_validation_evidence.py
```

생성 파일:

```text
docs/evidence/validation-results.json
docs/evidence/validation-results.md
```

## MVP 제한사항

- 공개 단일 URL만 분석합니다.
- 전체 도메인 크롤링은 지원하지 않습니다.
- 동적 로딩·쿠키 동의 뒤의 태그는 `미확인`일 수 있습니다.
- Search Console·GA4 계정 성과 데이터는 연동하지 않습니다.
- 검색 순위·트래픽·AI 검색 인용 성과를 측정하지 않습니다.
- 분석 결과는 실제 근거와 AI/규칙 기반 제안을 구분해야 합니다.
