from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.app.extractors.geo import extract_geo_facts
from backend.app.extractors.martech import detect_martech
from backend.app.extractors.technical_seo import extract_technical_seo
from backend.app.fetcher import fetch_public_page
from backend.app.prioritizer import build_issues, rank_issues


app = FastAPI(title="BrandScan MVP", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    url: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, object]:
    page = fetch_public_page(str(request.url))
    technical_seo = extract_technical_seo(page.html, page.final_url)
    martech = detect_martech(page.html)
    geo = extract_geo_facts(page.html)
    issues = rank_issues(build_issues(technical_seo, martech, geo))
    return {
        "url": page.requested_url,
        "final_url": page.final_url,
        "status_code": page.status_code,
        "content_type": page.content_type,
        "html_size": len(page.html),
        "technical_seo": technical_seo,
        "martech": martech,
        "geo": geo,
        "issues": issues,
        "top_priorities": issues[:3],
    }
