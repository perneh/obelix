"""Shared field definitions for Link 16 J-messages."""

from __future__ import annotations

from app.asterix.base import FieldDefinition, FieldType

IDENTITY_OPTIONS = [
    {"value": 0, "label": "0 — Pending"},
    {"value": 1, "label": "1 — Unknown"},
    {"value": 2, "label": "2 — Assumed Friend"},
    {"value": 3, "label": "3 — Friend"},
    {"value": 4, "label": "4 — Neutral"},
    {"value": 5, "label": "5 — Suspect"},
    {"value": 6, "label": "6 — Hostile"},
]

PLATFORM_AIR = [
    {"value": 0, "label": "0 — No statement"},
    {"value": 1, "label": "1 — Fighter"},
    {"value": 2, "label": "2 — Bomber"},
    {"value": 3, "label": "3 — Transport"},
    {"value": 4, "label": "4 — Tanker"},
    {"value": 5, "label": "5 — AWACS"},
    {"value": 6, "label": "6 — Helicopter"},
]

PLATFORM_SURFACE = [
    {"value": 0, "label": "0 — No statement"},
    {"value": 1, "label": "1 — Warship"},
    {"value": 2, "label": "2 — Merchant"},
    {"value": 3, "label": "3 — Patrol"},
]

STRENGTH_OPTIONS = [
    {"value": 0, "label": "0 — No statement"},
    {"value": 1, "label": "1 — Single unit"},
    {"value": 2, "label": "2 — Section"},
    {"value": 3, "label": "3 — Flight"},
    {"value": 4, "label": "4 — Squadron"},
]


def source_ju_field(default: int = 10001) -> FieldDefinition:
    return FieldDefinition(
        id="source_ju",
        label="Source JU (Unit TN)",
        field_type=FieldType.UINT32,
        default=default,
        min_value=1,
        max_value=999999,
        description="Simulated Link 16 participant sending this message",
    )


def npg_field(default: int) -> FieldDefinition:
    return FieldDefinition(
        id="npg",
        label="NPG",
        field_type=FieldType.UINT16,
        default=default,
        min_value=0,
        max_value=511,
        description="Network Participation Group",
    )


def track_number_field(default: int = 100) -> FieldDefinition:
    return FieldDefinition(
        id="track_number",
        label="Track Number",
        field_type=FieldType.UINT16,
        default=default,
        min_value=0,
        max_value=32767,
    )


def identity_field(default: int = 3) -> FieldDefinition:
    return FieldDefinition(
        id="identity",
        label="Identity",
        field_type=FieldType.ENUM,
        default=default,
        options=IDENTITY_OPTIONS,
    )


def position_field(*, lat: float = 59.0, lon: float = 18.0) -> FieldDefinition:
    return FieldDefinition(
        id="position",
        label="Position (WGS-84)",
        field_type=FieldType.COMPOUND,
        default={"latitude_deg": lat, "longitude_deg": lon},
        fields=[
            FieldDefinition(
                id="latitude_deg",
                label="Latitude",
                field_type=FieldType.FLOAT,
                default=lat,
                min_value=-90.0,
                max_value=90.0,
                unit="°",
            ),
            FieldDefinition(
                id="longitude_deg",
                label="Longitude",
                field_type=FieldType.FLOAT,
                default=lon,
                min_value=-180.0,
                max_value=180.0,
                unit="°",
            ),
        ],
    )


def altitude_field(default: float = 35000.0) -> FieldDefinition:
    return FieldDefinition(
        id="altitude_ft",
        label="Geodetic Altitude",
        field_type=FieldType.FLOAT,
        default=default,
        min_value=-1500.0,
        max_value=150000.0,
        unit="ft",
    )


def course_speed_fields(*, course: float = 90.0, speed: float = 450.0) -> list[FieldDefinition]:
    return [
        FieldDefinition(
            id="course_deg",
            label="Course",
            field_type=FieldType.FLOAT,
            default=course,
            min_value=0.0,
            max_value=359.994,
            unit="°",
        ),
        FieldDefinition(
            id="speed_kts",
            label="Ground Speed",
            field_type=FieldType.FLOAT,
            default=speed,
            min_value=0.0,
            max_value=2046.0,
            unit="kts",
        ),
    ]


def mode3a_field(default: int = 7777) -> FieldDefinition:
    return FieldDefinition(
        id="mode3a",
        label="Mode 3/A Code",
        field_type=FieldType.UINT16,
        default=default,
        min_value=0,
        max_value=7777,
    )


def strength_field(default: int = 1) -> FieldDefinition:
    return FieldDefinition(
        id="strength",
        label="Strength",
        field_type=FieldType.ENUM,
        default=default,
        options=STRENGTH_OPTIONS,
    )


def platform_air_field(default: int = 1) -> FieldDefinition:
    return FieldDefinition(
        id="platform",
        label="Platform",
        field_type=FieldType.ENUM,
        default=default,
        options=PLATFORM_AIR,
    )


def platform_surface_field(default: int = 1) -> FieldDefinition:
    return FieldDefinition(
        id="platform",
        label="Platform",
        field_type=FieldType.ENUM,
        default=default,
        options=PLATFORM_SURFACE,
    )


def text_field(default: str = "OBELIX LINK16") -> FieldDefinition:
    return FieldDefinition(
        id="text",
        label="Text",
        field_type=FieldType.STRING,
        default=default,
        description="Free text (J12.5 / mission data)",
    )
