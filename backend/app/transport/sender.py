"""UDP and TCP transport for ASTERIX messages."""

from __future__ import annotations

import asyncio
import socket
from enum import Enum


class TransportProtocol(str, Enum):
    UDP = "udp"
    TCP = "tcp"


async def send_udp(data: bytes, host: str, port: int) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _send_udp_sync, data, host, port)


def _send_udp_sync(data: bytes, host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(data, (host, port))


async def send_tcp(data: bytes, host: str, port: int) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _send_tcp_sync, data, host, port)


def _send_tcp_sync(data: bytes, host: str, port: int) -> None:
    with socket.create_connection((host, port), timeout=5.0) as sock:
        sock.sendall(data)
