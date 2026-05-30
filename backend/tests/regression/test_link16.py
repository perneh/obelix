"""Regression — Link 16 J-message API."""

import pytest

from tests.support.actions.regression_http import get, post
from tests.support.udp_listener import udp_listener


def _default_fields(address, port, j_series: str) -> dict:
    slug = j_series.replace(".", "-")
    detail = get(address, port, f"/api/link16/messages/{slug}")
    return {field["id"]: field["default"] for field in detail["fields"]}


@pytest.mark.regression
def test_link16_messages(address, port):
    messages = get(address, port, "/api/link16/messages")
    series = {item["j_series"] for item in messages}
    assert len(messages) >= 30
    assert "J3.2" in series
    assert "J2.2" in series


@pytest.mark.regression
def test_link16_encode_j32(address, port):
    fields = _default_fields(address, port, "J3.2")
    encoded = post(address, port, "/api/link16/encode", {"message": {"j_series": "J3.2", "fields": fields}})
    assert encoded["j_series"] == "J3.2"
    assert encoded["length"] > 0
    assert encoded["hex"].startswith("4A524541")


@pytest.mark.regression
def test_link16_send_j32_udp(address, port, udp_host):
    fields = _default_fields(address, port, "J3.2")
    encoded = post(address, port, "/api/link16/encode", {"message": {"j_series": "J3.2", "fields": fields}})

    with udp_listener() as (listen_port, sock):
        sent = post(
            address,
            port,
            "/api/link16/send/J3-2",
            {"fields": fields, "host": udp_host, "port": listen_port, "protocol": "udp"},
        )
        assert sent["success"] is True
        assert sent["j_series"] == "J3.2"
        assert sent["bytes_sent"] == encoded["length"]
        assert sock.recvfrom(65535)[0].hex().upper() == encoded["hex"]
