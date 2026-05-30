"""Common Link 16 field encoding helpers."""

from __future__ import annotations

import struct
from typing import Any

from app.asterix.base import FieldDefinition, FieldType, clamp

# Link 16 standard scales (STANAG 5516 simplified)
LAT_LON_LSB_DEG = 180.0 / (2**23)
ALTITUDE_LSB_FT = 25.0
COURSE_LSB_DEG = 360.0 / 4096.0
SPEED_LSB_KTS = 2.0 / 256.0


def encode_lat_lon(lat_deg: float, lon_deg: float) -> bytes:
    lat = int(round(clamp(lat_deg, -90.0, 90.0) / LAT_LON_LSB_DEG))
    lon = int(round(clamp(lon_deg, -180.0, 180.0) / LAT_LON_LSB_DEG))
    return struct.pack(">ii", lat, lon)


def encode_altitude_ft(altitude_ft: float) -> bytes:
    value = int(round(clamp(altitude_ft, -1500.0, 150000.0) / ALTITUDE_LSB_FT))
    return struct.pack(">i", value)


def encode_course_speed(course_deg: float, speed_kts: float) -> bytes:
    course = int(round(clamp(course_deg, 0.0, 359.994) / COURSE_LSB_DEG)) & 0xFFF
    speed = int(round(clamp(speed_kts, 0.0, 2046.0) / SPEED_LSB_KTS)) & 0xFFFF
    return struct.pack(">HH", course, speed)


def encode_track_number(track_number: int) -> bytes:
    return struct.pack(">H", track_number & 0x7FFF)


def encode_single_value(field: FieldDefinition, value: Any) -> bytes:
    if field.field_type == FieldType.COMPOUND and field.fields:
        parts = value if isinstance(value, dict) else {}
        return b"".join(encode_single_value(sub, parts.get(sub.id, sub.default)) for sub in field.fields)

    if field.field_type == FieldType.COMPOUND:
        return b""

    if field.id in {"latitude_deg", "longitude_deg"}:
        return b""

    if field.id == "position" or (isinstance(value, dict) and "latitude_deg" in value):
        pos = value if isinstance(value, dict) else {}
        return encode_lat_lon(float(pos.get("latitude_deg", 0)), float(pos.get("longitude_deg", 0)))

    if field.field_type == FieldType.FLOAT and field.unit == "ft" and "alt" in field.id:
        return encode_altitude_ft(float(value))

    if field.field_type in {FieldType.UINT8, FieldType.ENUM}:
        if isinstance(value, str):
            for opt in field.options:
                if opt.get("value") == value or opt.get("label", "").startswith(value):
                    value = opt["value"]
                    break
        return struct.pack(">B", int(value) & 0xFF)

    if field.field_type == FieldType.UINT16:
        return struct.pack(">H", int(value) & 0xFFFF)

    if field.field_type == FieldType.UINT32:
        return struct.pack(">I", int(value) & 0xFFFFFFFF)

    if field.field_type == FieldType.INT16:
        return struct.pack(">h", int(value))

    if field.field_type == FieldType.FLOAT:
        return struct.pack(">f", float(value))

    if field.field_type == FieldType.STRING:
        raw = str(value).encode("ascii", errors="replace")[:64]
        return struct.pack(">B", len(raw)) + raw

    return struct.pack(">I", int(value) if value is not None else 0)


def encode_field_block(fields: list[FieldDefinition], values: dict[str, Any]) -> bytes:
    return b"".join(
        encode_single_value(field, values.get(field.id, field.default)) for field in fields
    )


def j_series_code(j_series: str) -> int:
    """J3.2 -> 0x0302 style code for word 0."""
    body = j_series[1:]
    major, minor = body.split(".", 1)
    return (int(major) << 8) | int(minor)


def encode_message_header(j_series: str, word_count: int) -> bytes:
    code = j_series_code(j_series)
    return struct.pack(">HH", code, word_count & 0xFFFF)
