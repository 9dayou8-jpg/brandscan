import pytest

from backend.app.diagnosis import classify_finding


def test_observed_evidence_does_not_confirm_business_impact():
    result = classify_finding(
        evidence_status="confirmed",
        diagnosis_status="recommendation",
        issue_confirmed=False,
        confidence="medium",
    )

    assert result == {
        "evidence_status": "confirmed",
        "diagnosis_status": "recommendation",
        "issue_confirmed": False,
        "confidence": "medium",
        "business_impact_status": "not_measured",
    }


def test_unverified_evidence_requires_additional_review():
    result = classify_finding(
        evidence_status="unverified",
        diagnosis_status="additional_review",
        issue_confirmed=False,
        confidence="low",
    )

    assert result["diagnosis_status"] == "additional_review"
    assert result["issue_confirmed"] is False
    assert result["business_impact_status"] == "not_measured"


@pytest.mark.parametrize("field,value", [
    ("evidence_status", "invalid"),
    ("diagnosis_status", "invalid"),
    ("confidence", "invalid"),
])
def test_classification_rejects_unknown_states(field, value):
    values = {
        "evidence_status": "confirmed",
        "diagnosis_status": "normal",
        "issue_confirmed": False,
        "confidence": "high",
    }
    values[field] = value

    with pytest.raises(ValueError):
        classify_finding(**values)
