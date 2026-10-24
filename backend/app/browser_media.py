from __future__ import annotations

import asyncio
import os
from typing import Any

from backend.app.consent import classify_consent_signals


DEFAULT_BROWSER_PATH = "/home/dayoung/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"


def _capture_async(url: str, wait_ms: int) -> dict[str, object]:
    from playwright.async_api import async_playwright

    async def run() -> dict[str, object]:
        requests: list[str] = []
        browser_path = os.getenv("BRANDSCAN_BROWSER_PATH") or DEFAULT_BROWSER_PATH
        async with async_playwright() as playwright:
            launch_kwargs: dict[str, Any] = {"headless": True}
            if os.path.exists(browser_path):
                launch_kwargs["executable_path"] = browser_path
            browser = await playwright.chromium.launch(**launch_kwargs)
            context = await browser.new_context(
                ignore_https_errors=True,
                user_agent="BrandScan/0.2 runtime diagnostic",
            )
            page = await context.new_page()
            page.on("request", lambda request: requests.append(request.url))
            response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(wait_ms)
            consent_snapshot = await page.evaluate("""() => {
                const selectors = [
                    '[id*="cookie" i]', '[class*="cookie" i]', '[id*="consent" i]',
                    '[class*="consent" i]', '[aria-label*="cookie" i]', '[aria-label*="consent" i]'
                ];
                const visible = [];
                for (const selector of selectors) {
                    for (const element of document.querySelectorAll(selector)) {
                        const rect = element.getBoundingClientRect();
                        const style = window.getComputedStyle(element);
                        if (rect.width > 0 && rect.height > 0 && style.visibility !== 'hidden' && style.display !== 'none') {
                            const label = element.id ? `#${element.id}` : `${element.tagName.toLowerCase()}.${String(element.className || '').split(/\\s+/).filter(Boolean).slice(0, 2).join('.')}`;
                            if (label && !visible.includes(label)) visible.push(label);
                        }
                    }
                }
                return { visible_selectors: visible.slice(0, 12), body_text: (document.body?.innerText || '').slice(0, 12000) };
            }""")
            consent = classify_consent_signals(
                visible_selectors=consent_snapshot.get("visible_selectors", []),
                body_text=consent_snapshot.get("body_text", ""),
            )
            await browser.close()
            return {
                "status_code": response.status if response else None,
                "final_url": page.url,
                "request_urls": list(dict.fromkeys(requests)),
                "capture_method": "playwright_network_request",
                "consent_status": consent["status"],
                "consent_signals": consent["signals"],
                "consent_note": consent["note"],
            }

    return asyncio.run(run())


def capture_runtime_requests(url: str, *, wait_ms: int = 5000) -> dict[str, object]:
    try:
        return _capture_async(url, wait_ms)
    except Exception as exc:  # runtime capture is an optional enrichment path
        return {
            "status_code": None,
            "final_url": url,
            "request_urls": [],
            "capture_method": "unavailable",
            "error": str(exc),
        }
