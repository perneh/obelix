"""Link 16 J12.x mission assignment messages."""

from __future__ import annotations

from app.asterix.base import FieldDefinition, FieldType
from app.link16.messages._factory import make_j_message_class
from app.link16.messages.fields_common import (
    altitude_field,
    course_speed_fields,
    npg_field,
    position_field,
    source_ju_field,
    text_field,
    track_number_field,
)

J120 = make_j_message_class(
    j_series="J12.0",
    name="Mission Assignment",
    description="Assign a mission to a unit or track.",
    npg=5,
    fields=[
        source_ju_field(),
        npg_field(5),
        track_number_field(101),
        FieldDefinition(
            id="mission_type",
            label="Mission Type",
            field_type=FieldType.ENUM,
            default=1,
            options=[
                {"value": 0, "label": "0 — No statement"},
                {"value": 1, "label": "1 — CAP"},
                {"value": 2, "label": "2 — Strike"},
                {"value": 3, "label": "3 — Reconnaissance"},
                {"value": 4, "label": "4 — Escort"},
            ],
        ),
        position_field(lat=59.0, lon=18.0),
    ],
)

J121 = make_j_message_class(
    j_series="J12.1",
    name="Target Sorting",
    description="Target sorting and prioritization.",
    npg=5,
    fields=[
        source_ju_field(),
        npg_field(5),
        track_number_field(201),
        FieldDefinition(
            id="priority",
            label="Target Priority",
            field_type=FieldType.UINT8,
            default=1,
            min_value=1,
            max_value=10,
        ),
    ],
)

J122 = make_j_message_class(
    j_series="J12.2",
    name="Target Position",
    description="Target position update for mission planning.",
    npg=5,
    fields=[
        source_ju_field(),
        npg_field(5),
        track_number_field(201),
        position_field(lat=57.5, lon=16.0),
        altitude_field(25000),
    ],
)

J124 = make_j_message_class(
    j_series="J12.4",
    name="Target Position Weather",
    description="Weather at target position.",
    npg=5,
    fields=[
        source_ju_field(),
        npg_field(5),
        track_number_field(201),
        position_field(lat=57.5, lon=16.0),
        FieldDefinition(
            id="visibility_nm",
            label="Visibility",
            field_type=FieldType.UINT16,
            default=10,
            min_value=0,
            max_value=100,
            unit="nm",
        ),
    ],
)

J125 = make_j_message_class(
    j_series="J12.5",
    name="Text",
    description="Free-text mission or C2 message.",
    npg=5,
    fields=[
        source_ju_field(),
        npg_field(5),
        track_number_field(101),
        text_field("Mission: CAP station BALTIC-1"),
    ],
)

J126 = make_j_message_class(
    j_series="J12.6",
    name="Kinematic",
    description="Kinematic update for assigned target.",
    npg=5,
    fields=[
        source_ju_field(),
        npg_field(5),
        track_number_field(201),
        position_field(lat=57.5, lon=16.0),
        altitude_field(25000),
        *course_speed_fields(course=270, speed=480),
    ],
)

J12_MESSAGES = [J120, J121, J122, J124, J125, J126]
