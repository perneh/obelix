"""Frontend regression — top navigation and panel switching."""

import pytest
from playwright.sync_api import Page

from tests.frontend.support.actions.navigation import goto_home, navigate_to
from tests.frontend.support.assertions.panels import assert_active_panel, assert_page_title_contains


@pytest.mark.frontend
def test_home_loads(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    assert_page_title_contains(page, "Obelix")
    assert_active_panel(page, "tab-asterix-message")


@pytest.mark.frontend
def test_navigate_asterix_scenario_builder(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    navigate_to(page, "asterix", "scenario")
    assert_active_panel(page, "tab-asterix-scenario")


@pytest.mark.frontend
def test_navigate_link16_message_editor(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    navigate_to(page, "link16", "message")
    assert_active_panel(page, "tab-link16-message")


@pytest.mark.frontend
def test_navigate_link16_scenario_builder(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    navigate_to(page, "link16", "scenario")
    assert_active_panel(page, "tab-link16-scenario")
