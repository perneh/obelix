"""Link 16 J7.x system management messages."""

from __future__ import annotations

from app.asterix.base import FieldDefinition, FieldType
from app.link16.messages._factory import make_j_message_class
from app.link16.messages.fields_common import mode3a_field, npg_field, source_ju_field, track_number_field

J70 = make_j_message_class(
    j_series="J7.0",
    name="Track Management",
    description="Track management (correlation, drop, assume control).",
    npg=3,
    fields=[
        source_ju_field(),
        npg_field(3),
        track_number_field(101),
        FieldDefinition(
            id="management_action",
            label="Track Management Action",
            field_type=FieldType.ENUM,
            default=1,
            options=[
                {"value": 0, "label": "0 — No statement"},
                {"value": 1, "label": "1 — Assume control"},
                {"value": 2, "label": "2 — Drop track"},
                {"value": 3, "label": "3 — Correlation request"},
            ],
        ),
    ],
)

J71 = make_j_message_class(
    j_series="J7.1",
    name="Data Update Request",
    description="Request data update for a track or participant.",
    npg=3,
    fields=[
        source_ju_field(),
        npg_field(3),
        track_number_field(101),
        FieldDefinition(
            id="update_type",
            label="Update Type",
            field_type=FieldType.UINT8,
            default=1,
            min_value=0,
            max_value=255,
        ),
    ],
)

J72 = make_j_message_class(
    j_series="J7.2",
    name="Data Update Action",
    description="Action in response to a data update request.",
    npg=3,
    fields=[
        source_ju_field(),
        npg_field(3),
        track_number_field(101),
        FieldDefinition(
            id="action_code",
            label="Action Code",
            field_type=FieldType.UINT8,
            default=0,
            min_value=0,
            max_value=255,
        ),
    ],
)

J74 = make_j_message_class(
    j_series="J7.4",
    name="Aircraft Control",
    description="Aircraft control orders.",
    npg=3,
    fields=[
        source_ju_field(),
        npg_field(3),
        track_number_field(101),
        FieldDefinition(
            id="control_order",
            label="Control Order",
            field_type=FieldType.UINT8,
            default=0,
            options=[
                {"value": 0, "label": "0 — No statement"},
                {"value": 1, "label": "1 — Vector"},
                {"value": 2, "label": "2 — Orbit"},
                {"value": 3, "label": "3 — RTB"},
            ],
        ),
    ],
)

J75 = make_j_message_class(
    j_series="J7.5",
    name="IFF/SIF Management",
    description="IFF/SIF management for a track.",
    npg=3,
    fields=[
        source_ju_field(),
        npg_field(3),
        track_number_field(101),
        mode3a_field(7777),
        FieldDefinition(
            id="iff_mode4",
            label="Mode 4 Interrogation",
            field_type=FieldType.UINT8,
            default=0,
            options=[
                {"value": 0, "label": "0 — No statement"},
                {"value": 1, "label": "1 — Interrogate"},
                {"value": 2, "label": "2 — Do not interrogate"},
            ],
        ),
    ],
)

J7_MESSAGES = [J70, J71, J72, J74, J75]
