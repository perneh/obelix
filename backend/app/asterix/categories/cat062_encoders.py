"""Cat 062 helper encoders shared by the category module."""

from __future__ import annotations

from typing import Any

from app.asterix.base import clamp

_TIME_LSB = 1.0 / 128.0
_CART_LSB = 0.5
_WGS_LSB = 180.0 / (2**25)
_VEL_LSB = 0.25
_ACCEL_LSB = 0.25
_GEO_ALT_LSB = 6.25
_FL_LSB = 0.25
_BARO_FL_LSB = 0.25
_ROC_LSB = 6.25

_IA5_6BIT = "@ABCDEFGHIJKLMNOPQRSTUVWXYZ^^^^^0123456789^^^^^^"


def include_section(field_values: dict[str, Any], key: str) -> bool:
    section = field_values.get(key, {})
    if isinstance(section, dict):
        return int(section.get("include", 0)) == 1
    return int(field_values.get(f"include_{key}", 0)) == 1


def encode_optional_compound(field_values: dict[str, Any], key: str) -> bytes | None:
    if not include_section(field_values, key):
        return None
    section = field_values.get(key, {})
    raw = str(section.get("raw_hex", "")).strip().replace(" ", "")
    if raw:
        return bytes.fromhex(raw)
    return b"\x00"


def encode_data_source(data_source: dict[str, Any]) -> bytes:
    sac = clamp(int(data_source.get("sac", 1)), 0, 255)
    sic = clamp(int(data_source.get("sic", 1)), 0, 255)
    return bytes([sac, sic])


def encode_time_of_track(seconds: float) -> bytes:
    raw = clamp(int(round(seconds / _TIME_LSB)), 0, 0xFFFFFF)
    return _pack_uint24_be(raw)


def encode_track_number(track_number: int) -> bytes:
    return _pack_uint16_be(clamp(track_number, 0, 65535))


def encode_track_status(status: dict[str, Any]) -> bytes:
    mon = 0x80 if int(status.get("monosensor", 0)) else 0
    spi = 0x40 if int(status.get("spi", 0)) else 0
    mrh = 0x20 if int(status.get("mrh_geometric", 1)) else 0
    src = (int(status.get("src", 0)) & 0x7) << 2
    cnf = 0x02 if int(status.get("tentative", 0)) else 0
    return bytes([mon | spi | mrh | src | cnf])


def encode_cartesian(cartesian: dict[str, Any]) -> bytes:
    x_raw = _scale_signed(float(cartesian.get("x_m", 0.0)), _CART_LSB, 24)
    y_raw = _scale_signed(float(cartesian.get("y_m", 0.0)), _CART_LSB, 24)
    return _pack_int24_be(x_raw) + _pack_int24_be(y_raw)


def encode_wgs84(wgs84: dict[str, Any]) -> bytes:
    lat_raw = _scale_signed(float(wgs84.get("latitude_deg", 0.0)), _WGS_LSB, 32)
    lon_raw = _scale_signed(float(wgs84.get("longitude_deg", 0.0)), _WGS_LSB, 32)
    return _pack_int32_be(lat_raw) + _pack_int32_be(lon_raw)


def encode_velocity(velocity: dict[str, Any]) -> bytes:
    vx_raw = _scale_signed(float(velocity.get("vx_mps", 0.0)), _VEL_LSB, 16)
    vy_raw = _scale_signed(float(velocity.get("vy_mps", 0.0)), _VEL_LSB, 16)
    return _pack_int16_be(vx_raw) + _pack_int16_be(vy_raw)


def encode_acceleration(acceleration: dict[str, Any]) -> bytes:
    ax = _scale_signed(float(acceleration.get("ax_mps2", 0.0)), _ACCEL_LSB, 8)
    ay = _scale_signed(float(acceleration.get("ay_mps2", 0.0)), _ACCEL_LSB, 8)
    return bytes([ax & 0xFF, ay & 0xFF])


def encode_mode3a(mode3a: dict[str, Any]) -> bytes:
    validated = int(mode3a.get("validated", 1))
    garbled = int(mode3a.get("garbled", 0))
    changed = int(mode3a.get("changed", 0))
    code = clamp(int(mode3a.get("code", 0)), 0, 7777)
    mode_bits = _octal_to_12bit(code)
    value = (
        ((0 if validated else 1) << 15)
        | (garbled << 14)
        | (changed << 13)
        | (mode_bits & 0x1FFF)
    )
    return _pack_uint16_be(value)


