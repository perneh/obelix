"""Message editor actions in the Obelix web UI."""

from __future__ import annotations

import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def click_asterix_encode(page: Page) -> None:
    logger.debug("Clicking ASTERIX Generate Hex")
    page.locator("#btn-encode").click()


def click_link16_encode(page: Page) -> None:
    logger.debug("Clicking Link 16 Generate Hex")
    page.locator("#btn-link16-encode").click()


def read_asterix_hex_output(page: Page) -> str:
    return page.locator("#hex-output").inner_text()


def read_link16_hex_output(page: Page) -> str:
    return page.locator("#link16-hex-output").inner_text()
