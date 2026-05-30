"""Scenario builder import/export actions in the Obelix web UI."""

from __future__ import annotations

import logging

from playwright.sync_api import Page

logger = logging.getLogger(__name__)


def add_link16_step_from_message_editor(page: Page) -> None:
    logger.debug("Adding Link 16 step from message editor")
    page.locator("#btn-link16-add-step").click()


def click_link16_export_scenario(page: Page) -> None:
    logger.debug("Clicking Link 16 scenario export")
    page.locator("#btn-link16-export-scenario").click()


def click_link16_apply_json_editor(page: Page) -> None:
    logger.debug("Applying Link 16 scenario JSON editor")
    page.locator("#btn-link16-apply-json-editor").click()


def set_link16_json_editor(page: Page, text: str) -> None:
    logger.debug("Setting Link 16 scenario JSON editor content")
    editor = page.locator("#link16-scenario-json-editor")
    editor.fill(text)


def read_link16_json_status(page: Page) -> str:
    return page.locator("#link16-scenario-json-status").inner_text()