def encode_mode2(mode2: dict[str, Any]) -> bytes:
    code = clamp(int(mode2.get("code", 0)), 0, 7777)
    mode_bits = _octal_to_12bit(code)
    return _pack_uint16_be(mode_bits & 0x0FFF)


def encode_target_identification(data: dict[str, Any]) -> bytes:
    sti = int(data.get("sti", 0)) & 0x3
    callsign = str(data.get("callsign", "UNKNOWN"))[:8].upper().ljust(8)
    first = bytes([(sti << 6) & 0xC0])
    buffer = 0
    bits = 0
    out = bytearray()
    for char in callsign:
        buffer = (buffer << 6) | _ia5_char(char)
        bits += 6
        while bits >= 8:
            bits -= 8
            out.append((buffer >> bits) & 0xFF)
    return first + bytes(out)


def encode_mode_of_movement(data: dict[str, Any]) -> bytes:
    trans = int(data.get("transversal", 0)) & 0x3
    long_acc = int(data.get("longitudinal", 0)) & 0x3
    vert = int(data.get("vertical", 0)) & 0x3
    adf = int(data.get("altitude_discrepancy", 0)) & 0x1
    return bytes([(trans << 6) | (long_acc << 4) | (vert << 2) | (adf << 1)])


def encode_flight_level(flight_level: float) -> bytes:
    raw = _scale_signed(flight_level, _FL_LSB, 16)
    return _pack_int16_be(raw)


def encode_geometric_altitude(altitude_ft: float) -> bytes:
    raw = _scale_signed(altitude_ft, _GEO_ALT_LSB, 16)
    return _pack_int16_be(raw)


def encode_barometric_altitude(data: dict[str, Any]) -> bytes:
    qnh = int(data.get("qnh_applied", 0)) & 0x1
    fl = float(data.get("flight_level", 0.0))
    raw = _scale_signed(fl, _BARO_FL_LSB, 15)
    value = (qnh << 15) | (raw & 0x7FFF)
    return _pack_uint16_be(value)


def encode_rate_of_climb(fpm: float) -> bytes:
    raw = _scale_signed(fpm, _ROC_LSB, 16)
    return _pack_int16_be(raw)


def encode_vehicle_fleet_id(fleet_id: int) -> bytes:
    return bytes([clamp(fleet_id, 0, 255)])


def encode_composed_track_number(data: dict[str, Any]) -> bytes:
    unit_id = clamp(int(data.get("system_unit_id", 1)), 0, 255)
    track_num = clamp(int(data.get("system_track_number", 1)), 0, 0x7FFF)
    return bytes([unit_id, (track_num >> 7) & 0xFF, ((track_num & 0x7F) << 1) & 0xFE])


def resolve_position_type(value: Any) -> str:
    if isinstance(value, str):
        return value
    return {0: "none", 1: "cartesian", 2: "wgs84"}.get(int(value), "wgs84")


def _ia5_char(char: str) -> int:
    normalized = "@" if char == " " else char.upper()
    try:
        return _IA5_6BIT.index(normalized)
    except ValueError:
        return 0


def _scale_signed(value: float, lsb: float, bits: int) -> int:
    raw = int(round(value / lsb))
    min_val = -(1 << (bits - 1))
    max_val = (1 << (bits - 1)) - 1
    return clamp(raw, min_val, max_val)


def _pack_uint16_be(value: int) -> bytes:
    return bytes([(value >> 8) & 0xFF, value & 0xFF])


def _pack_uint24_be(value: int) -> bytes:
    return bytes([(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])


def _pack_int16_be(value: int) -> bytes:
    if value < 0:
        value = (1 << 16) + value
    return _pack_uint16_be(value & 0xFFFF)


def _pack_int24_be(value: int) -> bytes:
    if value < 0:
        value = (1 << 24) + value
    return _pack_uint24_be(value & 0xFFFFFF)


def _pack_int32_be(value: int) -> bytes:
    if value < 0:
        value = (1 << 32) + value
    return bytes(
        [
            (value >> 24) & 0xFF,
            (value >> 16) & 0xFF,
            (value >> 8) & 0xFF,
            value & 0xFF,
        ]
    )


def _octal_to_12bit(octal_value: int) -> int:
    digits: list[int] = []
    value = octal_value
    for _ in range(4):
        digits.append(value & 0x7)
        value >>= 3
    result = 0
    for digit in reversed(digits):
        result = (result << 3) | (digit & 0x7)
    return result & 0x0FFF
