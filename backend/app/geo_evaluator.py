from __future__ import annotations


def _criterion(criterion_id: str, result: str, evidence_refs: list[str], reason: str) -> dict[str, object]:
    return {
        "criterion_id": criterion_id,
        "result": result,
        "evidence_refs": evidence_refs,
        "reason": reason,
    }


def evaluate_geo(facts: dict[str, object]) -> dict[str, object]:
    evidence = {item["evidence_id"]: item for item in facts.get("evidence", [])}
    criteria = [
        _criterion(
            "GEO-QUESTION-001",
            "confirmed" if facts["has_question_heading"] else "additional_review",
            ["heading-001"],
            "질문형 heading 확인" if facts["has_question_heading"] else "질문형 heading이 공개 HTML에서 확인되지 않음",
        ),
        _criterion(
            "GEO-CONTEXT-001",
            "confirmed" if facts["has_explanatory_content"] else "additional_review",
            ["text-001"],
            "설명형 본문 확인" if facts["has_explanatory_content"] else "충분한 설명형 본문이 확인되지 않음",
        ),
        _criterion(
            "GEO-FAQ-001",
            "confirmed" if facts["has_faq_schema"] else "additional_review",
            ["jsonld-001"],
            "FAQPage 구조 확인" if facts["has_faq_schema"] else "FAQPage 구조가 공개 HTML에서 확인되지 않음",
        ),
    ]
    confirmed = sum(item["result"] == "confirmed" for item in criteria)
    readiness = "ready" if confirmed == len(criteria) else "partial" if confirmed else "additional_review"
    return {
        "geo_readiness": {"status": readiness, "confirmed_criteria": confirmed, "total_criteria": len(criteria)},
        "ai_search_performance": {"status": "not_measured", "value": None},
        "criteria": criteria,
        "evidence": list(evidence.values()),
    }
