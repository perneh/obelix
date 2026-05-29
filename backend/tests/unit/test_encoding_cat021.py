"""Tests for Cat021 encoding and registry round-trip."""

import pytest

from app.asterix.categories.cat021 import Cat021
from app.asterix.registry import encode_message, encode_message_hex
from tests.support.assertions.encoding import (
    assert_datablock_category,
    assert_hex_matches_bytes,
    assert_length_field_matches,
)
from tests.support.builders.encoding import build_cat021_adsb_fields


@pytest.mark.unit
def test_adsb_report_datablock_length_field_matches():
    fields = build_cat021_adsb_fields()
    result = Cat021.encode_datablock(fields)
    assert_datablock_category(result, 21)
    assert_length_field_matches(result)


@pytest.mark.unit
def test_registry_hex_matches_raw_bytes():
    fields = build_cat021_adsb_fields()
    hex_value = encode_message_hex(21, fields)
    raw = encode_message(21, fields)
    assert_hex_matches_bytes(hex_value, raw)


@pytest.mark.unit
def test_minimal_anonymous_report_encodes():
    fields = build_cat021_adsb_fields(
        target_address="000001",
        atp=3,
        include_mode3a=0,
        include_target_identification=0,
    )
    result = Cat021.encode_datablock(fields)
    assert len(result) >= 6
    assert_datablock_category(result, 21)
