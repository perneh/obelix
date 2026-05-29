"""Live API integration tests against a running Obelix instance."""

import pytest

from tests.support.actions.http import run_health_check, run_list_categories
from tests.support.assertions.http import assert_categories_include_category, assert_health_ok


@pytest.mark.integration
@pytest.mark.live
def test_health_returns_ok(live_http_client):
    result = run_health_check(live_http_client)
    assert_health_ok(result)


@pytest.mark.integration
@pytest.mark.live
def test_categories_include_cat034_when_server_running(live_http_client):
    categories = run_list_categories(live_http_client)
    assert_categories_include_category(categories, 34)
