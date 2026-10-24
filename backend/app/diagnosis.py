from __future__ import annotations

EVIDENCE_STATUSES = {"confirmed", "partial", "unverified"}
DIAGNOSIS_STATUSES = {"normal", "recommendation", "error_suspected", "additional_review"}
CONFIDENCE_LEVELS = {"high", "medium", "low"}


def classify_finding(*, evidence_status: str, diagnosis_status: str, issue_confirmed: bool, confidence: str) -> dict[str, object]:
    if evidence_status not in EVIDENCE_STATUSES:
        raise ValueError(f"알 수 없는 evidence_status: {evidence_status}")
    if diagnosis_status not in DIAGNOSIS_STATUSES:
        raise ValueError(f"알 수 없는 diagnosis_status: {diagnosis_status}")
    if confidence not in CONFIDENCE_LEVELS:
        raise ValueError(f"알 수 없는 confidence: {confidence}")
    if evidence_status == "unverified" and (issue_confirmed or diagnosis_status != "additional_review"):
        raise ValueError("미확인 근거는 확정 문제로 판정할 수 없습니다.")
    return {
        "evidence_status": evidence_status,
        "diagnosis_status": diagnosis_status,
        "issue_confirmed": issue_confirmed,
        "confidence": confidence,
        "business_impact_status": "not_measured",
    }
