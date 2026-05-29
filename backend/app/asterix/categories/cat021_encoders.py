"""Cat 021 helper encoders."""

from __future__ import annotations

from typing import Any

from app.asterix.base import clamp

_TIME_LSB = 1.0 / 128.0
_WGS_LOW_LSB = 180.0 / (2**23)
_WGS_HIGH_LSB = 180.0 / (2**30)
_FL_LSB = 0.25
_GEO_HEIGHT_LSB = 6.25

_IA5_6BIT = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ^^^^^0123456789^^^^^^"


def encode_data_source(data_source: dict[str, Any]) -> bytes:
    sac = clamp(int(data_source.get("sac", 1)), 0, 255)
    sic = clamp(int(data_source.get("sic", 1)), 0, 255)
    return bytes([sac, sic])


def encode_target_report_descriptor(descriptor: dict[str, Any]) -> bytes:
    atp = clamp(int(descriptor.get("atp", 0)), 0, 7)
    arc = clamp(int(descriptor.get("arc", 0)), 0, 3)
    rc = 1 if int(descriptor.get("rc", 0)) else 0
    rab = 1 if int(descriptor.get("rab", 0)) else 0
    include_ext1 = int(descriptor.get("include_extension1", 0)) == 1

    primary = (atp << 5) | (arc << 3) | (rc << 2) | (rab << 1)
    if include_ext1:
        primary |= 0x01
    out = bytearray([primary & 0xFF])

    if include_ext1:
        dcr = 1 if int(descriptor.get("dcr", 0)) else 0
        gbs = 1 if int(descriptor.get("gbs", 0)) else 0
        sim = 1 if int(descriptor.get("sim", 0)) else 0
        tst = 1 if int(descriptor.get("tst", 0)) else 0
        saa = 1 if int(descriptor.get("saa", 0)) else 0
        cl = clamp(int(descriptor.get("cl", 0)), 0, 3)
        ext1 = (dcr << 7) | (gbs << 6) | (sim << 5) | (tst << 4) | (saa << 3) | (cl << 1)
        out.append(ext1 & 0xFF)

    return bytes(out)


def encode_time_seconds(seconds: float) -> bytes:
    raw = clamp(int(round(seconds / _TIME_LSB)), 0, 0xFFFFFF)
    return _pack_uint24_be(raw)


def encode_wgs84_low(wgs84: dict[str, Any]) -> bytes:
    lat_raw = _scale_signed(float(wgs84.get("latitude_deg", 0.0)), _WGS_LOW_LSB, 24)
    lon_raw = _scale_signed(float(wgs84.get("longitude_deg", 0.0)), _WGS_LOW_LSB, 24)
    return _pack_int24_be(lat_raw) + _pack_int24_be(lon_raw)


def encode_wgs84_high(wgs84: dict[str, Any]) -> bytes:
    lat_raw = _scale_signed(float(wgs84.get("latitude_deg", 0.0)), _WGS_HIGH_LSB, 32)
    lon_raw = _scale_signed(float(wgs84.get("longitude_deg", 0.0)), _WGS_HIGH_LSB, 32)
    return _pack_int32_be(lat_raw) + _pack_int32_be(lon_raw)


def encode_target_address(address: str | int) -> bytes:
    if isinstance(address, int):
        value = address
    else:
        cleaned = str(address).strip().replace(" ", "").replace("0x", "").replace("0X", "")
        value = int(cleaned, 16) if cleaned else 0
    value = clamp(value, 0, 0xFFFFFF)
    return bytes([(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])


def encode_mode3a(code: int) -> bytes:
    mode_bits = _octal_to_12bit(clamp(code, 0, 7777))
    return _pack_uint16_be(mode_bits & 0x0FFF)


def encode_flight_level(flight_level: float) -> bytes:
    raw = _scale_signed(float(flight_level), _FL_LSB, 16)
    return _pack_int16_be(raw)


def encode_geometric_height(feet: float) -> bytes:
    raw = _scale_signed(float(feet), _GEO_HEIGHT_LSB, 16)
    return _pack_int16_be(raw)


def encode_target_identification(callsign: str) -> bytes:
    text = str(callsign)[:8].upper().ljust(8)
    buffer = 0
    bits = 0
    out = bytearray()
    for char in text:
        buffer = (buffer << 6) | _ia5_char(char)
        bits += 6
        while bits >= 8:
            bits -= 8
            out.append((buffer >> bits) & 0xFF)
    return bytes(out[:6]).ljust(6, b"\x40")


def _ia5_char(char: str) -> int:
    idx = _IA5_6BIT.find(char.upper())
    return idx if idx >= 0 else 0


def _octal_to_12bit(octal_value: int) -> int:
    digits: list[int] = []
    value = octal_value
    for _ in range(4):
        digits.append(value & 0x7)
        value >>= 3
    result = 0
    for digit in reversed(digits):
        result = (result << 4) | (digit & 0xF)
    return result & 0xFFF


def _scale_signed(value: float, lsb: float, bits: int) -> int:
    raw = int(round(value / lsb))
    limit = 1 << (bits - 1)
    return clamp(raw, -limit, limit - 1)


def _pack_uint16_be(value: int) -> bytes:
    value &= 0xFFFF
    return bytes([(value >> 8) & 0xFF, value & 0xFF])


def _pack_int16_be(value: int) -> bytes:
    if value < 0:
        value = (1 << 16) + value
    return _pack_uint16_be(value)


def _pack_uint24_be(value: int) -> bytes:
    value &= 0xFFFFFF
    return bytes([(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])


def _pack_int24_be(value: int) -> bytes:
    if value < 0:
        value = (1 << 24) + value
    return _pack_uint24_be(value)


def _pack_int32_be(value: int) -> bytes:
    if value < 0:
        value = (1 << 32) + value
    value &= 0xFFFFFFFF
    return bytes([(value >> 24) & 0xFF, (value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])
