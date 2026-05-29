"""ASTERIX Category 062 – System Track Data (Eurocontrol Part 9, Edition 1.21).

Reference: EUROCONTROL-SPEC-0149-9 — ASTERIX Part 9 Category 062
https://www.eurocontrol.int/publication/cat062-eurocontrol-specification-surveillance-data-exchange-asterix-part-9-category-062
"""

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

# Resolution constants from Eurocontrol Cat 062 ed. 1.21
_TIME_LSB = 1.0 / 128.0  # I062/070
_CART_LSB = 0.5  # I062/100
_WGS_LSB = 180.0 / (2**25)  # I062/105
_VEL_LSB = 0.25  # I062/185
_GEO_ALT_LSB = 6.25  # I062/130
_FL_LSB = 0.25  # I062/136 (1/4 FL)

_POSITION_TYPES = [
    {"value": 0, "label": "No position"},
    {"value": 1, "label": "Cartesian (I062/100)"},
    {"value": 2, "label": "WGS-84 (I062/105)"},
]

_SRC_OPTIONS = [
    {"value": 0, "label": "000 — No source"},
    {"value": 1, "label": "001 — GNSS"},
    {"value": 2, "label": "010 — 3D radar"},
    {"value": 3, "label": "011 — Triangulation"},
    {"value": 4, "label": "100 — Height from coverage"},
    {"value": 5, "label": "101 — Speed look-up table"},
    {"value": 6, "label": "110 — Default height"},
    {"value": 7, "label": "111 — Multilateration"},
]


