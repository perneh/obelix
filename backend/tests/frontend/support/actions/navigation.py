"""Navigation actions for the Obelix web UI."""

from __future__ import annotations

import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def goto_home(page: Page, base_url: str) -> None:
    logger.debug("Opening home page at %s", base_url)
    page.goto(base_url)
    page.wait_for_load_state("networkidle")


def open_nav_dropdown(page: Page, protocol: str) -> None:
    logger.debug("Opening nav dropdown for protocol=%s", protocol)
    toggle = page.locator(f'.nav-dropdown[data-protocol="{protocol}"] .nav-dropdown-toggle')
    toggle.click()


def navigate_to(page: Page, protocol: str, subtab: str) -> None:
    logger.debug("Navigating to protocol=%s subtab=%s", protocol, subtab)
    open_nav_dropdown(page, protocol)
    page.locator(
        f'.nav-dropdown-item[data-protocol="{protocol}"][data-subtab="{subtab}"]'
    ).click()
