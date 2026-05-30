"""Link 16 J0.x network management messages."""

from __future__ import annotations

from app.asterix.base import FieldDefinition, FieldType
from app.link16.messages._factory import make_j_message_class
from app.link16.messages.fields_common import npg_field, source_ju_field

J00 = make_j_message_class(
    j_series="J0.0",
    name="Network Status",
    description="Network status and connectivity summary for a Link 16 participant.",
    npg=0,
    fields=[
        source_ju_field(),
        npg_field(0),
        FieldDefinition(
            id="network_status",
            label="Network Status",
            field_type=FieldType.ENUM,
            default=1,
            options=[
                {"value": 0, "label": "0 — Offline"},
                {"value": 1, "label": "1 — Online"},
                {"value": 2, "label": "2 — Degraded"},
            ],
        ),
        FieldDefinition(
            id="active_participants",
            label="Active Participants",
            field_type=FieldType.UINT16,
            default=4,
            min_value=0,
            max_value=999,
        ),
    ],
)

J01 = make_j_message_class(
    j_series="J0.1",
    name="Network Participation Status",
    description="Reports participation status on assigned NPGs.",
    npg=0,
    fields=[
        source_ju_field(),
        npg_field(0),
        FieldDefinition(
            id="participation_status",
            label="Participation Status",
            field_type=FieldType.UINT8,
            default=1,
            min_value=0,
            max_value=255,
        ),
    ],
)

J02 = make_j_message_class(
    j_series="J0.2",
    name="Network Management",
    description="Network management command and control.",
    npg=0,
    fields=[
        source_ju_field(),
        npg_field(0),
        FieldDefinition(
            id="management_action",
            label="Management Action",
            field_type=FieldType.UINT8,
            default=0,
            options=[
                {"value": 0, "label": "0 — No action"},
                {"value": 1, "label": "1 — Join NPG"},
                {"value": 2, "label": "2 — Leave NPG"},
            ],
        ),
    ],
)

J03 = make_j_message_class(
    j_series="J0.3",
    name="Time Reference",
    description="Network time reference message.",
    npg=0,
    fields=[
        source_ju_field(),
        npg_field(0),
        FieldDefinition(
            id="time_quality",
            label="Time Quality",
            field_type=FieldType.UINT8,
            default=15,
            min_value=0,
            max_value=15,
        ),
        FieldDefinition(
            id="utc_seconds",
            label="UTC Seconds of Day",
            field_type=FieldType.UINT32,
            default=43200,
            min_value=0,
            max_value=86400,
        ),
    ],
)

J0_MESSAGES = [J00, J01, J02, J03]
