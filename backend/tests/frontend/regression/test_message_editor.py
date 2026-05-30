"""Frontend regression — ASTERIX and Link 16 message editors."""

import pytest
from playwright.sync_api import Page

from tests.frontend.support.actions.message_editor import (
    click_asterix_encode,
    click_link16_encode,
    read_asterix_hex_output,
    read_link16_hex_output,
)
from tests.frontend.support.actions.navigation import goto_home, navigate_to
from tests.frontend.support.assertions.panels import assert_hex_output_valid, assert_text_contains


@pytest.mark.frontend
def test_asterix_encode_button_produces_hex(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    click_asterix_encode(page)
    page.wait_for_timeout(800)
    assert_hex_output_valid(read_asterix_hex_output(page))


@pytest.mark.frontend
def test_link16_encode_button_produces_hex(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    navigate_to(page, "link16", "message")
    page.wait_for_timeout(1200)
    click_link16_encode(page)
    page.wait_for_timeout(800)
    output = read_link16_hex_output(page)
    assert_hex_output_valid(output)
    assert "JREA" in output.upper() or output.upper().startswith("4A524541")


@pytest.mark.frontend
def test_link16_message_help_panel(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    navigate_to(page, "link16", "message")
    page.wait_for_timeout(1200)

    page.locator("#btn-link16-help").click()
    page.wait_for_timeout(800)

    panel = page.locator("#link16-help-panel")
    assert panel.is_visible()
    content = panel.inner_text()
    assert_text_contains(content, "J")
    assert_text_contains(content, "source_ju")
