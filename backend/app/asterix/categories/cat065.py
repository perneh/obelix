"""ASTERIX Category 065 – SDPS Service Status Reports (Eurocontrol Part 15, Edition 1.5)."""

from __future__ import annotations

from typing import Any

from app.asterix.base import (
    AsterixCategory,
    CategoryDefinition,
    FieldDefinition,
    FieldType,
    build_fspec,
)
from app.asterix.categories.cat065_encoders import (
    encode_batch_number,
    encode_data_source,
    encode_message_type,
    encode_sdps_configuration,
    encode_service_id,
    encode_service_status_report,
    encode_time_of_message,
)
from app.asterix.categories.cat065_uap import CAT065_UAP
from app.asterix.uap import uap_to_dicts

_MESSAGE_TYPES = [
    {"value": 1, "label": "1 — SDPS Status"},
    {"value": 2, "label": "2 — End of Batch"},
    {"value": 3, "label": "3 — Service Status Report"},
]

_NOGO_OPTIONS = [
    {"value": 0, "label": "0 — Operational"},
    {"value": 1, "label": "1 — Degraded"},
    {"value": 2, "label": "2 — Not currently connected"},
    {"value": 3, "label": "3 — Unknown"},
]

_PSS_OPTIONS = [
    {"value": 0, "label": "0 — Not applicable"},
    {"value": 1, "label": "1 — SDPS-1 selected"},
    {"value": 2, "label": "2 — SDPS-2 selected"},
    {"value": 3, "label": "3 — SDPS-3 selected"},
]

_SERVICE_STATUS_OPTIONS = [
    {"value": 1, "label": "1 — Service degradation"},
    {"value": 2, "label": "2 — Service degradation ended"},
    {"value": 3, "label": "3 — Main radar out of service"},
    {"value": 4, "label": "4 — Service interrupted by operator"},
    {"value": 5, "label": "5 — Service interrupted due to contingency"},
    {"value": 6, "label": "6 — Ready for service restart after contingency"},
    {"value": 7, "label": "7 — Service ended by operator"},
    {"value": 8, "label": "8 — Failure of user main radar"},
    {"value": 9, "label": "9 — Service restarted by operator"},
    {"value": 10, "label": "10 — Main radar becoming operational"},
    {"value": 11, "label": "11 — Main radar becoming degraded"},
    {"value": 12, "label": "12 — Service continuity interrupted (adjacent unit)"},
    {"value": 13, "label": "13 — Service continuity restarted"},
    {"value": 14, "label": "14 — Service synchronised on backup radar"},
    {"value": 15, "label": "15 — Service synchronised on main radar"},
    {"value": 16, "label": "16 — Main and backup radar failed"},
]

_YES_NO = [
    {"value": 1, "label": "Yes — set FRN in FSPEC"},
    {"value": 0, "label": "No"},
]


def _frn_label(frn: int, item_id: str, name: str) -> str:
    return f"FRN {frn} · I065/{item_id} {name}" if item_id else name


