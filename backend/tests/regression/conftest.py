"""Regression tests target a running Obelix instance via httpx (address + port)."""

from __future__ import annotations

import logging

import httpx
import pytest

from tests.support.cli_options import TargetConfig
from tests.support.udp_target import resolve_udp_host

logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def address(target: TargetConfig) -> str:
    return target.address


@pytest.fixture(scope="session")
def port(target: TargetConfig) -> int:
    return target.port


@pytest.fixture(scope="session")
def udp_host(address: str) -> str:
    """UDP destination as seen from the Obelix server (often host.docker.internal)."""
    return resolve_udp_host(api_address=address)


@pytest.fixture(scope="session", autouse=True)
def _require_reachable_server(target: TargetConfig) -> None:
    try:
        response = httpx.get(f"{target.base_url}/api/categories", timeout=10.0)
        if response.status_code >= 500:
            pytest.skip(f"Server at {target.base_url} returned {response.status_code}")
    except httpx.ConnectError:
        pytest.skip(f"Server at {target.base_url} is not reachable")
    except httpx.TimeoutException:
        pytest.skip(f"Server at {target.base_url} timed out")

    logger.info("Regression target: %s:%s", target.address, target.port)
