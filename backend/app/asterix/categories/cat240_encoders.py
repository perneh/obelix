"""Cat 240 helper encoders."""

from __future__ import annotations

from typing import Any

from app.asterix.base import clamp

_AZIMUTH_LSB = 360.0 / (2**16)
_TIME_LSB = 1.0 / 128.0


def encode_data_source(data_source: dict[str, Any]) -> bytes:
    sac = clamp(int(data_source.get("sac", 1)), 0, 255)
    sic = clamp(int(data_source.get("sic", 1)), 0, 255)
    return bytes([sac, sic])


def encode_message_type(message_type: int) -> bytes:
    return bytes([clamp(message_type, 1, 2)])


def encode_video_sequence(sequence: int) -> bytes:
    value = clamp(sequence, 0, 0xFFFFFFFF)
    return bytes(
        [
            (value >> 24) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 8) & 0xFF,
            value & 0xFF,
        ]
    )


def encode_video_summary(text: str) -> bytes:
    payload = str(text).encode("ascii", errors="replace")[:255]
    return bytes([len(payload)]) + payload


def encode_video_header_nano(header: dict[str, Any]) -> bytes:
    start_az = _scale_azimuth(float(header.get("start_az_deg", 0.0)))
    end_az = _scale_azimuth(float(header.get("end_az_deg", 1.0)))
    start_rg = clamp(int(header.get("start_range_cells", 0)), 0, 0xFFFFFFFF)
    cell_dur = clamp(int(header.get("cell_duration_ns", 1000)), 0, 0xFFFFFFFF)
    return (
        _pack_uint16_be(start_az)
        + _pack_uint16_be(end_az)
        + _pack_uint32_be(start_rg)
        + _pack_uint32_be(cell_dur)
    )


def encode_video_header_femto(header: dict[str, Any]) -> bytes:
    start_az = _scale_azimuth(float(header.get("start_az_deg", 0.0)))
    end_az = _scale_azimuth(float(header.get("end_az_deg", 1.0)))
    start_rg = clamp(int(header.get("start_range_cells", 0)), 0, 0xFFFFFFFF)
    cell_dur = clamp(int(header.get("cell_duration_fs", 1_000_000)), 0, 0xFFFFFFFF)
    return (
        _pack_uint16_be(start_az)
        + _pack_uint16_be(end_az)
        + _pack_uint32_be(start_rg)
        + _pack_uint32_be(cell_dur)
    )


def encode_video_resolution(resolution: dict[str, Any]) -> bytes:
    compression = 1 if int(resolution.get("compression", 0)) else 0
    res = clamp(int(resolution.get("resolution", 4)), 1, 6)
    return bytes([(compression << 7) & 0x80, res & 0xFF])


def encode_video_counters(nb_octets: int, nb_cells: int) -> bytes:
    octets = clamp(nb_octets, 0, 0xFFFF)
    cells = clamp(nb_cells, 0, 0xFFFFFF)
    return _pack_uint16_be(octets) + _pack_uint24_be(cells)


def encode_video_block_low(cells_hex: str) -> bytes:
    data = _parse_cells_payload(cells_hex)
    if len(data) % 4 != 0:
        raise ValueError("Video block low: cell payload length must be a multiple of 4 octets")
    num_cells = len(data) // 4
    if num_cells > 255:
        raise ValueError("Video block low: at most 255 cells (REP is one octet)")
    return bytes([num_cells]) + data


def encode_video_block_medium(cells_hex: str) -> bytes:
    data = _parse_cells_payload(cells_hex)
    if len(data) % 64 != 0:
        raise ValueError("Video block medium: cell payload length must be a multiple of 64 octets")
    num_cells = len(data) // 64
    if num_cells > 255:
        raise ValueError("Video block medium: at most 255 cells")
    return bytes([num_cells]) + data


def encode_video_block_high(cells_hex: str) -> bytes:
    data = _parse_cells_payload(cells_hex)
    if len(data) % 256 != 0:
        raise ValueError("Video block high: cell payload length must be a multiple of 256 octets")
    num_cells = len(data) // 256
    if num_cells > 254:
        raise ValueError("Video block high: at most 254 cells per spec")
    return bytes([num_cells]) + data


def encode_time_of_day(seconds: float) -> bytes:
    raw = clamp(int(round(seconds / _TIME_LSB)), 0, 0xFFFFFF)
    return _pack_uint24_be(raw)


def default_video_cells_hex(num_cells: int = 8, amplitude_base: int = 40) -> str:
    """Synthetic low-block cells (32-bit each, amplitude in least significant octet)."""
    parts: list[str] = []
    for index in range(num_cells):
        amp = min(255, amplitude_base + index * 25)
        parts.append(f"{amp:08X}")
    return "".join(parts)


def counters_from_block(block: bytes) -> tuple[int, int]:
    if not block:
        return 0, 0
    rep = block[0]
    payload = block[1:]
    return len(payload), rep


def _parse_cells_payload(cells_hex: str) -> bytes:
    cleaned = str(cells_hex).strip().replace(" ", "")
    if not cleaned:
        cleaned = default_video_cells_hex()
    return bytes.fromhex(cleaned)


def _scale_azimuth(degrees: float) -> int:
    normalized = degrees % 360.0
    return clamp(int(round(normalized / _AZIMUTH_LSB)), 0, 0xFFFF)


def _pack_uint16_be(value: int) -> bytes:
    value &= 0xFFFF
    return bytes([(value >> 8) & 0xFF, value & 0xFF])


def _pack_uint24_be(value: int) -> bytes:
    value &= 0xFFFFFF
    return bytes([(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])


def _pack_uint32_be(value: int) -> bytes:
    value &= 0xFFFFFFFF
    return bytes(
        [
            (value >> 24) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 8) & 0xFF,
            value & 0xFF,
        ]
    )