class Cat065(AsterixCategory):
    """SDPS service status reports per Eurocontrol Cat 065 default UAP."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=65,
            name="SDPS Service Status Reports",
            edition="1.5",
            description=(
                "Surveillance Data Processing System (SDPS) service status and "
                "configuration reports per Eurocontrol ASTERIX Part 15 Category 065 Edition 1.5."
            ),
            fields=[
                FieldDefinition(
                    id="data_source",
                    label=_frn_label(1, "010", "Data Source Identifier"),
                    field_type=FieldType.COMPOUND,
                    default={"sac": 1, "sic": 1},
                    description="Mandatory — SDPS SAC/SIC",
                    uap_frn=1,
                    item_id="010",
                    fields=[
                        FieldDefinition(id="sac", label="SAC", field_type=FieldType.UINT8, default=1),
                        FieldDefinition(id="sic", label="SIC", field_type=FieldType.UINT8, default=1),
                    ],
                ),
                FieldDefinition(
                    id="message_type",
                    label=_frn_label(2, "000", "Message Type"),
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_MESSAGE_TYPES,
                    uap_frn=2,
                    item_id="000",
                ),
                FieldDefinition(
                    id="service_id",
                    label=_frn_label(3, "015", "Service Identification"),
                    field_type=FieldType.UINT8,
                    default=1,
                    description="Optional — set 0 to omit FRN 3",
                    min_value=0,
                    max_value=255,
                    uap_frn=3,
                    item_id="015",
                ),
                FieldDefinition(
                    id="time_of_message",
                    label=_frn_label(4, "030", "Time of Message"),
                    field_type=FieldType.FLOAT,
                    default=36000.0,
                    description="Seconds since midnight UTC (LSB = 1/128 s)",
                    min_value=0.0,
                    max_value=86400.0,
                    unit="s",
                    uap_frn=4,
                    item_id="030",
                ),
                FieldDefinition(
                    id="include_batch_number",
                    label="Include Batch Number (FRN 5)",
                    field_type=FieldType.ENUM,
                    default=0,
                    options=_YES_NO,
                    description="Typically used with message type End of Batch (2)",
                    uap_frn=5,
                    item_id="020",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="batch_number",
                    label=_frn_label(5, "020", "Batch Number"),
                    field_type=FieldType.UINT8,
                    default=0,
                    min_value=0,
                    max_value=255,
                    uap_frn=5,
                    item_id="020",
                ),
                FieldDefinition(
                    id="sdps_configuration",
                    label=_frn_label(6, "040", "SDPS Configuration and Status"),
                    field_type=FieldType.COMPOUND,
                    default={"nogo": 0, "ovl": 0, "tsv": 0, "pss": 1, "sttn": 0},
                    description="Typically included for message type SDPS Status (1)",
                    uap_frn=6,
                    item_id="040",
                    fields=[
                        FieldDefinition(
                            id="nogo",
                            label="NOGO — operational status",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=_NOGO_OPTIONS,
                        ),
                        FieldDefinition(
                            id="ovl",
                            label="OVL — overload",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Default"},
                                {"value": 1, "label": "Overload"},
                            ],
                        ),
                        FieldDefinition(
                            id="tsv",
                            label="TSV — invalid time source",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Default"},
                                {"value": 1, "label": "Invalid time source"},
                            ],
                        ),
                        FieldDefinition(
                            id="pss",
                            label="PSS — processing system selected",
                            field_type=FieldType.ENUM,
                            default=1,
                            options=_PSS_OPTIONS,
                        ),
                        FieldDefinition(
                            id="sttn",
                            label="STTN — track re-numbering toggle",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Default"},
                                {"value": 1, "label": "Track re-numbering occurred"},
                            ],
                        ),
                    ],
                ),
                FieldDefinition(
                    id="include_sdps_configuration",
                    label="Include SDPS Configuration (FRN 6)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_YES_NO,
                    uap_frn=6,
                    item_id="040",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="service_status_report",
                    label=_frn_label(7, "050", "Service Status Report"),
                    field_type=FieldType.ENUM,
                    default=15,
                    description="Used with message type Service Status Report (3)",
                    options=_SERVICE_STATUS_OPTIONS,
                    uap_frn=7,
                    item_id="050",
                ),
                FieldDefinition(
                    id="include_service_status_report",
                    label="Include Service Status Report (FRN 7)",
                    field_type=FieldType.ENUM,
                    default=0,
                    options=_YES_NO,
                    uap_frn=7,
                    item_id="050",
                    include_flag=True,
                ),
            ],
            uap=uap_to_dicts(CAT065_UAP),
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        message_type = int(field_values.get("message_type", 1))
        present_frns: list[int] = [1, 2, 4]
        items_by_frn: dict[int, bytes] = {
            1: encode_data_source(field_values.get("data_source", {})),
            2: encode_message_type(message_type),
            4: encode_time_of_message(float(field_values.get("time_of_message", 0.0))),
        }

        service_id = int(field_values.get("service_id", 0))
        if service_id > 0:
            present_frns.append(3)
            items_by_frn[3] = encode_service_id(service_id)

        if int(field_values.get("include_batch_number", 0)) == 1 or message_type == 2:
            present_frns.append(5)
            items_by_frn[5] = encode_batch_number(int(field_values.get("batch_number", 0)))

        if int(field_values.get("include_sdps_configuration", 1)) == 1 and message_type == 1:
            present_frns.append(6)
            items_by_frn[6] = encode_sdps_configuration(field_values.get("sdps_configuration", {}))

        include_report = int(field_values.get("include_service_status_report", 0)) == 1
        if include_report or message_type == 3:
            present_frns.append(7)
            items_by_frn[7] = encode_service_status_report(
                int(field_values.get("service_status_report", 15))
            )

        present_frns.sort()
        ordered = [items_by_frn[frn] for frn in present_frns]
        return build_fspec(present_frns) + b"".join(ordered)
