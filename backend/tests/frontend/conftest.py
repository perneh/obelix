"""Shared Playwright fixtures for frontend UI tests."""

from __future__ import annotations

import logging

import pytest

from tests.support.cli_options import TargetConfig

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def base_url(target: TargetConfig) -> str:
    """Playwright base URL — uses the same --address/--port/--url options as regression tests."""
    return target.base_url


@pytest.fixture(scope="session", autouse=True)
def _ensure_playwright_chromium() -> None:
    """Skip frontend tests when Playwright browsers are not installed."""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            browser.close()
    except Exception as exc:
        pytest.skip(
            f"Playwright chromium is not available ({exc}). "
            "Install dev deps and run: playwright install chromium"
        )

    logger.info("Playwright chromium is available for frontend tests")
