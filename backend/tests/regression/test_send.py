"""Regression — encode and send API."""

import pytest

from tests.support.actions.regression_http import get, post
from tests.support.builders.api import build_category_send_request, build_encode_request
from tests.support.builders.encoding import build_cat034_north_marker_fields
from tests.support.builders.regression import IMPLEMENTED_CATEGORIES
from tests.support.udp_listener import udp_listener


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
def test_openapi_category_send_paths(address, port):
    schema = get(address, port, "/openapi.json")
    paths = schema["paths"]

    for category in IMPLEMENTED_CATEGORIES:
        path = f"/api/send/{category}"
        assert path in paths
        operation = paths[path]["post"]
        assert operation["tags"] == ["send"]
        assert f"Cat {category:03d}" in operation["summary"]


@pytest.mark.regression
def test_send_udp(address, port, udp_host):
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
        assert sent["bytes_sent"] == 7
        assert sent["host"] == udp_host
        assert sent["port"] == listen_port
        assert sock.recvfrom(65535)[0].hex().upper() == encoded["hex"]


@pytest.mark.regression
def test_send_category_udp(address, port, udp_host):
    fields = build_cat034_north_marker_fields()
    encoded = post(address, port, "/api/encode", build_encode_request(category=34, fields=fields))

    with udp_listener() as (listen_port, sock):
        sent = post(
            address,
            port,
            "/api/send/34",
            build_category_send_request(fields=fields, host=udp_host, port=listen_port, protocol="udp"),
        )
        assert sent["success"] is True
        assert sent["protocol"] == "udp"
        assert sent["bytes_sent"] == encoded["length"]
        assert sent["host"] == udp_host
        assert sent["port"] == listen_port
        assert sock.recvfrom(65535)[0].hex().upper() == encoded["hex"]
