from backend.app.consent import classify_consent_signals


def test_consent_banner_is_reported_without_claiming_consent():
    result = classify_consent_signals(
        visible_selectors=["#onetrust-banner-sdk"],
        body_text="We use cookies to improve your experience.",
    )

    assert result["status"] == "present_not_interacted"
    assert "#onetrust-banner-sdk" in result["signals"]
    assert "consent_text" in result["signals"]
    assert "자동으로 동의" in result["note"]


def test_consent_wording_is_detected_when_selector_is_not_known():
    result = classify_consent_signals(
        visible_selectors=[],
        body_text="쿠키 설정을 확인해 주세요.",
    )

    assert result["status"] == "present_not_interacted"
    assert result["signals"] == ["consent_text"]


def test_missing_consent_signal_is_not_reported_as_consented():
    result = classify_consent_signals(visible_selectors=[], body_text="Nike homepage")

    assert result["status"] == "not_detected"
    assert result["signals"] == []
