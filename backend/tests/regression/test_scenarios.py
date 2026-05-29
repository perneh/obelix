"""Regression — scenario runner and validation API."""

import pytest

from tests.support.actions.regression_http import get, post, status
from tests.support.builders.api import build_encode_request
from tests.support.builders.encoding import build_cat034_north_marker_fields
from tests.support.builders.scenarios import build_minimal_scenario


@pytest.mark.regression
def test_scenario_validate(address, port):
    result = post(address, port, "/api/scenarios/validate", build_minimal_scenario())
    assert result["id"] == "regression-validate"
    assert result["name"] == "Regression validate"
    assert len(result["steps"]) == 1


@pytest.mark.regression
def test_scenario_validate_rejects_empty_steps(address, port):
    payload = build_minimal_scenario()
    payload["steps"] = []
    assert status(address, port, "POST", "/api/scenarios/validate", json=payload) == 400


@pytest.mark.regression
def test_scenario_motion_defaults(address, port):
    message = build_encode_request(category=34, fields=build_cat034_north_marker_fields())["message"]
    result = post(address, port, "/api/scenarios/motion-defaults", message)
    assert result["mode"] == "direction"
    assert result["heading_deg"] == 90.0
    assert result["ticks"] == 10
    assert len(result["waypoints"]) == 2
    assert result["waypoints"][0]["azimuth"] == 0.0
    assert result["waypoints"][1]["azimuth"] == 90.0


@pytest.mark.regression
def test_scenario_runs(address, port):
    assert isinstance(get(address, port, "/api/scenarios/runs"), list)
    assert status(address, port, "GET", "/api/scenarios/runs/nonexistent-regression-run") == 404
