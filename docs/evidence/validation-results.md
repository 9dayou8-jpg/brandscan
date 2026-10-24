# BrandScan 검증 결과

- 생성 시각(UTC): 2026-10-24T09:21:35.697287+00:00
- 분석 범위: 공개 단일 URL fixture
- 마케팅 목적: 신규 고객 유입(acquisition)
- 규칙 버전: 0.3.0

## 정상 페이지 (normal-page.html)

- Title: BrandScan 정상 페이지
- Description: 확인
- H1 개수: 1
- 이미지 alt 누락: 0개
- Canonical: https://fixture.example/normal
- 탐지 매체: Google
- 확정 개선 과제: 0개
- 추가 검증 항목: 0개
- GEO 준비도: ready
- AI 검색 성과: 미측정

판정 근거:

## 누락 페이지 (missing-page.html)

- Title: BrandScan 누락 페이지
- Description: 미확인
- H1 개수: 1
- 이미지 alt 누락: 1개
- Canonical: https://fixture.example/missing
- 탐지 매체: 없음
- 확정 개선 과제: 2개
- 추가 검증 항목: 2개
- GEO 준비도: additional_review
- AI 검색 성과: 미측정

판정 근거:
- Meta Description이 없습니다: description 메타요소가 발견되지 않았습니다.
- 이미지 alt가 누락되었습니다: 이미지 1개에서 alt가 확인되지 않았습니다.
- 추가 검증: 질문형 콘텐츠 구조가 부족합니다 — FAQ 또는 질문형 heading을 확인하지 못했습니다.
- 추가 검증: GA4 설치 여부를 확인할 수 없습니다 — 공개 HTML에서 GA4 단서를 찾지 못했습니다.

## 의심 페이지 (suspicious-page.html)

- Title: BrandScan 의심 페이지
- Description: 미확인
- H1 개수: 2
- 이미지 alt 누락: 0개
- Canonical: https://other.example/canonical
- 탐지 매체: 없음
- 확정 개선 과제: 1개
- 추가 검증 항목: 4개
- GEO 준비도: partial
- AI 검색 성과: 미측정

판정 근거:
- Meta Description이 없습니다: description 메타요소가 발견되지 않았습니다.
- 추가 검증: 질문형 콘텐츠 구조가 부족합니다 — FAQ 또는 질문형 heading을 확인하지 못했습니다.
- 추가 검증: Canonical 대상이 다른 호스트를 가리킵니다 — 관찰된 canonical: https://other.example/canonical
- 추가 검증: H1 구조를 추가 확인해야 합니다 — H1 2개가 확인되었습니다.
- 추가 검증: GA4 설치 여부를 확인할 수 없습니다 — 공개 HTML에서 GA4 단서를 찾지 못했습니다.
