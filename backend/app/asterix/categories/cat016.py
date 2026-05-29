"""ASTERIX Category 016 – INCS Configuration Reports (Eurocontrol Part 30, Edition 1.0)."""

from __future__ import annotations

from typing import Any

from app.asterix.base import (
    AsterixCategory,
    CategoryDefinition,
    FieldDefinition,
    FieldType,
    build_fspec,
    clamp,
)

_TIME_LSB = 1.0 / 128.0
_WGS_LSB = 180.0 / (2**31)
_HEIGHT_LSB = 0.25

_MESSAGE_TYPES = [
    {"value": 1, "label": "1 — System configuration"},
    {"value": 2, "label": "2 — Transmitter / receiver configuration"},
]


class Cat016(AsterixCategory):
    """Independent Non-Cooperative Surveillance system configuration reports."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=16,
            name="INCS Configuration Reports",
            edition="1.0",
            description=(
                "INCS system configuration data per Eurocontrol ASTERIX Part 30 "
                "Category 016 Edition 1.0. Pairs with Cat 015 via measurement/pair IDs."
            ),
            fields=[
                FieldDefinition(
                    id="data_source",
                    label="Data Source Identifier (I016/010)",
                    field_type=FieldType.COMPOUND,
                    default={"sac": 1, "sic": 1},
                    uap_frn=1,
                    item_id="010",
                    fields=[
                        FieldDefinition(
                            id="sac",
                            label="SAC",
                            field_type=FieldType.UINT8,
                            default=1,
                            min_value=0,
                            max_value=255,
                        ),
                        FieldDefinition(
                            id="sic",
                            label="SIC",
                            field_type=FieldType.UINT8,
                            default=1,
                            min_value=0,
                            max_value=255,
                        ),
                    ],
                ),
                FieldDefinition(
                    id="service_id",
                    label="Service Identification (I016/015)",
                    field_type=FieldType.UINT8,
                    default=0,
                    description="Optional — set > 0 to include",
                    min_value=0,
                    max_value=255,
                    uap_frn=2,
                    item_id="015",
                ),
                FieldDefinition(
                    id="message_type",
                    label="Message Type (I016/000)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_MESSAGE_TYPES,
                    uap_frn=3,
                    item_id="000",
                ),
                FieldDefinition(
                    id="time_of_day",
                    label="Time Of Day (I016/140)",
                    field_type=FieldType.FLOAT,
                    default=44100.0,
                    description="Seconds since midnight UTC (LSB = 1/128 s)",
                    min_value=0.0,
                    max_value=86400.0,
                    unit="s",
                    uap_frn=4,
                    item_id="140",
                ),
                FieldDefinition(
                    id="reporting_period_s",
                    label="Configuration Reporting Period (I016/200)",
                    field_type=FieldType.UINT8,
                    default=0,
                    description="Optional — seconds between periodic reports (0 = omit)",
                    min_value=0,
                    max_value=255,
                    uap_frn=5,
                    item_id="200",
                ),
                FieldDefinition(
                    id="pair",
                    label="Pair Identification (I016/300)",
                    field_type=FieldType.COMPOUND,
                    default={"pair_id": 1, "transmitter_id": 1, "receiver_id": 1},
                    uap_frn=6,
                    item_id="300",
                    fields=[
                        FieldDefinition(
                            id="pair_id",
                            label="Pair ID",
                            field_type=FieldType.UINT16,
                            default=1,
                            min_value=0,
                            max_value=65535,
                        ),
                        FieldDefinition(
                            id="transmitter_id",
                            label="Transmitter ID",
                            field_type=FieldType.UINT16,
                            default=1,
                            min_value=0,
                            max_value=65535,
                        ),
                        FieldDefinition(
                            id="receiver_id",
                            label="Receiver ID",
                            field_type=FieldType.UINT16,
                            default=1,
                            min_value=0,
                            max_value=65535,
                        ),
                    ],
                ),
                FieldDefinition(
                    id="reference_point",
                    label="System Reference Point (I016/400 + I016/405)",
                    field_type=FieldType.COMPOUND,
                    default={
                        "latitude_deg": 59.3293,
                        "longitude_deg": 18.0686,
                        "height_m": 25.0,
                    },
                    uap_frn=7,
                    item_id="400",
                    fields=[
                        FieldDefinition(
                            id="latitude_deg",
                            label="Latitude",
                            field_type=FieldType.FLOAT,
                            default=59.3293,
                            min_value=-90.0,
                            max_value=90.0,
                            unit="°",
                        ),
                        FieldDefinition(
                            id="longitude_deg",
                            label="Longitude",
                            field_type=FieldType.FLOAT,
                            default=18.0686,
                            min_value=-180.0,
                            max_value=180.0,
                            unit="°",
                        ),
                        FieldDefinition(
                            id="height_m",
                            label="Height (MSL)",
                            field_type=FieldType.FLOAT,
                            default=25.0,
                            unit="m",
                        ),
                    ],
                ),
            ],
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        items_by_frn: dict[int, bytes] = {}

        ds = field_values.get("data_source", {})
        items_by_frn[1] = bytes(
            [
                clamp(int(ds.get("sac", 1)), 0, 255),
                clamp(int(ds.get("sic", 1)), 0, 255),
            ]
        )

        service_id = int(field_values.get("service_id", 0))
        if service_id > 0:
            items_by_frn[2] = bytes([clamp(service_id, 0, 255)])

        items_by_frn[3] = bytes([clamp(int(field_values.get("message_type", 1)), 1, 255)])
        items_by_frn[4] = _encode_time(float(field_values.get("time_of_day", 0.0)))

        period = int(field_values.get("reporting_period_s", 0))
        if period > 0:
            items_by_frn[5] = bytes([clamp(period, 1, 255)])

        pair = field_values.get("pair", {})
        pair_id = int(pair.get("pair_id", 1))
        tx_id = clamp(int(pair.get("transmitter_id", 1)), 0, 65535)
        rx_id = clamp(int(pair.get("receiver_id", 1)), 0, 65535)
        items_by_frn[6] = bytes([1]) + _pack_uint16_be(pair_id) + _pack_uint16_be(tx_id) + _pack_uint16_be(rx_id)

        ref = field_values.get("reference_point", {})
        lat = float(ref.get("latitude_deg", 0.0))
        lon = float(ref.get("longitude_deg", 0.0))
        height = float(ref.get("height_m", 0.0))
        items_by_frn[7] = _encode_wgs84(lat, lon)
        items_by_frn[8] = _pack_int16_be(_scale_signed(height, _HEIGHT_LSB, 16))

        present_frns = sorted(items_by_frn)
        return build_fspec(present_frns) + b"".join(items_by_frn[frn] for frn in present_frns)


def _encode_time(seconds: float) -> bytes:
    raw = clamp(int(round(seconds / _TIME_LSB)), 0, 0xFFFFFF)
    return _pack_uint24_be(raw)


def _encode_wgs84(latitude_deg: float, longitude_deg: float) -> bytes:
    lat_raw = _scale_signed(latitude_deg, _WGS_LSB, 32)
    lon_raw = _scale_signed(longitude_deg, _WGS_LSB, 32)
    return _pack_int32_be(lat_raw) + _pack_int32_be(lon_raw)


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
