"""Unit tests for Link 16 registry and JREAP encoding."""

import pytest

from app.link16.jreap import unwrap_jreap, wrap_jreap
from app.link16.messages.j3 import J32
from app.link16.registry import encode_message, list_messages


@pytest.mark.unit
def test_list_messages_includes_core_j_series():
    series = {message.j_series for message in list_messages()}
    assert "J2.2" in series
    assert "J3.2" in series
    assert "J12.0" in series
    assert len(series) >= 30


@pytest.mark.unit
def test_j32_encode_wraps_jreap():
    fields = J32.definition().fields
    values = {}
    for field in fields:
        values[field.id] = field.default

    packet = encode_message("J3.2", values)
    series, source_ju, npg, payload = unwrap_jreap(packet)
    assert series == "J3.2"
    assert source_ju == values["source_ju"]
    assert npg == values["npg"]
    assert len(payload) > 0


@pytest.mark.unit
def test_jreap_round_trip():
    payload = b"\x03\x02\x01\x02track"
    packet = wrap_jreap("J3.2", 10001, 2, payload)
    assert unwrap_jreap(packet) == ("J3.2", 10001, 2, payload)
