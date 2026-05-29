"""Regression — static frontend."""

import pytest

from tests.support.actions.regression_http import get_text


@pytest.mark.regression
def test_frontend(address, port):
    assert "Obelix" in get_text(address, port, "/")
