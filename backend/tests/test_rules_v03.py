import pytest

from backend.app.prioritizer import calculate_priority


def test_priority_uses_weighted_sum_and_keeps_calculation_evidence():
    result = calculate_priority(
        impact=3,
        urgency=2,
        ease=3,
        marketing_objective="acquisition",
    )

    assert result == {
        "formula": "(impact × 4) + (urgency × 3) + (ease × 1)",
        "formula_version": "0.3.0",
        "weights": {"impact": 4, "urgency": 3, "ease": 1},
        "factors": {"impact": 3, "urgency": 2, "ease": 3},
        "marketing_objective": "acquisition",
        "score": 21,
    }


@pytest.mark.parametrize("field", ["impact", "urgency", "ease"])
def test_priority_rejects_scores_outside_one_to_three(field):
    factors = {"impact": 2, "urgency": 2, "ease": 2}
    factors[field] = 0

    with pytest.raises(ValueError):
        calculate_priority(**factors, marketing_objective="conversion")
