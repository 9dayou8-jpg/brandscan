from __future__ import annotations


_CONSENT_TERMS = (
    "cookie",
    "cookies",
    "쿠키",
    "privacy preference",
    "privacy settings",
    "개인정보 설정",
    "동의",
)


def classify_consent_signals(*, visible_selectors: list[str], body_text: str) -> dict[str, object]:
    signals = list(dict.fromkeys(visible_selectors))
    normalized = body_text.lower()
    if any(term.lower() in normalized for term in _CONSENT_TERMS):
        signals.append("consent_text")
    signals = list(dict.fromkeys(signals))
    if signals:
        return {
            "status": "present_not_interacted",
            "signals": signals,
            "note": "동의 UI 또는 관련 문구가 확인되었지만 BrandScan은 자동으로 동의하지 않았습니다. 현재 분석 브라우저는 사용자의 브라우저 쿠키를 공유하지 않으므로, 동일 세션에서의 동의 후 재분석은 아직 지원되지 않습니다.",
        }
    return {
        "status": "not_detected",
        "signals": [],
        "note": "자동으로 동의 상태를 확인할 수 있는 신호가 관측되지 않았습니다. 이는 동의 완료를 의미하지 않습니다.",
    }
