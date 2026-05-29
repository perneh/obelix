"""Tests for Cat016 encoding — INCS configuration reports."""

import pytest

from tests.support.actions.encoding import run_encode_cat016_datablock
from tests.support.assertions.encoding import assert_datablock_category, assert_hex_equals
from tests.support.builders.encoding import build_cat016_system_config_fields


@pytest.mark.unit
def test_system_config_encodes_expected_hex():
    fields = build_cat016_system_config_fields()
    result = run_encode_cat016_datablock(fields)
    assert_datablock_category(result, 16)
    assert_hex_equals(result, "10001CB780010101004000010001000A001429F49F4A0CCCCCCD0064")
