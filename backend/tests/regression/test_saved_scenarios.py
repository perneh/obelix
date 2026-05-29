"""Regression — saved scenarios API."""

import json
import uuid

import pytest

from tests.support.actions.regression_http import delete, get, get_text, post
from tests.support.builders.scenarios import build_minimal_scenario
from tests.support.udp_listener import udp_listener


@pytest.mark.regression
def test_saved_scenarios(address, port):
    scenario_id = f"reg-{uuid.uuid4().hex[:8]}"
    payload = build_minimal_scenario(scenario_id)
    payload["name"] = "Regression saved scenario"

    assert post(address, port, "/api/saved-scenarios", payload, scope="local")["id"] == scenario_id
    assert scenario_id in {item["id"] for item in get(address, port, "/api/saved-scenarios")}
    assert get(address, port, f"/api/saved-scenarios/{scenario_id}")["name"] == "Regression saved scenario"
    assert get(address, port, f"/api/saved-scenarios/{scenario_id}")["id"] == scenario_id

    file_body = json.loads(get_text(address, port, f"/api/saved-scenarios/{scenario_id}/file"))
    assert file_body["id"] == scenario_id
    assert file_body["name"] == "Regression saved scenario"

    assert delete(address, port, f"/api/saved-scenarios/{scenario_id}")["status"] == "deleted"


@pytest.mark.regression
def test_saved_scenarios_send_udp(address, port, udp_host):
    step_message = build_minimal_scenario()["steps"][0]["message"]
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
