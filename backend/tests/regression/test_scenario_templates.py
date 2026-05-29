"""Regression — built-in scenario templates API."""

import pytest

from tests.support.actions.regression_http import get, post
from tests.support.builders.scenarios import BALTIC_TEMPLATE_IDS


@pytest.mark.regression
def test_scenario_templates_catalog(address, port):
    assert {item["id"] for item in get(address, port, "/api/scenario-templates")} == BALTIC_TEMPLATE_IDS


@pytest.mark.regression
def test_scenario_template_jas(address, port):
    template = get(address, port, "/api/scenario-templates/jas-bromma-visby")
    assert template["id"] == "jas-bromma-visby"
    assert template["name"] == "JAS 39 – Bromma → Visby"
    assert len(template["steps"]) == 10


@pytest.mark.regression
def test_scenario_template_build(address, port):
    built = post(address, port, "/api/scenario-templates/jas-bromma-visby/build", {"ticks": 5})
    assert built["template_id"] == "jas-bromma-visby"

    motion_step = next(
        step for step in built["steps"] if step.get("motion") and step["motion"].get("enabled")
    )
    assert motion_step["motion"]["ticks"] == 5