class Cat062(AsterixCategory):
    """SDPS system track messages per Eurocontrol Cat 062 default UAP."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=62,
            name="System Track Data",
            edition="1.21",
            description=(
                "Processed system track data (SDPS track messages) per Eurocontrol "
                "ASTERIX Part 9 Category 062 Edition 1.21."
            ),
            fields=[
                FieldDefinition(
                    id="data_source",
                    label="Data Source Identifier (I062/010)",
                    field_type=FieldType.COMPOUND,
                    default={"sac": 1, "sic": 1},
                    description="Mandatory — system sending the track data",
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
                    label="Service Identification (I062/015)",
                    field_type=FieldType.UINT8,
                    default=0,
                    description="Optional — set > 0 to include in message",
                    min_value=0,
                    max_value=255,
                    uap_frn=3,
                    item_id="015",
                ),
                FieldDefinition(
                    id="time_of_track",
                    label="Time Of Track Information (I062/070)",
                    field_type=FieldType.FLOAT,
                    default=44100.0,
                    description="Seconds since last midnight UTC (LSB = 1/128 s)",
                    min_value=0.0,
                    max_value=86400.0,
                    unit="s",
                    uap_frn=4,
                    item_id="070",
                ),
                FieldDefinition(
                    id="position_type",
                    label="Position format",
                    field_type=FieldType.ENUM,
                    default=2,
                    description="Select Cartesian (I062/100) or WGS-84 (I062/105) position",
                    options=_POSITION_TYPES,
                ),
                FieldDefinition(
                    id="cartesian",
                    label="Calculated Track Position — Cartesian (I062/100)",
                    field_type=FieldType.COMPOUND,
                    default={"x_m": 1000.0, "y_m": 2000.0},
                    description="Local Cartesian coordinates, LSB = 0.5 m",
                    uap_frn=6,
                    item_id="100",
                    fields=[
                        FieldDefinition(
                            id="x_m",
                            label="X",
                            field_type=FieldType.FLOAT,
                            default=1000.0,
                            unit="m",
                        ),
                        FieldDefinition(
                            id="y_m",
                            label="Y",
                            field_type=FieldType.FLOAT,
                            default=2000.0,
                            unit="m",
                        ),
                    ],
                ),
                FieldDefinition(
                    id="wgs84",
                    label="Calculated Position — WGS-84 (I062/105)",
                    field_type=FieldType.COMPOUND,
                    default={"latitude_deg": 59.3293, "longitude_deg": 18.0686},
                    description="WGS-84 coordinates, LSB = 180/2²⁵ degrees",
                    uap_frn=5,
                    item_id="105",
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
                    id="velocity",
                    label="Calculated Track Velocity — Cartesian (I062/185)",
                    field_type=FieldType.COMPOUND,
                    default={"vx_mps": 50.0, "vy_mps": 10.0},
                    description="Track velocity in m/s, LSB = 0.25 m/s",
                    uap_frn=7,
                    item_id="185",
                    fields=[
                        FieldDefinition(
                            id="vx_mps",
                            label="Vx",
                            field_type=FieldType.FLOAT,
                            default=50.0,
                            unit="m/s",
                        ),
                        FieldDefinition(
                            id="vy_mps",
                            label="Vy",
                            field_type=FieldType.FLOAT,
                            default=10.0,
                            unit="m/s",
                        ),
                    ],
                ),
                FieldDefinition(
                    id="mode3a",
                    label="Track Mode 3/A Code (I062/060)",
                    field_type=FieldType.COMPOUND,
                    default={
                        "code": 7000,
                        "validated": True,
                        "garbled": False,
                        "changed": False,
                    },
                    description="Mode 3/A in octal (0–7777); set code to 0 to omit item",
                    uap_frn=9,
                    item_id="060",
                    fields=[
                        FieldDefinition(
                            id="code",
                            label="Mode 3/A (octal)",
                            field_type=FieldType.UINT16,
                            default=7000,
                            min_value=0,
                            max_value=7777,
                        ),
                        FieldDefinition(
                            id="validated",
                            label="Code validated",
                            field_type=FieldType.ENUM,
                            default=1,
                            options=[
                                {"value": 1, "label": "Validated"},
                                {"value": 0, "label": "Not validated"},
                            ],
                        ),
                        FieldDefinition(
                            id="garbled",
                            label="Garbled",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Normal"},
                                {"value": 1, "label": "Garbled"},
                            ],
                        ),
                        FieldDefinition(
                            id="changed",
                            label="Mode 3/A changed",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "No change"},
                                {"value": 1, "label": "Changed"},
                            ],
                        ),
                    ],
                ),
                FieldDefinition(
                    id="track_number",
                    label="Track Number (I062/040)",
                    field_type=FieldType.UINT16,
                    default=1,
                    description="Mandatory track identifier",
                    min_value=0,
                    max_value=65535,
                    uap_frn=12,
                    item_id="040",
                ),
                FieldDefinition(
                    id="track_status",
                    label="Track Status (I062/080)",
                    field_type=FieldType.COMPOUND,
                    default={
                        "monosensor": 0,
                        "spi": 0,
                        "mrh_geometric": 1,
                        "src": 0,
                        "tentative": 0,
                    },
                    description="Mandatory — first octet of track status (FX=0)",
                    uap_frn=13,
                    item_id="080",
                    fields=[
                        FieldDefinition(
                            id="monosensor",
                            label="MON — Monosensor track",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Multisensor"},
                                {"value": 1, "label": "Monosensor"},
                            ],
                        ),
                        FieldDefinition(
                            id="spi",
                            label="SPI present",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "No"},
                                {"value": 1, "label": "Yes"},
                            ],
                        ),
                        FieldDefinition(
                            id="mrh_geometric",
                            label="MRH — Most reliable height",
                            field_type=FieldType.ENUM,
                            default=1,
                            options=[
                                {"value": 0, "label": "Barometric (Mode C)"},
                                {"value": 1, "label": "Geometric"},
                            ],
                        ),
                        FieldDefinition(
                            id="src",
                            label="SRC — Altitude source",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=_SRC_OPTIONS,
                        ),
                        FieldDefinition(
                            id="tentative",
                            label="CNF — Tentative track",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Confirmed"},
                                {"value": 1, "label": "Tentative"},
                            ],
                        ),
                    ],
                ),
                FieldDefinition(
                    id="flight_level",
                    label="Measured Flight Level (I062/136)",
                    field_type=FieldType.FLOAT,
                    default=0.0,
                    description="Flight level (1/4 FL resolution); set 0 to omit",
                    min_value=-15.0,
                    max_value=1500.0,
                    unit="FL",
                    uap_frn=17,
                    item_id="136",
                ),
                FieldDefinition(
                    id="geometric_altitude_ft",
                    label="Calculated Track Geometric Altitude (I062/130)",
                    field_type=FieldType.FLOAT,
                    default=35000.0,
                    description="Geometric altitude in feet (LSB = 6.25 ft); omit if not used",
                    min_value=-1500.0,
                    max_value=150000.0,
                    unit="ft",
                    uap_frn=18,
                    item_id="130",
                ),
                FieldDefinition(
                    id="include_velocity",
                    label="Include velocity (I062/185)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=[
                        {"value": 1, "label": "Yes"},
                        {"value": 0, "label": "No"},
                    ],
                ),
                FieldDefinition(
                    id="include_geometric_altitude",
                    label="Include geometric altitude (I062/130)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=[
                        {"value": 1, "label": "Yes"},
                        {"value": 0, "label": "No"},
                    ],
                ),
            ],
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        items_by_frn: dict[int, bytes] = {}

        # Mandatory items (Eurocontrol encoding rules)
        items_by_frn[1] = _encode_data_source(field_values.get("data_source", {}))
        items_by_frn[4] = _encode_time_of_track(float(field_values.get("time_of_track", 0.0)))
        items_by_frn[12] = _encode_track_number(int(field_values.get("track_number", 1)))
        items_by_frn[13] = _encode_track_status(field_values.get("track_status", {}))

        service_id = int(field_values.get("service_id", 0))
        if service_id > 0:
            items_by_frn[3] = bytes([clamp(service_id, 0, 255)])

        position_type = _resolve_position_type(field_values.get("position_type", 2))
        if position_type == "cartesian":
            items_by_frn[6] = _encode_cartesian(field_values.get("cartesian", {}))
        elif position_type == "wgs84":
            items_by_frn[5] = _encode_wgs84(field_values.get("wgs84", {}))

        if int(field_values.get("include_velocity", 1)):
            items_by_frn[7] = _encode_velocity(field_values.get("velocity", {}))

        mode3a = field_values.get("mode3a", {})
        mode3a_code = int(mode3a.get("code", 0))
        if mode3a_code > 0:
            items_by_frn[9] = _encode_mode3a(mode3a)

        flight_level = float(field_values.get("flight_level", 0.0))
        if flight_level != 0.0:
            items_by_frn[17] = _encode_flight_level(flight_level)

        if int(field_values.get("include_geometric_altitude", 1)):
            items_by_frn[18] = _encode_geometric_altitude(
                float(field_values.get("geometric_altitude_ft", 0.0))
            )

        present_frns = sorted(items_by_frn)
        return build_fspec(present_frns) + b"".join(items_by_frn[frn] for frn in present_frns)


def _resolve_position_type(value: Any) -> str:
    if isinstance(value, str):
        return value
    return {0: "none", 1: "cartesian", 2: "wgs84"}.get(int(value), "wgs84")


def _encode_data_source(data_source: dict[str, Any]) -> bytes:
    sac = clamp(int(data_source.get("sac", 1)), 0, 255)
    sic = clamp(int(data_source.get("sic", 1)), 0, 255)
    return bytes([sac, sic])


def _encode_time_of_track(seconds: float) -> bytes:
    raw = clamp(int(round(seconds / _TIME_LSB)), 0, 0xFFFFFF)
    return _pack_uint24_be(raw)


def _encode_track_number(track_number: int) -> bytes:
    return _pack_uint16_be(clamp(track_number, 0, 65535))


def _encode_track_status(status: dict[str, Any]) -> bytes:
    mon = 0x80 if int(status.get("monosensor", 0)) else 0
    spi = 0x40 if int(status.get("spi", 0)) else 0
    mrh = 0x20 if int(status.get("mrh_geometric", 1)) else 0
    src = (int(status.get("src", 0)) & 0x7) << 2
    cnf = 0x02 if int(status.get("tentative", 0)) else 0
    return bytes([mon | spi | mrh | src | cnf])


def _encode_cartesian(cartesian: dict[str, Any]) -> bytes:
    x_raw = _scale_signed(float(cartesian.get("x_m", 0.0)), _CART_LSB, 24)
    y_raw = _scale_signed(float(cartesian.get("y_m", 0.0)), _CART_LSB, 24)
    return _pack_int24_be(x_raw) + _pack_int24_be(y_raw)


def _encode_wgs84(wgs84: dict[str, Any]) -> bytes:
    lat_raw = _scale_signed(float(wgs84.get("latitude_deg", 0.0)), _WGS_LSB, 32)
    lon_raw = _scale_signed(float(wgs84.get("longitude_deg", 0.0)), _WGS_LSB, 32)
    return _pack_int32_be(lat_raw) + _pack_int32_be(lon_raw)


def _encode_velocity(velocity: dict[str, Any]) -> bytes:
    vx_raw = _scale_signed(float(velocity.get("vx_mps", 0.0)), _VEL_LSB, 16)
    vy_raw = _scale_signed(float(velocity.get("vy_mps", 0.0)), _VEL_LSB, 16)
    return _pack_int16_be(vx_raw) + _pack_int16_be(vy_raw)


def _encode_mode3a(mode3a: dict[str, Any]) -> bytes:
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


def _encode_flight_level(flight_level: float) -> bytes:
    raw = _scale_signed(flight_level, _FL_LSB, 16)
    return _pack_int16_be(raw)


def _encode_geometric_altitude(altitude_ft: float) -> bytes:
    raw = _scale_signed(altitude_ft, _GEO_ALT_LSB, 16)
    return _pack_int16_be(raw)


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
    """Pack four octal digits (Mode 3/A) into 12 bits."""
    digits: list[int] = []
    value = octal_value
    for _ in range(4):
        digits.append(value & 0x7)
        value >>= 3
    result = 0
    for digit in reversed(digits):
        result = (result << 3) | (digit & 0x7)
    return result & 0x0FFF
