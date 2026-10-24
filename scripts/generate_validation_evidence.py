from pathlib import Path
from datetime import datetime, timezone
import json

from backend.app.analysis_context import build_analysis_metadata
from backend.app.extractors.geo import extract_geo_facts
from backend.app.extractors.martech import detect_martech
from backend.app.extractors.technical_seo import extract_technical_seo
from backend.app.geo_evaluator import evaluate_geo
from backend.app.prioritizer import build_issues, deduplicate_issues, rank_issues

ROOT = Path(__file__).parents[1]
CASES = [
    ("normal-page.html", "정상 페이지"),
    ("missing-page.html", "누락 페이지"),
    ("suspicious-page.html", "의심 페이지"),
]


def main() -> None:
    stamp = datetime.now(timezone.utc).isoformat()
    rows = []
    for filename, label in CASES:
        url = f"https://fixture.example/{filename.removesuffix('-page.html')}"
        html = (ROOT / "fixtures" / filename).read_text(encoding="utf-8")
        seo = extract_technical_seo(html, url)
        martech = detect_martech(html)
        geo = extract_geo_facts(html)
        geo_evaluation = evaluate_geo(geo)
        issues = rank_issues(deduplicate_issues(build_issues(seo, martech, geo, marketing_objective="acquisition")))
        confirmed = [issue for issue in issues if issue["issue_confirmed"]]
        review = [issue for issue in issues if not issue["issue_confirmed"]]
        rows.append({
            "fixture": filename,
            "label": label,
            "analysis_metadata": build_analysis_metadata(
                requested_url=url,
                final_url=url,
                predicted_page_type="unknown",
                marketing_objective="acquisition",
            ),
            "observations": {
                "title": seo["title"],
                "description_present": bool(seo["description"]),
                "h1_count": len(seo["headings"]["h1"]),
                "missing_alt": seo["images"]["missing_alt"],
                "canonical": seo["canonical"],
                "martech_platforms": [item["platform"] for item in martech["media_inventory"]],
            },
            "confirmed_issue_count": len(confirmed),
            "additional_review_count": len(review),
            "confirmed_issues": [{"id": x["id"], "title": x["title"], "score": x["score"], "evidence": x["evidence"]} for x in confirmed],
            "additional_review_items": [{"id": x["id"], "title": x["title"], "evidence": x["evidence"]} for x in review],
            "geo_evaluation": geo_evaluation,
        })

    payload = {"generated_at": stamp, "rulebook_version": "0.3.0", "purpose": "acquisition", "cases": rows}
    evidence_dir = ROOT / "docs" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "validation-results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# BrandScan 검증 결과", "", f"- 생성 시각(UTC): {stamp}",
        "- 분석 범위: 공개 단일 URL fixture", "- 마케팅 목적: 신규 고객 유입(acquisition)",
        "- 규칙 버전: 0.3.0", "",
    ]
    for row in rows:
        lines.extend([
            f"## {row['label']} ({row['fixture']})", "",
            f"- Title: {row['observations']['title']}",
            f"- Description: {'확인' if row['observations']['description_present'] else '미확인'}",
            f"- H1 개수: {row['observations']['h1_count']}",
            f"- 이미지 alt 누락: {row['observations']['missing_alt']}개",
            f"- Canonical: {row['observations']['canonical'] or '미확인'}",
            f"- 탐지 매체: {', '.join(row['observations']['martech_platforms']) or '없음'}",
            f"- 확정 개선 과제: {row['confirmed_issue_count']}개",
            f"- 추가 검증 항목: {row['additional_review_count']}개",
            f"- GEO 준비도: {row['geo_evaluation']['geo_readiness']['status']}",
            "- AI 검색 성과: 미측정", "", "판정 근거:",
        ])
        lines.extend(f"- {item['title']}: {item['evidence']}" for item in row["confirmed_issues"])
        lines.extend(f"- 추가 검증: {item['title']} — {item['evidence']}" for item in row["additional_review_items"])
        lines.append("")
    (evidence_dir / "validation-results.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "cases": len(rows),
        "json": "docs/evidence/validation-results.json",
        "markdown": "docs/evidence/validation-results.md",
        "confirmed_total": sum(row["confirmed_issue_count"] for row in rows),
        "review_total": sum(row["additional_review_count"] for row in rows),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
