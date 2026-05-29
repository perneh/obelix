"""Regression — built-in scenario templates API."""

import pytest

from tests.support.actions.regression_http import get, post
from tests.support.builders.scenarios import BALTIC_TEMPLATE_IDS
from tests.support.udp_listener import udp_listener


@pytest.mark.regression
def test_scenario_templates_catalog(address, port):
    assert {item["id"] for item in get(address, port, "/api/scenario-templates")} == BALTIC_TEMPLATE_IDS


@pytest.mark.regression
def test_scenario_template_jas(address, port):
    template = get(address, port, "/api/scenario-templates/jas-bromma-visby")
    assert template["id"] == "jas-bromma-visby"
    assert template["name"] == "JAS 39 – Bromma → Visby"
    assert len(template["steps"]) == 10


@pytest.mark.regression
def test_scenario_template_build(address, port):
    built = post(address, port, "/api/scenario-templates/jas-bromma-visby/build", {"ticks": 5})
    assert built["template_id"] == "jas-bromma-visby"

    motion_step = next(
        step for step in built["steps"] if step.get("motion") and step["motion"].get("enabled")
    )
    assert motion_step["motion"]["ticks"] == 5


@pytest.mark.regression
def test_scenario_templates_send_udp(address, port, udp_host):
    step_message = get(address, port, "/api/scenario-templates/jas-bromma-visby")["steps"][0]["message"]
    encode_payload = {"message": step_message}
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
