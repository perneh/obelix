"""Tests for Cat240 encoding and registry round-trip."""

import pytest

from app.asterix.categories.cat240 import Cat240
from app.asterix.registry import encode_message, encode_message_hex
from tests.support.assertions.encoding import (
    assert_datablock_category,
    assert_hex_matches_bytes,
    assert_length_field_matches,
)
from tests.support.builders.encoding import (
    build_cat240_video_radial_fields,
    build_cat240_video_summary_fields,
)


@pytest.mark.unit
def test_video_summary_datablock():
    fields = build_cat240_video_summary_fields()
    result = Cat240.encode_datablock(fields)
    assert_datablock_category(result, 240)
    assert_length_field_matches(result)


@pytest.mark.unit
def test_video_radial_datablock():
    fields = build_cat240_video_radial_fields()
    result = Cat240.encode_datablock(fields)
    assert_datablock_category(result, 240)
    assert_length_field_matches(result)
    assert len(result) > 20


@pytest.mark.unit
def test_registry_hex_matches_raw_bytes():
    fields = build_cat240_video_radial_fields()
    hex_value = encode_message_hex(240, fields)
    raw = encode_message(240, fields)
    assert_hex_matches_bytes(hex_value, raw)
