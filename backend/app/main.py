from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.browser_media import capture_runtime_requests
from backend.app.extractors.geo import extract_geo_facts
from backend.app.extractors.martech import detect_martech
from backend.app.extractors.technical_seo import extract_technical_seo
from backend.app.fetcher import fetch_public_page
from backend.app.geo_evaluator import evaluate_geo
from backend.app.network_media import classify_runtime_requests
from backend.app.page_context import infer_page_type
from backend.app.analysis_context import build_analysis_metadata
from backend.app.prioritizer import build_issues, deduplicate_issues, rank_issues


app = FastAPI(title="BrandScan MVP", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    url: str
    marketing_objective: str = "acquisition"
    page_type: str | None = None
    capture_runtime: bool = False


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _merge_media_inventory(static_items: list[dict[str, object]], runtime_items: list[dict[str, object]]) -> list[dict[str, object]]:
    merged = {str(item["platform"]): dict(item) for item in static_items}
    for item in runtime_items:
        platform = str(item["platform"])
        if platform not in merged:
            merged[platform] = {
                "platform": platform,
                "category": "runtime_detected",
                "status": "confirmed",
                "operating_inference": "likely",
                "evidence": list(item.get("evidence", [])),
                "events": list(item.get("events", [])),
                "note": "브라우저 런타임 네트워크 요청에서 확인됨. 실제 캠페인 운영·광고비·성과는 측정하지 않음.",
            }
        else:
            existing = merged[platform]
            existing["runtime_status"] = "confirmed"
            existing["runtime_events"] = list(item.get("events", []))
            existing["runtime_evidence"] = list(item.get("evidence", []))
    return list(merged.values())


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, object]:
    try:
        page = fetch_public_page(str(request.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    technical_seo = extract_technical_seo(page.html, page.final_url)
    predicted_page_type = infer_page_type(page.final_url, title=technical_seo.get("title"), headings=technical_seo.get("headings"))
    analysis_metadata = build_analysis_metadata(
        requested_url=page.requested_url,
        final_url=page.final_url,
        predicted_page_type=predicted_page_type,
        selected_page_type=request.page_type,
        marketing_objective=request.marketing_objective,
    )
    martech = detect_martech(page.html)
    if request.capture_runtime:
        runtime_capture = capture_runtime_requests(page.final_url)
        runtime_classification = classify_runtime_requests(runtime_capture.get("request_urls", []))
        martech["runtime_capture"] = runtime_capture
        martech["runtime_media_inventory"] = runtime_classification["media_inventory"]
        martech["runtime_request_count"] = runtime_classification["request_count"]
        martech["media_inventory"] = _merge_media_inventory(martech["media_inventory"], runtime_classification["media_inventory"])
    geo = extract_geo_facts(page.html)
    geo_evaluation = evaluate_geo(geo)
    all_issues = rank_issues(deduplicate_issues(build_issues(technical_seo, martech, geo, marketing_objective=request.marketing_objective)))
    confirmed_issues = [issue for issue in all_issues if issue["issue_confirmed"]]
    additional_review_items = [issue for issue in all_issues if not issue["issue_confirmed"]]
    return {
        "url": page.requested_url,
        "final_url": page.final_url,
        "status_code": page.status_code,
        "content_type": page.content_type,
        "html_size": len(page.html),
        "analysis_metadata": analysis_metadata,
        "technical_seo": technical_seo,
        "martech": martech,
        "geo": geo,
        "geo_evaluation": geo_evaluation,
        "issues": all_issues,
        "confirmed_issues": confirmed_issues,
        "additional_review_items": additional_review_items,
        "top_priorities": confirmed_issues[:3],
    }
