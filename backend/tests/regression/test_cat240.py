"""Regression — Cat 240."""

import pytest

from tests.support.actions.regression_http import get, post
from tests.support.builders.api import build_encode_request
from tests.support.builders.regression import cat240_summary_fields, fields_for_category


@pytest.mark.regression
def test_cat240_radial(address, port):
    category = 240
    fields = fields_for_category(category)

    detail = get(address, port, f"/api/categories/{category}")
    assert detail["category"] == category
    assert len(detail["fields"]) > 0
    assert len(detail["uap"]) > 0

    help_body = get(address, port, f"/api/categories/{category}/help")
    assert help_body["category"] == category
    assert help_body["format"] == "markdown"
    assert f"Category {category:03d}" in help_body["content"]

    encoded = post(address, port, "/api/encode", build_encode_request(category=category, fields=fields))
    assert encoded["category"] == category
    assert encoded["length"] > 0
    assert len(encoded["hex"]) == encoded["length"] * 2


@pytest.mark.regression
def test_cat240_summary(address, port):
    encoded = post(
        address,
        port,
        "/api/encode",
        build_encode_request(category=240, fields=cat240_summary_fields()),
    )
    assert encoded["category"] == 240
    assert encoded["length"] > 0
    assert len(encoded["hex"]) == encoded["length"] * 2
