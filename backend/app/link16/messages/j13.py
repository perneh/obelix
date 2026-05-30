"""Link 16 J13.x weather messages."""

from __future__ import annotations

from app.asterix.base import FieldDefinition, FieldType
from app.link16.messages._factory import make_j_message_class
from app.link16.messages.fields_common import npg_field, position_field, source_ju_field

J130 = make_j_message_class(
    j_series="J13.0",
    name="Weather",
    description="Weather summary for an area.",
    npg=6,
    fields=[
        source_ju_field(),
        npg_field(6),
        position_field(lat=59.0, lon=18.0),
        FieldDefinition(
            id="cloud_base_ft",
            label="Cloud Base",
            field_type=FieldType.UINT16,
            default=3000,
            min_value=0,
            max_value=60000,
            unit="ft",
        ),
        FieldDefinition(
            id="wind_direction_deg",
            label="Wind Direction",
            field_type=FieldType.UINT16,
            default=270,
            min_value=0,
            max_value=359,
            unit="°",
        ),
        FieldDefinition(
            id="wind_speed_kts",
            label="Wind Speed",
            field_type=FieldType.UINT16,
            default=15,
            min_value=0,
            max_value=200,
            unit="kts",
        ),
    ],
)

J132 = make_j_message_class(
    j_series="J13.2",
    name="Weather Data Update",
    description="Incremental weather data update.",
    npg=6,
    fields=[
        source_ju_field(),
        npg_field(6),
        position_field(lat=59.0, lon=18.0),
        FieldDefinition(
            id="precipitation",
            label="Precipitation",
            field_type=FieldType.UINT8,
            default=0,
            options=[
                {"value": 0, "label": "0 — None"},
                {"value": 1, "label": "1 — Light"},
                {"value": 2, "label": "2 — Moderate"},
                {"value": 3, "label": "3 — Heavy"},
            ],
        ),
    ],
)

J13_MESSAGES = [J130, J132]
