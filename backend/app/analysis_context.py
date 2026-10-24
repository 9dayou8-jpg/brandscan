from __future__ import annotations

PAGE_TYPES = {"homepage", "service", "product", "landing", "blog", "article", "campaign", "unknown"}
MARKETING_OBJECTIVES = {"brand_awareness", "acquisition", "conversion", "lead_generation"}


def build_analysis_metadata(
    *,
    requested_url: str,
    final_url: str,
    predicted_page_type: str,
    marketing_objective: str,
    selected_page_type: str | None = None,
) -> dict[str, object]:
    if predicted_page_type not in PAGE_TYPES:
        raise ValueError(f"알 수 없는 페이지 유형: {predicted_page_type}")
    if selected_page_type is not None and selected_page_type not in PAGE_TYPES:
        raise ValueError(f"알 수 없는 선택 페이지 유형: {selected_page_type}")
    if marketing_objective not in MARKETING_OBJECTIVES:
        raise ValueError(f"알 수 없는 마케팅 목적: {marketing_objective}")
    selected = selected_page_type or predicted_page_type
    user_selected = selected_page_type is not None
    return {
        "analysis_scope": "single_url",
        "site_wide_inference": False,
        "requested_url": requested_url,
        "final_url": final_url,
        "page_type": {
            "predicted": predicted_page_type,
            "selected": selected,
            "source": "user" if user_selected else "auto",
            "confidence": "user_selected" if user_selected else "medium",
        },
        "marketing_objective": marketing_objective,
        "collection_method": ["server_http_fetch", "html_parser"],
        "parser_version": "0.1.0",
        "rulebook_version": "0.3.0",
    }
