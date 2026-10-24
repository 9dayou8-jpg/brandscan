# Consent-Aware MarTech Runtime Analysis Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or implement task-by-task with TDD.

**Goal:** Make BrandScan explain consent-dependent runtime differences from Omnibug and preserve Omnibug-style tag identifiers, types, events, and evidence without auto-accepting consent.

**Architecture:** Extend Playwright runtime capture with a non-invasive consent signal detector. Keep the existing API and `capture_runtime` flow; add explicit runtime consent metadata and render it in the existing MarTech panel. Reuse the current `network_media` classifier and add structured request detail fields.

**Tech Stack:** FastAPI, Playwright, Python standard library, vanilla JavaScript/CSS, pytest.

**Spec:** User-approved next step: consent state display + user-controlled reanalysis guidance + Omnibug-style detail table.

## Global Constraints

- Never auto-click cookie consent or import the user's browser cookies.
- Never treat an observed tag as proof of campaign operation, spend, or performance.
- Preserve existing `/api/analyze` response fields and dashboard tabs.
- Keep unknown, unobserved, and runtime-failure states distinct.
- Do not add a paid API or a new runtime dependency.

## Review Focus

- Consent banner visible: report `present_not_interacted`, do not click it.
- No consent banner detected: report `not_detected`, not `consented`.
- Runtime capture failure: preserve error and mark consent `not_measured`.
- Multiple IDs/events for one platform: deduplicate without losing values.
- Google Analytics vs Google Ads: preserve `tag_types` and ID values under shared provider grouping.

### Task 1: Consent signal model

**Files:**
- Create: `backend/app/consent.py`
- Create: `backend/tests/test_consent.py`
- Modify: `backend/app/browser_media.py`

- [ ] Write failing tests for visible banner, consent wording in body, and no signal.
- [ ] Run the focused test and verify the expected failure.
- [ ] Implement pure `classify_consent_signals(*, visible_selectors: list[str], body_text: str) -> dict[str, object]`.
- [ ] Return `present_not_interacted`, `not_detected`, or `not_measured` with signals and a Korean explanatory note.
- [ ] Add Playwright DOM-only detection after page load; never click.
- [ ] Run focused and full tests.

### Task 2: Runtime detail contract

**Files:**
- Modify: `backend/app/browser_media.py`, `backend/app/network_media.py`, `backend/app/main.py`
- Create/modify: `backend/tests/test_runtime_capture_api.py`, `backend/tests/test_omnibug_tag_details.py`

- [ ] Preserve `consent_status`, `consent_signals`, and `consent_note` through `/api/analyze`.
- [ ] Preserve tag identifiers, tag types, events, request evidence, and runtime source.
- [ ] Verify screenshot-derived synthetic request fixtures for Google, Bing, Criteo, Meta.

### Task 3: UI explanation and reanalysis guidance

**Files:**
- Modify: `frontend/app.js`, `frontend/styles.css`
- Modify: `frontend/index.html` only if an existing target needs a stable label.

- [ ] Add a MarTech consent status card with explicit “자동 동의하지 않음” copy.
- [ ] Render an honest next-action message when status is `present_not_interacted`.
- [ ] Render detail rows with platform, tag type, ID, event, source, and evidence.
- [ ] Keep tabs and section navigation working.
- [ ] Verify with a representative payload in a browser and run syntax tests.

### Task 4: Nike verification and documentation

- [ ] Run the exact Nike `/kr` URL variant available from the user evidence.
- [ ] Record observed runtime count, consent status, classified vendors, and unclassified count.
- [ ] Run `node --check frontend/app.js`, `git diff --check`, and `python3 -m pytest -q`.
- [ ] Update README or agent log only with measured facts.
- [ ] Commit and push after verification.
