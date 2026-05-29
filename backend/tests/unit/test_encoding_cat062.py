"""Tests for Cat062 encoding — Eurocontrol Part 9 ed. 1.21."""

import pytest

from tests.support.actions.encoding import run_encode_cat062_datablock
from tests.support.assertions.encoding import (
    assert_datablock_category,
    assert_length_field_matches,
)
from tests.support.builders.encoding import (
    build_cat062_minimal_fields,
    build_cat062_system_track_fields,
)


@pytest.mark.unit
def test_minimal_track_includes_mandatory_items():
    fields = build_cat062_minimal_fields(track_number=42, time_seconds=128.0)
    result = run_encode_cat062_datablock(fields)
    assert_datablock_category(result, 62)
    assert_length_field_matches(result)
    assert len(result) == 13


@pytest.mark.unit
def test_system_track_with_wgs84_is_larger_than_minimal():
    minimal = run_encode_cat062_datablock(build_cat062_minimal_fields())
    full = run_encode_cat062_datablock(build_cat062_system_track_fields())
    assert len(full) > len(minimal)


@pytest.mark.unit
@pytest.mark.parametrize(
    "position_type",
    [0, 1, 2],
)
def test_position_type_changes_record_size(position_type):
    fields = build_cat062_minimal_fields()
    base = run_encode_cat062_datablock(fields)
    fields["position_type"] = position_type
    if position_type == 1:
        fields["cartesian"] = {"x_m": 500.0, "y_m": -250.0}
    elif position_type == 2:
        fields["wgs84"] = {"latitude_deg": 59.0, "longitude_deg": 18.0}
    sized = run_encode_cat062_datablock(fields)
    if position_type == 0:
        assert len(sized) == len(base)
    else:
        assert len(sized) > len(base)


@pytest.mark.unit
def test_cartesian_position_encoding():
    fields = build_cat062_minimal_fields()
    fields["position_type"] = 1
    fields["cartesian"] = {"x_m": 1000.0, "y_m": 2000.0}
    result = run_encode_cat062_datablock(fields)
    assert_datablock_category(result, 62)
    assert_length_field_matches(result)
