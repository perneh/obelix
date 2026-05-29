"""Regression — API health and category registry."""

import pytest

from tests.support.actions.regression_http import get, post
from tests.support.builders.api import build_encode_request
from tests.support.builders.encoding import build_cat034_north_marker_fields
from tests.support.builders.regression import IMPLEMENTED_CATEGORIES
from tests.support.udp_listener import udp_listener


@pytest.mark.regression
def test_api_health(address, port):
    categories = get(address, port, "/api/categories")
    registered = {item["category"] for item in categories}

    assert len(categories) == len(IMPLEMENTED_CATEGORIES)
    for category in IMPLEMENTED_CATEGORIES:
        assert category in registered


@pytest.mark.regression
def test_health_send_udp(address, port, udp_host):
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
