"""Regression — configurations API."""

import uuid

import pytest

from tests.support.actions.regression_http import delete, get, post
from tests.support.builders.api import build_configuration_payload, build_encode_request
from tests.support.builders.encoding import build_cat034_north_marker_fields
from tests.support.udp_listener import udp_listener


@pytest.mark.regression
def test_configurations(address, port):
    slug = f"reg-{uuid.uuid4().hex[:8]}"
    config_id = f"local:cat034:{slug}"
    payload = build_configuration_payload(
        config_id=slug,
        name="Regression config",
        category=34,
        fields=build_cat034_north_marker_fields(sac=1, sic=1),
        scope="local",
    )

    saved = post(address, port, "/api/configurations", payload)
    assert saved["id"] == slug
    assert saved["scope"] == "local"

    listed = get(address, port, "/api/configurations", category=34, scope="local")
    assert slug in {item["id"] for item in listed}

    assert get(address, port, f"/api/configurations/{config_id}")["name"] == "Regression config"
    assert get(address, port, f"/api/configurations/{config_id}")["message"] == payload["message"]

    assert delete(address, port, f"/api/configurations/{config_id}")["status"] == "deleted"


@pytest.mark.regression
def test_configurations_send_udp(address, port, udp_host):
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
