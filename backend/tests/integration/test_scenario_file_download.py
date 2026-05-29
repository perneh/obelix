"""Scenario file download API tests."""

import pytest


@pytest.mark.integration
def test_download_saved_scenario_file(api_client):
    payload = {
        "id": "edit-me",
        "name": "Edit me",
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
    save = api_client.post("/api/saved-scenarios", json=payload)
    assert save.status_code == 200

    response = api_client.get("/api/saved-scenarios/edit-me/file")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "attachment" in response.headers.get("content-disposition", "")
    body = response.json()
    assert body["id"] == "edit-me"
    assert len(body["steps"]) == 1
