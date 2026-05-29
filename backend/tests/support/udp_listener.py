"""UDP socket helper for regression send verification."""

from __future__ import annotations

import socket
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def udp_listener(*, host: str = "0.0.0.0", timeout: float = 2.0) -> Iterator[tuple[int, socket.socket]]:
    """Bind an ephemeral UDP port and yield (port, socket)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, 0))
    sock.settimeout(timeout)
    listen_port = sock.getsockname()[1]
    try:
        yield listen_port, sock
    finally:
        sock.close()
