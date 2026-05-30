"""Frontend regression — Link 16 scenario JSON import/export."""

import json

import pytest
from playwright.sync_api import Page

from tests.frontend.support.actions.navigation import goto_home, navigate_to
from tests.frontend.support.actions.scenario_io import (
    click_link16_apply_json_editor,
    click_link16_export_scenario,
    read_link16_json_status,
    set_link16_json_editor,
)
from tests.frontend.support.assertions.panels import assert_active_panel, assert_element_visible, assert_text_contains


MINIMAL_LINK16_SCENARIO = {
    "id": "ui-test-export",
    "name": "UI export test",
    "description": "Created by Playwright frontend regression test",
    "transport": {"host": "host.docker.internal", "port": 8700, "protocol": "udp"},
    "loop_count": 1,
    "interval_ms": 1000,
    "steps": [
        {
            "id": "step-1",
            "name": "J3.2 air track",
            "message": {
                "j_series": "J3.2",
                "fields": {
                    "source_ju": 10001,
                    "npg": 2,
                    "track_number": 101,
                    "identity": 3,
                    "platform": 1,
                    "mode3a": 7341,
                    "position": {"latitude_deg": 59.33, "longitude_deg": 18.05},
                    "altitude_ft": 35000,
                    "course_deg": 90,
                    "speed_kts": 450,
                },
            },
            "delay_ms": 0,
            "repeat": 1,
        }
    ],
}


@pytest.mark.frontend
def test_link16_scenario_export_controls_visible(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    navigate_to(page, "link16", "scenario")
    assert_active_panel(page, "tab-link16-scenario")
    assert_element_visible(page, "#btn-link16-export-scenario")
    assert_element_visible(page, "#btn-link16-import-scenario")
    assert_element_visible(page, "#btn-link16-apply-json-editor")
    assert_element_visible(page, "#link16-scenario-json-editor")


@pytest.mark.frontend
def test_link16_scenario_import_and_export_json(page: Page, base_url: str) -> None:
    goto_home(page, base_url)
    navigate_to(page, "link16", "scenario")

    set_link16_json_editor(page, json.dumps(MINIMAL_LINK16_SCENARIO, indent=2))
    click_link16_apply_json_editor(page)
    page.wait_for_timeout(500)

    status = read_link16_json_status(page)
    assert_text_contains(status, "Imported")
    assert_text_contains(status, "1 steps")

    with page.expect_download() as download_info:
        click_link16_export_scenario(page)
    download = download_info.value
    assert download.suggested_filename.endswith(".json")

    path = download.path()
    assert path is not None
    exported = json.loads(path.read_text(encoding="utf-8"))
    assert exported["id"] == MINIMAL_LINK16_SCENARIO["id"]
    assert len(exported["steps"]) == 1
    assert exported["steps"][0]["message"]["j_series"] == "J3.2"
