"""UI panel and content assertion helpers."""

from __future__ import annotations

from playwright.sync_api import Page, expect


def assert_active_panel(page: Page, panel_id: str) -> None:
    panel = page.locator(f"#{panel_id}.panel.active")
    expect(panel).to_be_visible()


def assert_page_title_contains(page: Page, text: str) -> None:
    expect(page.locator("h1")).to_contain_text(text)


def assert_element_visible(page: Page, selector: str) -> None:
    expect(page.locator(selector)).to_be_visible()


def assert_text_contains(actual: str, expected: str) -> None:
    assert expected in actual, f"Expected {expected!r} in {actual!r}"


def assert_hex_output_valid(text: str) -> None:
    assert "Error:" not in text, f"Unexpected error in hex output: {text!r}"
    assert text.strip() not in {"", "—"}, f"Expected encoded hex output, got {text!r}"
