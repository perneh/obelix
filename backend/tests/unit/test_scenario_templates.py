"""Tests for realistic scenario templates."""

import pytest

from app.scenarios.geo import bearing_deg, distance_m, BROMMA, KALININGRAD, VISBY
from app.scenarios.templates import build_template, list_template_catalog


@pytest.mark.unit
def test_catalog_lists_three_templates():
    catalog = list_template_catalog()
    ids = {item["id"] for item in catalog}
    assert ids == {"jas-bromma-visby", "mig-kaliningrad-visby", "baltic-combined"}


@pytest.mark.unit
def test_jas_template_uses_all_categories():
    scenario = build_template("jas-bromma-visby")
    categories = {step.message.category for step in scenario.steps}
    assert categories == {15, 16, 34, 48, 62}
    assert len(scenario.steps) == 6
    motion_steps = [s for s in scenario.steps if s.motion and s.motion.enabled]
    assert len(motion_steps) == 3


@pytest.mark.unit
def test_mig_template_route_heading_northwest():
    scenario = build_template("mig-kaliningrad-visby")
    track = next(s for s in scenario.steps if s.id == "mig-062")
    assert track.motion is not None
    heading = track.motion.heading_deg
    expected = bearing_deg(*KALININGRAD, *VISBY)
    assert heading == pytest.approx(expected, abs=1.0)


@pytest.mark.unit
def test_combined_has_both_aircraft_tracks():
    scenario = build_template("baltic-combined")
    track_numbers = {
        s.message.fields.get("track_number")
        for s in scenario.steps
        if s.message.category == 62
    }
    assert track_numbers == {101, 201}


@pytest.mark.unit
def test_jas_route_distance_realistic():
    dist = distance_m(*BROMMA, *VISBY)
    assert 180_000 < dist < 220_000
