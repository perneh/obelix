"""Regression — Cat 034."""

import pytest

from tests.support.actions.regression_http import get, post
from tests.support.builders.api import build_encode_request
from tests.support.builders.regression import fields_for_category
from tests.support.udp_listener import udp_listener


@pytest.mark.regression
def test_cat034(address, port):
    category = 34
    fields = fields_for_category(category)

    detail = get(address, port, f"/api/categories/{category}")
    assert detail["category"] == category
    assert len(detail["fields"]) > 0
    assert len(detail["uap"]) > 0

    help_body = get(address, port, f"/api/categories/{category}/help")
    assert help_body["category"] == category
    assert help_body["format"] == "markdown"
    assert f"Category {category:03d}" in help_body["content"]

    encoded = post(address, port, "/api/encode", build_encode_request(category=category, fields=fields))
    assert encoded["category"] == category
    assert encoded["length"] > 0
    assert len(encoded["hex"]) == encoded["length"] * 2


@pytest.mark.regression
def test_cat034_send_udp(address, port, udp_host):
    category = 34
    fields = fields_for_category(category)
    encode_payload = build_encode_request(category=category, fields=fields)
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
