from __future__ import annotations

import asyncio
import os
from typing import Any


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
            await browser.close()
            return {
                "status_code": response.status if response else None,
                "final_url": page.url,
                "request_urls": list(dict.fromkeys(requests)),
                "capture_method": "playwright_network_request",
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
