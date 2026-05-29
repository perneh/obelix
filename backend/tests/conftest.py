"""Shared pytest fixtures and CLI options."""

from __future__ import annotations

import logging

import httpx
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.support.cli_options import TargetConfig, resolve_target
from tests.support.logging_config import configure_test_logging

logger = logging.getLogger(__name__)


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption("--address", action="store", default=None, help="Host under test")
    parser.addoption("--port", action="store", type=int, default=None, help="Port under test")
    parser.addoption("--url", action="store", default=None, help="Base URL under test")


def pytest_configure(config: pytest.Config) -> None:
    log_cli_level = config.getoption("log_cli_level", default=None)
    configure_test_logging(str(log_cli_level) if log_cli_level else None)


@pytest.fixture(scope="session")
def target(pytestconfig: pytest.Config) -> TargetConfig:
    resolved = resolve_target(
        address=pytestconfig.getoption("--address"),
        port=pytestconfig.getoption("--port"),
        url=pytestconfig.getoption("--url"),
    )
    logger.info(
        "Test target: %s (source: %s)",
        resolved.base_url,
        resolved.source,
    )
    logger.debug(
        "Resolved address=%s port=%s base_url=%s",
        resolved.address,
        resolved.port,
        resolved.base_url,
    )
    return resolved


@pytest.fixture
def api_client(tmp_path, monkeypatch) -> TestClient:
    """In-process FastAPI client with isolated template/scenario storage."""
    from app.core.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OBELIX_SHARED_CONFIGURATIONS_DIR", str(tmp_path / "configurations"))
    monkeypatch.setenv("OBELIX_LOCAL_CONFIGURATIONS_DIR", str(tmp_path / "local-configurations"))
    monkeypatch.setenv("OBELIX_SCENARIOS_DIR", str(tmp_path / "scenarios"))
    logger.debug("Created in-process TestClient with tmp storage at %s", tmp_path)
    return TestClient(create_app())


@pytest.fixture(scope="session")
def live_http_client(target: TargetConfig):
    """HTTP client against a running Obelix instance; skips if unreachable."""
    client = httpx.Client(base_url=target.base_url, timeout=5.0)
    try:
        response = client.get("/api/categories")
        if response.status_code >= 500:
            pytest.skip(f"Server at {target.base_url} returned {response.status_code}")
    except httpx.ConnectError:
        pytest.skip(f"Server at {target.base_url} is not reachable")
    except httpx.TimeoutException:
        pytest.skip(f"Server at {target.base_url} timed out")

    logger.info("Live HTTP client connected to %s", target.base_url)
    yield client
    client.close()
