"""Scenario validate API tests."""

import pytest


def _minimal_scenario() -> dict:
    return {
        "id": "test-import",
        "name": "Import test",
        "transport": {"host": "127.0.0.1", "port": 8600, "protocol": "udp"},
        "loop_count": 1,
        "interval_ms": 1000,
        "steps": [
            {
                "id": "step-1",
                "name": "Cat 34",
                "message": {"category": 34, "fields": {"data_source": {"sac": 1, "sic": 1}}},
                "delay_ms": 0,
                "repeat": 1,
            }
        ],
    }


@pytest.mark.integration
def test_validate_scenario_accepts_minimal_payload(api_client):
    response = api_client.post("/api/scenarios/validate", json=_minimal_scenario())
    assert response.status_code == 200
    assert response.json()["id"] == "test-import"


@pytest.mark.integration
def test_validate_scenario_rejects_empty_steps(api_client):
    payload = _minimal_scenario()
    payload["steps"] = []
    response = api_client.post("/api/scenarios/validate", json=payload)
    assert response.status_code == 400


@pytest.mark.integration
def test_validate_scenario_rejects_unknown_category(api_client):
    payload = _minimal_scenario()
    payload["steps"][0]["message"]["category"] = 199
    response = api_client.post("/api/scenarios/validate", json=payload)
    assert response.status_code == 400
