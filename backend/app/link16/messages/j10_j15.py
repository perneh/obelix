"""Link 16 J10.x, J11.x, J14.x, J15.x messages."""

from __future__ import annotations

from app.asterix.base import FieldDefinition, FieldType
from app.link16.messages._factory import make_j_message_class
from app.link16.messages.fields_common import npg_field, source_ju_field, text_field, track_number_field

J100 = make_j_message_class(
    j_series="J10.0",
    name="Engagement Coordination",
    description="Engagement coordination between C2 nodes.",
    npg=7,
    fields=[
        source_ju_field(),
        npg_field(7),
        track_number_field(201),
        FieldDefinition(
            id="engagement_status",
            label="Engagement Status",
            field_type=FieldType.UINT8,
            default=0,
            options=[
                {"value": 0, "label": "0 — No statement"},
                {"value": 1, "label": "1 — Hold fire"},
                {"value": 2, "label": "2 — Weapons free"},
            ],
        ),
    ],
)

J101 = make_j_message_class(
    j_series="J10.1",
    name="Engagement Status",
    description="Status of an ongoing engagement.",
    npg=7,
    fields=[
        source_ju_field(),
        npg_field(7),
        track_number_field(201),
        FieldDefinition(
            id="status_code",
            label="Status Code",
            field_type=FieldType.UINT8,
            default=1,
            min_value=0,
            max_value=255,
        ),
    ],
)

J110 = make_j_message_class(
    j_series="J11.0",
    name="Electronic Warfare",
    description="Electronic warfare coordination.",
    npg=8,
    fields=[
        source_ju_field(),
        npg_field(8),
        track_number_field(301),
        FieldDefinition(
            id="ew_action",
            label="EW Action",
            field_type=FieldType.UINT8,
            default=0,
            min_value=0,
            max_value=255,
        ),
    ],
)

J140 = make_j_message_class(
    j_series="J14.0",
    name="Parametric Information",
    description="Parametric information exchange.",
    npg=9,
    fields=[
        source_ju_field(),
        npg_field(9),
        FieldDefinition(
            id="parameter_id",
            label="Parameter ID",
            field_type=FieldType.UINT16,
            default=1,
            min_value=0,
            max_value=65535,
        ),
        FieldDefinition(
            id="parameter_value",
            label="Parameter Value",
            field_type=FieldType.UINT32,
            default=0,
            min_value=0,
            max_value=4294967295,
        ),
    ],
)

J150 = make_j_message_class(
    j_series="J15.0",
    name="Simulation Management",
    description="Simulation management for distributed exercises.",
    npg=10,
    fields=[
        source_ju_field(),
        npg_field(10),
        FieldDefinition(
            id="simulation_state",
            label="Simulation State",
            field_type=FieldType.ENUM,
            default=1,
            options=[
                {"value": 0, "label": "0 — Stop"},
                {"value": 1, "label": "1 — Run"},
                {"value": 2, "label": "2 — Pause"},
                {"value": 3, "label": "3 — Reset"},
            ],
        ),
        text_field("Obelix Link 16 simulation"),
    ],
)

J10_MESSAGES = [J100, J101]
J11_MESSAGES = [J110]
J14_MESSAGES = [J140]
J15_MESSAGES = [J150]
