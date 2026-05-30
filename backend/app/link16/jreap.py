"""JREAP-C simple envelope for Link 16 simulation over IP."""

from __future__ import annotations

import struct

MAGIC = b"JREA"
VERSION = 1
HEADER_SIZE = 16
SERIES_SIZE = 8


def wrap_jreap(j_series: str, source_ju: int, npg: int, payload: bytes) -> bytes:
    """Wrap a J-message payload in a JREAP-C simple header for UDP/TCP transport."""
    series_bytes = j_series.encode("ascii")
    if len(series_bytes) > SERIES_SIZE:
        raise ValueError(f"J-series label too long: {j_series}")

    header = struct.pack(
        ">4sBBHII",
        MAGIC,
        VERSION,
        len(series_bytes),
        npg & 0xFFFF,
        source_ju & 0xFFFFFFFF,
        len(payload) & 0xFFFFFFFF,
    )
    series_padded = series_bytes.ljust(SERIES_SIZE, b"\x00")
    return header + series_padded + payload


def unwrap_jreap(data: bytes) -> tuple[str, int, int, bytes]:
    """Parse JREAP-C simple header (for tests and verification)."""
    if len(data) < HEADER_SIZE + SERIES_SIZE:
        raise ValueError("JREAP packet too short")
    magic, version, series_len, npg, source_ju, payload_len = struct.unpack(">4sBBHII", data[:HEADER_SIZE])
    if magic != MAGIC:
        raise ValueError("Invalid JREAP magic")
    if version != VERSION:
        raise ValueError(f"Unsupported JREAP version {version}")
    series = data[HEADER_SIZE : HEADER_SIZE + SERIES_SIZE][:series_len].decode("ascii")
    payload_start = HEADER_SIZE + SERIES_SIZE
    payload = data[payload_start : payload_start + payload_len]
    return series, source_ju, npg, payload
