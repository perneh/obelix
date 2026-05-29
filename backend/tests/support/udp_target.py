"""Resolve UDP target host for regression send tests."""

from __future__ import annotations

import os
import platform
import socket


def resolve_udp_host(*, api_address: str) -> str:
    """Host the Obelix server should send UDP to so pytest receives it on this machine."""
    configured = os.environ.get("TEST_UDP_HOST")
    if configured:
        return configured

    if api_address not in {"localhost", "127.0.0.1", "::1"}:
        return api_address

    if platform.system() == "Darwin":
        # Obelix usually runs in Docker Desktop; container localhost != host.
        return "host.docker.internal"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("8.8.8.8", 80))
            return probe.getsockname()[0]
    except OSError:
        return "127.0.0.1"
