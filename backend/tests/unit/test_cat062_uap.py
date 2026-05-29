"""Tests for Cat 062 UAP coverage and FRN encoding."""

import pytest

from app.asterix.categories.cat062 import Cat062
from app.asterix.categories.cat062_uap import CAT062_UAP
from tests.support.actions.encoding import run_encode_cat062_datablock
from tests.support.assertions.encoding import assert_datablock_category, assert_length_field_matches
from tests.support.builders.encoding import build_cat062_minimal_fields, build_cat062_system_track_fields


@pytest.mark.unit
def test_uap_lists_35_frn_positions():
    assert len(CAT062_UAP) == 35
    assert CAT062_UAP[0].frn == 1
    assert CAT062_UAP[-1].frn == 35


@pytest.mark.unit
def test_category_definition_exposes_uap_table():
    uap = Cat062.definition().to_dict()["uap"]
    assert len(uap) == 35
    implemented = [row for row in uap if row["implemented"]]
    assert len(implemented) >= 28
    spare = [row for row in uap if row["spare"]]
    assert {row["frn"] for row in spare} == {2, 29, 30, 31, 32, 33}


@pytest.mark.unit
def test_optional_frns_can_be_included():
    fields = build_cat062_system_track_fields()
    fields["acceleration"] = {"include": 1, "ax_mps2": 1.0, "ay_mps2": -0.5}
    fields["target_identification"] = {"include": 1, "sti": 0, "callsign": "SVF123"}
    fields["mode_of_movement"] = {
        "include": 1,
        "transversal": 0,
        "longitudinal": 0,
        "vertical": 1,
        "altitude_discrepancy": 0,
    }
    fields["barometric_altitude"] = {"include": 1, "qnh_applied": 1, "flight_level": 360.0}
    fields["rate_of_climb"] = {"include": 1, "fpm": 1500.0}
    fields["mode2_code"] = {"include": 1, "code": 1234}
    fields["composed_track_number"] = {"include": 1, "system_unit_id": 2, "system_track_number": 99}

    result = run_encode_cat062_datablock(fields)
    assert_datablock_category(result, 62)
    assert_length_field_matches(result)
    assert len(result) > 40


@pytest.mark.unit
def test_compound_items_use_raw_hex_override():
    fields = build_cat062_minimal_fields()
    fields["position_type"] = 0
    fields["aircraft_derived_data"] = {"include": 1, "raw_hex": "AABBCC"}
    result = run_encode_cat062_datablock(fields)
    assert b"\xaa\xbb\xcc" in result
