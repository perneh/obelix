"""In-process API integration tests — functional."""

import pytest

from tests.support.actions.http import (
    run_encode_message,
    run_get_category_detail,
    run_get_category_help,
    run_get_frontend,
    run_list_categories,
    run_load_configuration,
    run_save_configuration,
)
from tests.support.assertions.http import (
    assert_category_detail,
    assert_frontend_contains,
    assert_json_field,
    assert_status_not_found,
    assert_status_ok,
)
from tests.support.builders.api import build_configuration_payload, build_encode_request
from tests.support.builders.encoding import build_cat034_north_marker_fields, build_cat048_plot_fields


@pytest.mark.integration
def test_list_categories_returns_cat034(api_client):
    result = run_list_categories(api_client)
    categories = {item["category"] for item in result}
    assert 34 in categories


@pytest.mark.integration
def test_get_category_detail_includes_fields(api_client):
    result = run_get_category_detail(api_client, 34)
    assert_status_ok(result)
    assert_category_detail(result.json, category_id=34)


@pytest.mark.integration
def test_get_category_help_returns_markdown(api_client):
    result = run_get_category_help(api_client, 34)
    assert_status_ok(result)
    assert_json_field(result, "category", 34)
    assert_json_field(result, "format", "markdown")
    assert "Monoradar Service Messages" in result.json["content"]


@pytest.mark.integration
def test_encode_north_marker_returns_expected_hex(api_client):
    fields = build_cat034_north_marker_fields(sac=1, sic=2)
    payload = build_encode_request(category=34, fields=fields)
    result = run_encode_message(api_client, payload)
    assert_status_ok(result)
    assert_json_field(result, "hex", "220007C0010102")
    assert_json_field(result, "length", 7)


@pytest.mark.integration
def test_encode_unknown_category_returns_not_found(api_client):
    payload = build_encode_request(category=199, fields={})
    result = run_encode_message(api_client, payload)
    assert_status_not_found(result)


@pytest.mark.integration
def test_save_and_load_local_configuration(api_client):
    fields = build_cat034_north_marker_fields(sac=1, sic=1)
    payload = build_configuration_payload(
        config_id="test-local",
        name="Test Local",
        category=34,
        fields=fields,
        scope="local",
    )
    saved = run_save_configuration(api_client, payload)
    assert_status_ok(saved)

    loaded = run_load_configuration(api_client, "local:cat034:test-local")
    assert_status_ok(loaded)
    assert_json_field(loaded, "name", "Test Local")


@pytest.mark.integration
def test_save_shared_configuration(api_client):
    fields = build_cat048_plot_fields()
    payload = build_configuration_payload(
        config_id="test-shared-plot",
        name="Shared Plot",
        category=48,
        fields=fields,
        scope="shared",
    )
    saved = run_save_configuration(api_client, payload)
    assert_status_ok(saved)
    assert_json_field(saved, "scope", "shared")


@pytest.mark.integration
def test_frontend_is_served(api_client):
    result = run_get_frontend(api_client)
    assert_frontend_contains(result, "Obelix")
