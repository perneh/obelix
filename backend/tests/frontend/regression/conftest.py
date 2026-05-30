"""Frontend regression tests require a reachable Obelix web server."""

from __future__ import annotations

import logging

import httpx
import pytest

from tests.support.cli_options import TargetConfig

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def address(target: TargetConfig) -> str:
    return target.address


@pytest.fixture(scope="session")
def port(target: TargetConfig) -> int:
    return target.port


@pytest.fixture(scope="session", autouse=True)
def _require_reachable_server(target: TargetConfig) -> None:
    try:
        response = httpx.get(f"{target.base_url}/", timeout=10.0)
        if response.status_code >= 500:
            pytest.skip(f"Server at {target.base_url} returned {response.status_code}")
    except httpx.ConnectError:
        pytest.skip(f"Server at {target.base_url} is not reachable")
    except httpx.TimeoutException:
        pytest.skip(f"Server at {target.base_url} timed out")

    logger.info("Frontend regression target: %s", target.base_url)
