from __future__ import annotations


def _issue(issue_id: str, area: str, title: str, evidence: str, recommendation: str, impact: int, urgency: int, effort: int, status: str = "confirmed") -> dict[str, object]:
    score = impact * urgency * effort
    return {
        "id": issue_id,
        "area": area,
        "title": title,
        "status": status,
        "problem": title,
        "evidence": evidence,
        "recommendation": recommendation,
        "priority": "high" if score >= 8 else "medium" if score >= 4 else "low",
        "score": score,
        "score_reason": f"영향도 {impact} × 시급성 {urgency} × 실행 난이도 {effort} = {score}",
    }


def build_issues(technical: dict[str, object], martech: dict[str, object], geo: dict[str, object]) -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    if not technical.get("title"):
        issues.append(_issue("seo-title", "technical_seo", "페이지 제목이 없습니다", "title 메타요소가 발견되지 않았습니다.", "페이지의 핵심 주제를 담은 title을 추가합니다.", 3, 3, 1))
    if not technical.get("description"):
        issues.append(_issue("seo-description", "technical_seo", "Meta Description이 없습니다", "description 메타요소가 발견되지 않았습니다.", "페이지 가치와 핵심 내용을 설명하는 Meta Description을 추가합니다.", 3, 3, 1))
    images = technical.get("images", {})
    if isinstance(images, dict) and images.get("missing_alt", 0):
        issues.append(_issue("seo-alt", "technical_seo", "이미지 alt가 누락되었습니다", f"이미지 {images['missing_alt']}개에서 alt가 확인되지 않았습니다.", "이미지의 의미를 설명하는 alt 텍스트를 추가합니다.", 2, 2, 1))
    tools = martech.get("tools", {})
    if isinstance(tools, dict) and tools.get("ga4", {}).get("status") == "unknown":
        issues.append(_issue("martech-ga4", "martech", "GA4 설치 여부를 확인할 수 없습니다", "공개 HTML에서 GA4 단서를 찾지 못했습니다.", "쿠키 동의 후 실제 네트워크 요청과 태그 설정을 추가 확인합니다.", 2, 2, 2, status="unknown"))
    if not geo.get("has_question_heading"):
        issues.append(_issue("geo-question", "geo", "질문형 콘텐츠 구조가 부족합니다", "FAQ 또는 질문형 heading을 확인하지 못했습니다.", "사용자 질문을 H2와 FAQ/Q&A 형식으로 구성합니다.", 2, 2, 2))
    if not geo.get("has_explanatory_content"):
        issues.append(_issue("geo-context", "geo", "설명형 콘텐츠가 부족합니다", "페이지 본문에서 충분한 설명형 텍스트를 확인하지 못했습니다.", "고객 문제·선택 기준·사용 방법을 설명하는 본문을 추가합니다.", 2, 2, 2))
    return issues


def rank_issues(issues: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(issues, key=lambda item: int(item["score"]), reverse=True)
