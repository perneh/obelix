#!/usr/bin/env python3
"""Capture Obelix course screenshots with Playwright."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "docs" / "course" / "images"


def navigate_to(page, protocol: str, subtab: str) -> None:
    page.locator(f'.nav-dropdown[data-protocol="{protocol}"] .nav-dropdown-toggle').click()
    page.locator(
        f'.nav-dropdown-item[data-protocol="{protocol}"][data-subtab="{subtab}"]'
    ).click()
    page.wait_for_timeout(400)


def capture_frontend(page, base_url: str, out: Path) -> None:
    page.set_viewport_size({"width": 1440, "height": 900})

    page.goto(base_url, wait_until="networkidle")
    page.wait_for_timeout(1500)
    page.screenshot(path=str(out / "01-home-asterix-message.png"), full_page=True)

    page.locator('.nav-dropdown[data-protocol="asterix"] .nav-dropdown-toggle').click()
    page.wait_for_timeout(300)
    page.screenshot(path=str(out / "02-nav-dropdown-asterix.png"), full_page=False)

    page.locator(
        '.nav-dropdown-item[data-protocol="asterix"][data-subtab="message"]'
    ).click()
    page.wait_for_timeout(400)
    page.locator("#btn-encode").click()
    page.wait_for_timeout(800)
    page.screenshot(path=str(out / "03-asterix-encode-hex.png"), full_page=True)

    navigate_to(page, "asterix", "scenario")
    page.wait_for_timeout(600)
    page.screenshot(path=str(out / "04-asterix-scenario-builder.png"), full_page=True)

    scenario_json = page.locator(".scenario-json-card").first
    if scenario_json.is_visible():
        scenario_json.scroll_into_view_if_needed()
        page.wait_for_timeout(300)
        scenario_json.screenshot(path=str(out / "05-asterix-scenario-json.png"))

    navigate_to(page, "asterix", "library")
    page.wait_for_timeout(800)
    page.screenshot(path=str(out / "06-asterix-library.png"), full_page=True)

    navigate_to(page, "link16", "message")
    page.wait_for_timeout(1200)
    page.screenshot(path=str(out / "07-link16-message-editor.png"), full_page=True)

    page.locator("#btn-link16-help").click()
    page.wait_for_timeout(800)
    page.screenshot(path=str(out / "08-link16-help-panel.png"), full_page=True)

    navigate_to(page, "link16", "scenario")
    page.wait_for_timeout(600)
    page.screenshot(path=str(out / "09-link16-scenario-builder.png"), full_page=True)

    navigate_to(page, "link16", "library")
    page.wait_for_timeout(800)
    page.screenshot(path=str(out / "10-link16-library.png"), full_page=True)


def _open_swagger_operation(page, href_fragment: str, screenshot: Path) -> bool:
    link = page.locator(f'a[href="{href_fragment}"]')
    if not link.count():
        return False
    link.first.click()
    page.wait_for_timeout(800)
    page.screenshot(path=str(screenshot), full_page=True)
    return True


def capture_backend(page, base_url: str, out: Path) -> None:
    page.set_viewport_size({"width": 1440, "height": 900})

    page.goto(f"{base_url}/docs", wait_until="networkidle")
    page.wait_for_timeout(1500)
    page.screenshot(path=str(out / "11-swagger-overview.png"), full_page=True)

    if not _open_swagger_operation(
        page,
        "#/send/send_cat_048_api_send_48_post",
        out / "12-swagger-asterix-send.png",
    ):
        send = page.get_by_role("link", name="POST /api/send/48", exact=False)
        if send.count():
            send.first.click()
            page.wait_for_timeout(800)
            page.screenshot(path=str(out / "12-swagger-asterix-send.png"), full_page=True)

    if not _open_swagger_operation(
        page,
        "#/link16/send_J3_2_api_link16_send_J3_2_post",
        out / "13-swagger-link16-send.png",
    ):
        send_link = page.locator('a[href*="link16/send/J3-2"]')
        if send_link.count():
            send_link.first.click()
            page.wait_for_timeout(800)
            page.screenshot(path=str(out / "13-swagger-link16-send.png"), full_page=True)

    page.goto(f"{base_url}/docs", wait_until="networkidle")
    page.wait_for_timeout(800)
    if not _open_swagger_operation(
        page,
        "#/link16/get_link16_messages_api_link16_messages_get",
        out / "14-swagger-link16-messages.png",
    ):
        page.goto(f"{base_url}/docs#/link16", wait_until="networkidle")
        page.wait_for_timeout(800)
        page.screenshot(path=str(out / "14-swagger-link16-messages.png"), full_page=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture Obelix course screenshots")
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--output", type=Path, default=OUT_DIR)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            capture_frontend(page, args.base_url.rstrip("/"), args.output)
            capture_backend(page, args.base_url.rstrip("/"), args.output)
        finally:
            browser.close()

    files = sorted(args.output.glob("*.png"))
    print(f"Captured {len(files)} screenshots in {args.output}")
    for path in files:
        print(f"  {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
