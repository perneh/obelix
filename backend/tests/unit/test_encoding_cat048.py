"""Tests for Cat048 encoding and registry round-trip — functional."""

import pytest

from tests.support.actions.encoding import (
    run_encode_cat048_datablock,
    run_encode_hex_via_registry,
    run_encode_via_registry,
)
from tests.support.assertions.encoding import (
    assert_datablock_category,
    assert_hex_matches_bytes,
    assert_length_field_matches,
)
from tests.support.builders.encoding import build_cat048_plot_fields, build_cat048_registry_fields


@pytest.mark.unit
def test_basic_plot_datablock_length_field_matches():
    fields = build_cat048_plot_fields()
    result = run_encode_cat048_datablock(fields)
    assert_datablock_category(result, 48)
    assert_length_field_matches(result)


@pytest.mark.unit
def test_registry_hex_matches_raw_bytes():
    fields = build_cat048_registry_fields()
    hex_value = run_encode_hex_via_registry(48, fields)
    raw = run_encode_via_registry(48, fields)
    assert_hex_matches_bytes(hex_value, raw)
