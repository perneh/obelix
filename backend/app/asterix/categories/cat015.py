"""ASTERIX Category 015 – INCS Target Reports (Eurocontrol Part 28, Edition 1.1)."""

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
_RANGE_LSB = 0.1
_AZIMUTH_LSB = 360.0 / 65536.0

_MESSAGE_TYPES = [
    {"value": 1, "label": "1 — Measurement plot"},
    {"value": 2, "label": "2 — Measurement track"},
    {"value": 3, "label": "3 — Sensor centric plot"},
    {"value": 4, "label": "4 — Sensor centric track"},
    {"value": 5, "label": "5 — Track end message"},
]

_POSITION_TYPES = [
    {"value": 0, "label": "No position"},
    {"value": 1, "label": "WGS-84 (I015/600)"},
    {"value": 2, "label": "Range & azimuth (I015/625 / I015/627)"},
]


class Cat015(AsterixCategory):
    """Independent Non-Cooperative Surveillance system target reports."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=15,
            name="INCS Target Reports",
            edition="1.1",
            description=(
                "Independent Non-Cooperative Surveillance (INCS) target reports "
                "per Eurocontrol ASTERIX Part 28 Category 015 Edition 1.1."
            ),
            fields=[
                FieldDefinition(
                    id="data_source",
                    label="Data Source Identifier (I015/010)",
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
                    id="message_type",
                    label="Message Type (I015/000)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_MESSAGE_TYPES,
                    uap_frn=2,
                    item_id="000",
                ),
                FieldDefinition(
                    id="report_generation",
                    label="Report generation (I015/000)",
                    field_type=FieldType.ENUM,
                    default=0,
                    description="0 = periodic, 1 = event driven",
                    options=[
                        {"value": 0, "label": "Periodic report"},
                        {"value": 1, "label": "Event driven report"},
                    ],
                ),
                FieldDefinition(
                    id="service_id",
                    label="Service Identification (I015/015)",
                    field_type=FieldType.UINT8,
                    default=0,
                    description="Optional — set > 0 to include",
                    min_value=0,
                    max_value=255,
                    uap_frn=3,
                    item_id="015",
                ),
                FieldDefinition(
                    id="time_of_applicability",
                    label="Time Of Applicability (I015/145)",
                    field_type=FieldType.FLOAT,
                    default=44100.0,
                    description="Seconds since midnight UTC (LSB = 1/128 s)",
                    min_value=0.0,
                    max_value=86400.0,
                    unit="s",
                    uap_frn=6,
                    item_id="145",
                ),
                FieldDefinition(
                    id="track_plot_number",
                    label="Track/Plot Number (I015/161)",
                    field_type=FieldType.UINT16,
                    default=1,
                    min_value=0,
                    max_value=65535,
                    uap_frn=7,
                    item_id="161",
                ),
                FieldDefinition(
                    id="measurement_id",
                    label="Measurement Identifier (I015/400)",
                    field_type=FieldType.COMPOUND,
                    default={"pair_id": 0, "observation_number": 0},
                    description="Links to Cat 016 pair — omit when pair_id is 0",
                    uap_frn=12,
                    item_id="400",
                    fields=[
                        FieldDefinition(
                            id="pair_id",
                            label="Pair ID",
                            field_type=FieldType.UINT16,
                            default=0,
                            min_value=0,
                            max_value=65535,
                        ),
                        FieldDefinition(
                            id="observation_number",
                            label="Observation number",
                            field_type=FieldType.UINT32,
                            default=0,
                            min_value=0,
                            max_value=16777215,
                        ),
                    ],
                ),
                FieldDefinition(
                    id="position_type",
                    label="Position format",
                    field_type=FieldType.ENUM,
                    default=2,
                    options=_POSITION_TYPES,
                ),
                FieldDefinition(
                    id="wgs84",
                    label="Horizontal Position WGS-84 (I015/600)",
                    field_type=FieldType.COMPOUND,
                    default={"latitude_deg": 59.3293, "longitude_deg": 18.0686},
                    description="Latitude/longitude only (P84 subset)",
                    uap_frn=13,
                    item_id="600",
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
                    ],
                ),
                FieldDefinition(
                    id="range_azimuth",
                    label="Range & Azimuth (I015/625 / I015/627)",
                    field_type=FieldType.COMPOUND,
                    default={"range_m": 5000.0, "azimuth_deg": 45.0},
                    uap_frn=20,
                    item_id="625",
                    fields=[
                        FieldDefinition(
                            id="range_m",
                            label="Range",
                            field_type=FieldType.FLOAT,
                            default=5000.0,
                            unit="m",
                        ),
                        FieldDefinition(
                            id="azimuth_deg",
                            label="Azimuth",
                            field_type=FieldType.FLOAT,
                            default=45.0,
                            min_value=0.0,
                            max_value=360.0,
                            unit="°",
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

        mt = clamp(int(field_values.get("message_type", 1)), 1, 127)
        rg = clamp(int(field_values.get("report_generation", 0)), 0, 1)
        items_by_frn[2] = bytes([(mt << 1) | rg])

        service_id = int(field_values.get("service_id", 0))
        if service_id > 0:
            items_by_frn[3] = bytes([clamp(service_id, 0, 255)])

        items_by_frn[6] = _encode_time(float(field_values.get("time_of_applicability", 0.0)))
        items_by_frn[7] = _pack_uint16_be(clamp(int(field_values.get("track_plot_number", 1)), 0, 65535))

        meas = field_values.get("measurement_id", {})
        pair_id = int(meas.get("pair_id", 0))
        if pair_id > 0:
            obs = clamp(int(meas.get("observation_number", 0)), 0, 0xFFFFFF)
            items_by_frn[12] = _pack_uint16_be(pair_id) + _pack_uint24_be(obs)

        position_type = int(field_values.get("position_type", 2))
        if position_type == 1:
            wgs = field_values.get("wgs84", {})
            items_by_frn[13] = _encode_wgs84(
                float(wgs.get("latitude_deg", 0.0)),
                float(wgs.get("longitude_deg", 0.0)),
            )
        elif position_type == 2:
            ra = field_values.get("range_azimuth", {})
            range_raw = _scale_signed(float(ra.get("range_m", 0.0)), _RANGE_LSB, 24)
            az_raw = clamp(int(round(float(ra.get("azimuth_deg", 0.0)) / _AZIMUTH_LSB)), 0, 65535)
            items_by_frn[20] = _pack_int24_be(range_raw)
            items_by_frn[22] = _pack_uint16_be(az_raw)

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
