"""Tests for Cat034 encoding — specification-style, functional."""

import pytest

from tests.support.actions.encoding import run_encode_cat034_datablock, run_encode_cat034_record
from tests.support.assertions.encoding import (
    assert_datablock_category,
    assert_datablock_length,
    assert_fspec_byte,
    assert_hex_equals,
    assert_record_shorter_than,
)
from tests.support.builders.encoding import (
    build_cat034_north_marker_fields,
    build_cat034_sector_crossing_fields,
)


@pytest.mark.unit
def test_north_marker_encodes_expected_hex():
    fields = build_cat034_north_marker_fields(sac=1, sic=2)
    result = run_encode_cat034_datablock(fields)
    assert_datablock_category(result, 34)
    assert_datablock_length(result, 7)
    assert_hex_equals(result, "220007C0010102")


@pytest.mark.unit
def test_sector_crossing_includes_azimuth_fspec():
    fields = build_cat034_sector_crossing_fields(sac=3, sic=4, azimuth=90.0)
    result = run_encode_cat034_datablock(fields)
    assert_datablock_category(result, 34)
    assert_datablock_length(result, 9)
    assert_fspec_byte(result, 3, 0xE0)


@pytest.mark.unit
def test_sector_crossing_record_is_longer_than_north_marker():
    north_fields = build_cat034_north_marker_fields()
    sector_fields = build_cat034_sector_crossing_fields(sac=1, sic=1, azimuth=0.0)
    north = run_encode_cat034_record(north_fields)
    sector = run_encode_cat034_record(sector_fields)
    assert_record_shorter_than(north, sector)
