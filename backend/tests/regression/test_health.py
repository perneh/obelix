"""Regression — API health and category registry."""

import pytest

from tests.support.actions.regression_http import get
from tests.support.builders.regression import IMPLEMENTED_CATEGORIES


@pytest.mark.regression
def test_api_health(address, port):
    categories = get(address, port, "/api/categories")
    registered = {item["category"] for item in categories}

    assert len(categories) == len(IMPLEMENTED_CATEGORIES)
    for category in IMPLEMENTED_CATEGORIES:
        assert category in registered
