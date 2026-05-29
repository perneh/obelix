"""Tests for ASTERIX category registry — functional."""

import pytest

from tests.support.actions.encoding import run_get_category, run_list_categories
from tests.support.assertions.encoding import assert_categories_include


@pytest.mark.unit
def test_unknown_category_raises_key_error():
    with pytest.raises(KeyError):
        run_get_category(999)


@pytest.mark.unit
def test_list_includes_cat034_and_cat048():
    categories = run_list_categories()
    category_ids = {definition.category for definition in categories}
    assert_categories_include(category_ids, {15, 16, 34, 48, 62})
