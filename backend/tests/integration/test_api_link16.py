"""Integration tests for Link 16 API."""

import pytest


@pytest.mark.integration
def test_list_link16_messages(api_client):
    messages = api_client.get("/api/link16/messages").json()
    series = {item["j_series"] for item in messages}
    assert "J3.2" in series
    assert "J2.2" in series
    assert len(messages) >= 30


@pytest.mark.integration
def test_get_j32_detail(api_client):
    detail = api_client.get("/api/link16/messages/J3-2").json()
    assert detail["j_series"] == "J3.2"
    assert detail["name"] == "Air Track"
    assert len(detail["fields"]) > 0
    assert len(detail["word_layout"]) > 0


@pytest.mark.integration
def test_encode_j32(api_client):
    detail = api_client.get("/api/link16/messages/J3-2").json()
    fields = {}
    for field in detail["fields"]:
        fields[field["id"]] = field["default"]

    result = api_client.post("/api/link16/encode", json={"message": {"j_series": "J3.2", "fields": fields}}).json()
    assert result["j_series"] == "J3.2"
    assert result["length"] > 0
    assert result["hex"].startswith("4A524541")  # JREA


@pytest.mark.integration
def test_openapi_link16_send_paths(api_client):
    schema = api_client.get("/openapi.json").json()
    paths = schema["paths"]
    assert "/api/link16/send/J3-2" in paths
    assert "/api/link16/messages" in paths


@pytest.mark.integration
def test_send_j32_via_category_endpoint(api_client):
    detail = api_client.get("/api/link16/messages/J3-2").json()
    fields = {field["id"]: field["default"] for field in detail["fields"]}

    response = api_client.post(
        "/api/link16/send/J3-2",
        json={"fields": fields, "host": "127.0.0.1", "port": 9, "protocol": "udp"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["j_series"] == "J3.2"
    assert body["bytes_sent"] > 0
