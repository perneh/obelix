"""Link 16 J9.x command messages."""

from __future__ import annotations

from app.asterix.base import FieldDefinition, FieldType
from app.link16.messages._factory import make_j_message_class
from app.link16.messages.fields_common import npg_field, source_ju_field, track_number_field

J90 = make_j_message_class(
    j_series="J9.0",
    name="Command",
    description="Generic command message.",
    npg=4,
    fields=[
        source_ju_field(),
        npg_field(4),
        track_number_field(101),
        FieldDefinition(
            id="command_type",
            label="Command Type",
            field_type=FieldType.UINT8,
            default=1,
            min_value=0,
            max_value=255,
        ),
    ],
)

J91 = make_j_message_class(
    j_series="J9.1",
    name="Air Command",
    description="Air-specific command.",
    npg=4,
    fields=[
        source_ju_field(),
        npg_field(4),
        track_number_field(101),
        FieldDefinition(
            id="air_command",
            label="Air Command",
            field_type=FieldType.ENUM,
            default=1,
            options=[
                {"value": 0, "label": "0 — No statement"},
                {"value": 1, "label": "1 — Intercept"},
                {"value": 2, "label": "2 — CAP"},
                {"value": 3, "label": "3 — RTB"},
            ],
        ),
    ],
)

J92 = make_j_message_class(
    j_series="J9.2",
    name="Surface Command",
    description="Surface-specific command.",
    npg=4,
    fields=[
        source_ju_field(),
        npg_field(4),
        track_number_field(201),
        FieldDefinition(
            id="surface_command",
            label="Surface Command",
            field_type=FieldType.ENUM,
            default=1,
            options=[
                {"value": 0, "label": "0 — No statement"},
                {"value": 1, "label": "1 — Patrol"},
                {"value": 2, "label": "2 — Hold"},
                {"value": 3, "label": "3 — Engage"},
            ],
        ),
    ],
)

J9_MESSAGES = [J90, J91, J92]
