"""Regression — static frontend."""

import pytest

from tests.support.actions.regression_http import get_text, post
from tests.support.builders.api import build_encode_request
from tests.support.builders.encoding import build_cat034_north_marker_fields
from tests.support.udp_listener import udp_listener


@pytest.mark.regression
def test_frontend(address, port):
    assert "Obelix" in get_text(address, port, "/")


@pytest.mark.regression
def test_frontend_send_udp(address, port, udp_host):
    encode_payload = build_encode_request(category=34, fields=build_cat034_north_marker_fields())
    encoded = post(address, port, "/api/encode", encode_payload)

    with udp_listener() as (listen_port, sock):
        sent = post(
            address,
            port,
            "/api/send",
            {**encode_payload, "host": udp_host, "port": listen_port, "protocol": "udp"},
        )
        assert sent["success"] is True
        assert sent["protocol"] == "udp"
        assert sent["bytes_sent"] == encoded["length"]
        assert sock.recvfrom(65535)[0].hex().upper() == encoded["hex"]
