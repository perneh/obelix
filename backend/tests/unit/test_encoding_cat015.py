"""Tests for Cat015 encoding — INCS target reports."""

import pytest

from app.asterix.categories.cat015 import Cat015
from tests.support.actions.encoding import run_encode_cat015_datablock
from tests.support.assertions.encoding import assert_datablock_category, assert_hex_equals
from tests.support.builders.encoding import build_cat015_range_plot_fields


@pytest.mark.unit
def test_range_plot_encodes_expected_hex():
    fields = build_cat015_range_plot_fields(sac=1, sic=2, track_number=42)
    result = run_encode_cat015_datablock(fields)
    assert_datablock_category(result, 15)
    assert_hex_equals(result, "0F0014C7010580010202004000002A00C3502000")


@pytest.mark.unit
def test_wgs84_plot_is_larger_than_range_only():
    range_fields = build_cat015_range_plot_fields()
    wgs_fields = build_cat015_range_plot_fields()
    wgs_fields["position_type"] = 1
    wgs_fields["wgs84"] = {"latitude_deg": 59.0, "longitude_deg": 18.0}
    range_block = run_encode_cat015_datablock(range_fields)
    wgs_block = run_encode_cat015_datablock(wgs_fields)
    assert len(wgs_block) > len(range_block)
