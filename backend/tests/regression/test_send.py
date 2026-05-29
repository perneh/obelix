"""Regression — encode and send API."""

import pytest

from tests.support.actions.regression_http import post, status
from tests.support.builders.api import build_encode_request
from tests.support.builders.encoding import build_cat034_north_marker_fields


@pytest.mark.regression
def test_encode(address, port):
    encoded = post(
        address,
        port,
        "/api/encode",
        build_encode_request(category=34, fields=build_cat034_north_marker_fields()),
    )
    assert encoded["hex"] == "220007C0010102"
    assert encoded["length"] == 7
    assert encoded["category"] == 34


@pytest.mark.regression
def test_send(address, port):
    payload = {
        **build_encode_request(category=34, fields=build_cat034_north_marker_fields()),
        "host": "127.0.0.1",
        "port": 8600,
        "protocol": "udp",
    }
    send_status = status(address, port, "POST", "/api/send", json=payload)
    assert send_status in {200, 502}

    if send_status == 200:
        result = post(address, port, "/api/send", payload)
        assert result["success"] is True
        assert result["bytes_sent"] == 7
        assert result["host"] == "127.0.0.1"
        assert result["port"] == 8600
        assert result["protocol"] == "udp"
    else:
        assert send_status == 502
