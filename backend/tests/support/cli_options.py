"""Pure resolvers for pytest CLI target options."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import urlparse


DEFAULT_ADDRESS = "localhost"
DEFAULT_PORT = 8000
ENV_ADDRESS = "TEST_ADDRESS"
ENV_PORT = "TEST_PORT"
ENV_URL = "TEST_URL"


@dataclass(frozen=True)
class TargetConfig:
    address: str
    port: int
    base_url: str
    source: str


def _validate_port(port: int) -> int:
    if port < 1 or port > 65535:
        raise ValueError(f"Port must be between 1 and 65535, got {port}")
    return port


def _validate_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"URL must use http or https scheme, got {url!r}")
    if not parsed.netloc:
        raise ValueError(f"URL must include a host, got {url!r}")
    return url.rstrip("/")


def resolve_target(
    *,
    address: str | None = None,
    port: int | None = None,
    url: str | None = None,
) -> TargetConfig:
    """Resolve test target with precedence: CLI url > CLI address+port > env > defaults."""
    env_url = os.environ.get(ENV_URL)
    env_address = os.environ.get(ENV_ADDRESS)
    env_port = os.environ.get(ENV_PORT)

    if url:
        base = _validate_url(url)
        parsed = urlparse(base)
        host = parsed.hostname or DEFAULT_ADDRESS
        resolved_port = parsed.port or (443 if parsed.scheme == "https" else 80)
        return TargetConfig(
            address=host,
            port=resolved_port,
            base_url=base,
            source="cli --url",
        )

    if env_url:
        base = _validate_url(env_url)
        parsed = urlparse(base)
        host = parsed.hostname or DEFAULT_ADDRESS
        resolved_port = parsed.port or (443 if parsed.scheme == "https" else 80)
        return TargetConfig(
            address=host,
            port=resolved_port,
            base_url=base,
            source=f"env {ENV_URL}",
        )

    resolved_address = address or env_address or DEFAULT_ADDRESS

    if port is not None:
        resolved_port = _validate_port(port)
        source = "cli --address/--port"
    elif env_port is not None:
        try:
            resolved_port = _validate_port(int(env_port))
        except ValueError as exc:
            raise ValueError(f"{ENV_PORT} must be an integer, got {env_port!r}") from exc
        source = f"env {ENV_ADDRESS}/{ENV_PORT}"
    else:
        resolved_port = DEFAULT_PORT
        if address:
            source = "cli --address"
        elif env_address:
            source = f"env {ENV_ADDRESS}"
        else:
            source = "default"

    base = f"http://{resolved_address}:{resolved_port}"
    return TargetConfig(
        address=resolved_address,
        port=resolved_port,
        base_url=base,
        source=source,
    )
