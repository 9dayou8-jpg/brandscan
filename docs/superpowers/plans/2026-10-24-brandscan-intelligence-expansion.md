# BrandScan Intelligence Expansion Plan

> **For agentic workers:** execute this plan task-by-task with TDD; preserve the existing diagnostic API and dashboard.

**Goal:** Extend the working single-URL evidence diagnostic into a BrandProfile, SEO/GEO intelligence, content-gap, and recommendation pipeline without removing existing functionality.

**Architecture:** Keep the existing FastAPI + vanilla JavaScript stack. Add versioned domain modules and pure rule functions first; return structured JSON from the existing `/api/analyze`. Add a BrandProfile draft endpoint before any persistence. Keep AI Visibility as an explicit not-measured adapter until a supported provider is approved.

**Spec:** `docs/brandscan-data-spec-v1.md` and the approved BrandScan expansion requirements.

## Current baseline

- Working: public URL fetch, SSRF boundary, Technical SEO extraction, static/runtime MarTech detection, media inventory, GEO evidence evaluation, weighted priorities, deduplication, dashboard tabs, PDF print, fixtures, public GitHub repository.
- Missing: BrandProfile draft/confirmation, body-content model, keyword seeds, PromptSet, ContentGap, CompetitorProfile, AIResponse adapter, persistence, deployment.
- Constraint: no destructive schema/data changes; no paid API or external provider without approval.

## One-week safe MVP scope

1. BrandProfile draft extraction and user-editable confirmation.
2. PageContent body text and evidence-preserving content inventory.
3. Keyword candidate extraction/classification with `Suggested Keyword` status; no search volume/rank claims.
4. GEO readiness/content gap criteria backed by evidence IDs.
5. Recommendation output using the existing priority engine.
6. Keep AI Visibility explicitly `not_measured` unless a provider is later approved.

## Tasks

### Task 1: BrandProfile draft contract

**Files:**
- Create: `backend/app/brand_profile.py`
- Create: `backend/tests/test_brand_profile.py`
- Modify: `backend/app/main.py`

**Tests:** URL/title/OG data produce a draft; missing industry/products become `needs_user_confirmation`; no field is auto-confirmed without evidence.

### Task 2: PageContent body and evidence extraction

**Files:**
- Modify: `backend/app/extractors/technical_seo.py`
- Create: `backend/tests/test_page_content.py`

**Tests:** body text, author/date signals, internal/external links, stable evidence IDs, and missing fields remain unknown.

### Task 3: Keyword seeds and clusters

**Files:**
- Create: `backend/app/keyword_intelligence.py`
- Create: `backend/tests/test_keyword_intelligence.py`
- Modify: `backend/app/main.py`

**Tests:** Korean/English normalization, duplicate removal, deterministic type/intent labels, `suggested` source, and no fabricated volume/rank.

### Task 4: Content gaps and recommendation bridge

**Files:**
- Create: `backend/app/content_intelligence.py`
- Create: `backend/tests/test_content_intelligence.py`
- Modify: `backend/app/main.py`, `frontend/app.js`

**Tests:** missing FAQ/evidence/comparison/outdated signals map to ContentGap with evidence refs and existing/new page recommendations.

### Task 5: Dashboard integration

**Files:**
- Modify: `frontend/index.html`, `frontend/app.js`, `frontend/styles.css`
- Create: browser smoke assertions under `backend/tests` or a reproducible browser script.

Preserve the approved dark dashboard hierarchy. Add seed confirmation and SEO/GEO intelligence panels without replacing existing panels.

### Task 6: Evidence and public reproduction

- Extend fixture matrix for normal/missing/suspicious/content-gap cases.
- Regenerate `docs/evidence/validation-results.*`.
- Update README and `docs/agent-log.md`.
- Keep AI Visibility as `not_measured` in all evidence unless an approved provider is connected.

## Review gates / user confirmation needed

- Confirm the first-party fields for `brand_name`, `industry`, and `primary_products` after automatic draft extraction.
- Confirm whether any paid LLM/search/AI provider may be connected. Default is no external paid API.
- Confirm deployment target before adding Playwright browser installation configuration.

## Verification commands

```bash
node --check frontend/app.js
python3 -m pytest -q
PYTHONPATH=. python3 scripts/generate_validation_evidence.py
```
