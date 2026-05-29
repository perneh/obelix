"""Tests for Cat065 encoding and registry round-trip."""

import pytest

from app.asterix.categories.cat065 import Cat065
from app.asterix.registry import encode_message, encode_message_hex
from tests.support.assertions.encoding import (
    assert_datablock_category,
    assert_hex_matches_bytes,
    assert_length_field_matches,
)
from tests.support.builders.encoding import build_cat065_sdps_status_fields


@pytest.mark.unit
def test_sdps_status_datablock_length_field_matches():
    fields = build_cat065_sdps_status_fields()
    result = Cat065.encode_datablock(fields)
    assert_datablock_category(result, 65)
    assert_length_field_matches(result)


@pytest.mark.unit
def test_registry_hex_matches_raw_bytes():
    fields = build_cat065_sdps_status_fields()
    hex_value = encode_message_hex(65, fields)
    raw = encode_message(65, fields)
    assert_hex_matches_bytes(hex_value, raw)


@pytest.mark.unit
def test_service_status_report_message_type():
    fields = build_cat065_sdps_status_fields(
        message_type=3,
        include_sdps_configuration=0,
        include_service_status_report=1,
        service_status_report=1,
    )
    result = Cat065.encode_datablock(fields)
    assert_datablock_category(result, 65)
    assert len(result) >= 6
