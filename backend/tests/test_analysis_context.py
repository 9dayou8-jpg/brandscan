import pytest

from backend.app.analysis_context import build_analysis_metadata


def test_analysis_metadata_records_scope_page_type_and_objective():
    result = build_analysis_metadata(
        requested_url="https://example.com/service",
        final_url="https://example.com/service",
        predicted_page_type="service",
        marketing_objective="acquisition",
    )

    assert result == {
        "analysis_scope": "single_url",
        "site_wide_inference": False,
        "requested_url": "https://example.com/service",
        "final_url": "https://example.com/service",
        "page_type": {
            "predicted": "service",
            "selected": "service",
            "source": "auto",
            "confidence": "medium",
        },
        "marketing_objective": "acquisition",
        "collection_method": ["server_http_fetch", "html_parser"],
        "parser_version": "0.1.0",
        "rulebook_version": "0.3.0",
    }


def test_user_page_type_override_is_preserved():
    result = build_analysis_metadata(
        requested_url="https://example.com/landing",
        final_url="https://example.com/landing",
        predicted_page_type="service",
        selected_page_type="landing",
        marketing_objective="lead_generation",
    )

    assert result["page_type"] == {
        "predicted": "service",
        "selected": "landing",
        "source": "user",
        "confidence": "user_selected",
    }


@pytest.mark.parametrize("field,value", [
    ("predicted_page_type", "unknown_type"),
    ("marketing_objective", "traffic_growth"),
])
def test_analysis_metadata_rejects_unknown_context_values(field, value):
    values = {
        "requested_url": "https://example.com",
        "final_url": "https://example.com",
        "predicted_page_type": "homepage",
        "marketing_objective": "brand_awareness",
    }
    values[field] = value

    with pytest.raises(ValueError):
        build_analysis_metadata(**values)
