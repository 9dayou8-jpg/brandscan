from backend.app.diagnosis import classify_finding


PRIORITY_FORMULA_VERSION = "0.3.0"
PRIORITY_WEIGHTS = {"impact": 4, "urgency": 3, "ease": 1}
OBJECTIVE_IMPACT_ADJUSTMENTS = {
    "seo-description": {"brand_awareness": 0, "acquisition": 1, "conversion": 0, "lead_generation": 0},
    "martech-ga4": {"brand_awareness": 0, "acquisition": 0, "conversion": 1, "lead_generation": 1},
    "geo-question": {"brand_awareness": 0, "acquisition": 1, "conversion": 0, "lead_generation": 1},
}
ISSUE_GROUPS = {
    "seo-title": ("content-context-001", "content-messaging-001"),
    "seo-description": ("content-context-001", "content-messaging-001"),
    "seo-alt": ("accessibility-001", "image-content-001"),
    "martech-ga4": ("martech-measurement-001", "martech-validation-001"),
    "geo-question": ("geo-structure-001", "geo-content-001"),
    "geo-context": ("geo-structure-001", "geo-content-001"),
}


def adjust_impact(issue_id: str, base_impact: int, marketing_objective: str) -> int:
    adjustment = OBJECTIVE_IMPACT_ADJUSTMENTS.get(issue_id, {}).get(marketing_objective, 0)
    return max(1, min(3, base_impact + adjustment))


def calculate_priority(*, impact: int, urgency: int, ease: int, marketing_objective: str) -> dict[str, object]:
    factors = {"impact": impact, "urgency": urgency, "ease": ease}
    if any(not isinstance(value, int) or value < 1 or value > 3 for value in factors.values()):
        raise ValueError("impact, urgency, ease는 1~3점이어야 합니다.")
    score = sum(factors[key] * PRIORITY_WEIGHTS[key] for key in factors)
    return {
        "formula": "(impact × 4) + (urgency × 3) + (ease × 1)",
        "formula_version": PRIORITY_FORMULA_VERSION,
        "weights": dict(PRIORITY_WEIGHTS),
        "factors": factors,
        "marketing_objective": marketing_objective,
        "score": score,
    }


def _issue(issue_id: str, area: str, title: str, evidence: str, recommendation: str, impact: int, urgency: int, ease: int, status: str = "confirmed", marketing_objective: str = "acquisition") -> dict[str, object]:
    state_map = {
        "confirmed": ("confirmed", "recommendation", True, "high"),
        "unknown": ("unverified", "additional_review", False, "low"),
        "partial": ("partial", "additional_review", False, "medium"),
        "suspicious": ("confirmed", "error_suspected", False, "medium"),
    }
    evidence_status, diagnosis_status, issue_confirmed, confidence = state_map[status]
    classification = classify_finding(
        evidence_status=evidence_status,
        diagnosis_status=diagnosis_status,
        issue_confirmed=issue_confirmed,
        confidence=confidence,
    )
    adjusted_impact = adjust_impact(issue_id, impact, marketing_objective)
    priority = calculate_priority(impact=adjusted_impact, urgency=urgency, ease=ease, marketing_objective=marketing_objective)
    score = int(priority["score"])
    return {
        "id": issue_id,
        "root_cause_id": ISSUE_GROUPS.get(issue_id, (issue_id, issue_id))[0],
        "resolution_group_id": ISSUE_GROUPS.get(issue_id, (issue_id, issue_id))[1],
        "area": area,
        "title": title,
        "status": status,
        "evidence_status": classification["evidence_status"],
        "diagnosis_status": classification["diagnosis_status"],
        "issue_confirmed": classification["issue_confirmed"],
        "confidence": classification["confidence"],
        "business_impact_status": classification["business_impact_status"],
        "problem": title,
        "evidence": evidence,
        "recommendation": recommendation,
        "impact": adjusted_impact,
        "priority": "high" if score >= 18 else "medium" if score >= 12 else "low",
        "score": score,
        "priority_calculation": priority,
        "score_reason": f"영향도 {impact} × 4 + 시급성 {urgency} × 3 + 개선 용이성 {ease} × 1 = {score}",
    }


def build_issues(technical: dict[str, object], martech: dict[str, object], geo: dict[str, object], marketing_objective: str = "acquisition") -> list[dict[str, object]]:
    issues: list[dict[str, object]] = []
    if not technical.get("title"):
        issues.append(_issue("seo-title", "technical_seo", "페이지 제목이 없습니다", "title 메타요소가 발견되지 않았습니다.", "페이지의 핵심 주제를 담은 title을 추가합니다.", 3, 3, 1, marketing_objective=marketing_objective))
    if not technical.get("description"):
        issues.append(_issue("seo-description", "technical_seo", "Meta Description이 없습니다", "description 메타요소가 발견되지 않았습니다.", "페이지 가치와 핵심 내용을 설명하는 Meta Description을 추가합니다.", 2, 3, 1, marketing_objective=marketing_objective))
    images = technical.get("images", {})
    if isinstance(images, dict) and images.get("missing_alt", 0):
        issues.append(_issue("seo-alt", "technical_seo", "이미지 alt가 누락되었습니다", f"이미지 {images['missing_alt']}개에서 alt가 확인되지 않았습니다.", "이미지의 의미를 설명하는 alt 텍스트를 추가합니다.", 2, 2, 1, marketing_objective=marketing_objective))
    tools = martech.get("tools", {})
    if isinstance(tools, dict) and tools.get("ga4", {}).get("status") == "unknown":
        issues.append(_issue("martech-ga4", "martech", "GA4 설치 여부를 확인할 수 없습니다", "공개 HTML에서 GA4 단서를 찾지 못했습니다.", "쿠키 동의 후 실제 네트워크 요청과 태그 설정을 추가 확인합니다.", 2, 2, 2, status="unknown", marketing_objective=marketing_objective))
    if not geo.get("has_question_heading"):
        issues.append(_issue("geo-question", "geo", "질문형 콘텐츠 구조가 부족합니다", "FAQ 또는 질문형 heading을 확인하지 못했습니다.", "사용자 질문을 H2와 FAQ/Q&A 형식으로 구성합니다.", 2, 2, 2, status="unknown", marketing_objective=marketing_objective))
    if not geo.get("has_explanatory_content"):
        issues.append(_issue("geo-context", "geo", "설명형 콘텐츠가 부족합니다", "페이지 본문에서 충분한 설명형 텍스트를 확인하지 못했습니다.", "고객 문제·선택 기준·사용 방법을 설명하는 본문을 추가합니다.", 2, 2, 2, status="unknown", marketing_objective=marketing_objective))
    return issues


def deduplicate_issues(issues: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = {}
    for issue in issues:
        group_key = str(issue.get("resolution_group_id") or issue["id"])
        groups.setdefault(group_key, []).append(issue)
    representatives: list[dict[str, object]] = []
    for members in groups.values():
        ordered = sorted(members, key=lambda item: int(item.get("score", 0)), reverse=True)
        representative = dict(ordered[0])
        related_ids = [str(item["id"]) for item in ordered[1:]]
        representative["related_issue_ids"] = related_ids
        representative["deduplicated_count"] = len(ordered)
        representatives.append(representative)
    return sorted(representatives, key=lambda item: int(item.get("score", 0)), reverse=True)


def rank_issues(issues: list[dict[str, object]]) -> list[dict[str, object]]:
    return sorted(issues, key=lambda item: int(item["score"]), reverse=True)
