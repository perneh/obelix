"""Integration tests for per-category send endpoints."""

import pytest

from tests.support.builders.encoding import build_cat034_north_marker_fields


@pytest.mark.integration
def test_openapi_exposes_category_send_paths(api_client):
    schema = api_client.get("/openapi.json").json()
    paths = schema["paths"]

    for category in (15, 16, 21, 34, 48, 62, 65, 240):
        assert f"/api/send/{category}" in paths
        post = paths[f"/api/send/{category}"]["post"]
        assert post["tags"] == ["send"]
        assert f"Cat {category:03d}" in post["summary"]


@pytest.mark.integration
def test_openapi_category_send_schemas_have_examples(api_client):
    schema = api_client.get("/openapi.json").json()
    components = schema["components"]["schemas"]

    cat034 = components["Cat034SendRequest"]
    assert "examples" in cat034
    assert cat034["examples"][0]["fields"]["message_type"] == 1
    assert "Cat034Fields" in components


@pytest.mark.integration
def test_send_cat034_via_category_endpoint(api_client):
    fields = build_cat034_north_marker_fields(sac=1, sic=2)
    response = api_client.post(
        "/api/send/34",
        json={
            "fields": fields,
            "host": "127.0.0.1",
            "port": 9,
            "protocol": "udp",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["bytes_sent"] == 7
    assert body["protocol"] == "udp"


@pytest.mark.integration
def test_send_unknown_category_path_not_registered(api_client):
    response = api_client.post(
        "/api/send/199",
        json={"fields": {}, "host": "127.0.0.1", "port": 9, "protocol": "udp"},
    )
    # No route for cat 199; with the frontend mount, Starlette may answer 405 instead of 404.
    assert response.status_code in {404, 405}
