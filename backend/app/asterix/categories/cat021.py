"""ASTERIX Category 021 – ADS-B Target Reports (Eurocontrol Part 12, Edition 2.7)."""

from __future__ import annotations

from typing import Any

from app.asterix.base import (
    AsterixCategory,
    CategoryDefinition,
    FieldDefinition,
    FieldType,
    build_fspec,
)
from app.asterix.categories.cat021_encoders import (
    encode_data_source,
    encode_flight_level,
    encode_geometric_height,
    encode_mode3a,
    encode_target_address,
    encode_target_identification,
    encode_target_report_descriptor,
    encode_time_seconds,
    encode_wgs84_high,
    encode_wgs84_low,
)
from app.asterix.categories.cat021_uap import CAT021_UAP
from app.asterix.uap import uap_to_dicts

_ATP_OPTIONS = [
    {"value": 0, "label": "0 — 24-bit ICAO address"},
    {"value": 1, "label": "1 — Duplicate address"},
    {"value": 2, "label": "2 — Surface vehicle address"},
    {"value": 3, "label": "3 — Anonymous address"},
]

_ARC_OPTIONS = [
    {"value": 0, "label": "0 — 25 ft"},
    {"value": 1, "label": "1 — 100 ft"},
    {"value": 2, "label": "2 — Unknown"},
    {"value": 3, "label": "3 — Invalid"},
]

_POSITION_RESOLUTION = [
    {"value": "high", "label": "High resolution (I021/131 · FRN 7)"},
    {"value": "low", "label": "Standard resolution (I021/130 · FRN 6)"},
]

_YES_NO = [
    {"value": 1, "label": "Yes — set FRN in FSPEC"},
    {"value": 0, "label": "No"},
]


def _frn_label(frn: int, item_id: str, name: str) -> str:
    return f"FRN {frn} · I021/{item_id} {name}" if item_id else name


class Cat021(AsterixCategory):
    """ADS-B target reports per Eurocontrol Cat 021 default UAP."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=21,
            name="ADS-B Target Reports",
            edition="2.7",
            description=(
                "Automatic Dependent Surveillance – Broadcast (ADS-B) target reports "
                "per Eurocontrol ASTERIX Part 12 Category 021 Edition 2.7."
            ),
            fields=[
                FieldDefinition(
                    id="data_source",
                    label=_frn_label(1, "010", "Data Source Identification"),
                    field_type=FieldType.COMPOUND,
                    default={"sac": 1, "sic": 1},
                    description="Mandatory — ground station SAC/SIC",
                    uap_frn=1,
                    item_id="010",
                    fields=[
                        FieldDefinition(id="sac", label="SAC", field_type=FieldType.UINT8, default=1),
                        FieldDefinition(id="sic", label="SIC", field_type=FieldType.UINT8, default=1),
                    ],
                ),
                FieldDefinition(
                    id="target_report_descriptor",
                    label=_frn_label(2, "040", "Target Report Descriptor"),
                    field_type=FieldType.COMPOUND,
                    default={
                        "atp": 0,
                        "arc": 0,
                        "rc": 0,
                        "rab": 0,
                        "include_extension1": 1,
                        "dcr": 0,
                        "gbs": 0,
                        "sim": 0,
                        "tst": 0,
                        "saa": 0,
                        "cl": 0,
                    },
                    uap_frn=2,
                    item_id="040",
                    fields=[
                        FieldDefinition(
                            id="atp",
                            label="Address Type (ATP)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=_ATP_OPTIONS,
                        ),
                        FieldDefinition(
                            id="arc",
                            label="Altitude Reporting Capability (ARC)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=_ARC_OPTIONS,
                        ),
                        FieldDefinition(
                            id="rc",
                            label="Range Check (RC)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Default"},
                                {"value": 1, "label": "Range check passed, CPR pending"},
                            ],
                        ),
                        FieldDefinition(
                            id="rab",
                            label="Report Type (RAB)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Target transponder"},
                                {"value": 1, "label": "Field monitor"},
                            ],
                        ),
                        FieldDefinition(
                            id="include_extension1",
                            label="Include 1st extension (GBS, SIM, …)",
                            field_type=FieldType.ENUM,
                            default=1,
                            options=_YES_NO,
                        ),
                        FieldDefinition(
                            id="gbs",
                            label="Ground Bit Setting (GBS)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Airborne"},
                                {"value": 1, "label": "On ground"},
                            ],
                        ),
                        FieldDefinition(
                            id="sim",
                            label="Simulated Target (SIM)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Actual target"},
                                {"value": 1, "label": "Simulated target"},
                            ],
                        ),
                        FieldDefinition(
                            id="tst",
                            label="Test Target (TST)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "Default"},
                                {"value": 1, "label": "Test target"},
                            ],
                        ),
                    ],
                ),
                FieldDefinition(
                    id="time_of_applicability_position",
                    label=_frn_label(5, "071", "Time of Applicability for Position"),
                    field_type=FieldType.FLOAT,
                    default=36000.0,
                    description="Seconds since midnight UTC (LSB = 1/128 s)",
                    min_value=0.0,
                    max_value=86400.0,
                    unit="s",
                    uap_frn=5,
                    item_id="071",
                ),
                FieldDefinition(
                    id="position_resolution",
                    label="WGS-84 position resolution",
                    field_type=FieldType.ENUM,
                    default="high",
                    options=_POSITION_RESOLUTION,
                    description="Select I021/131 (high) or I021/130 (low)",
                ),
                FieldDefinition(
                    id="wgs84",
                    label="Position in WGS-84",
                    field_type=FieldType.COMPOUND,
                    default={"latitude_deg": 59.0, "longitude_deg": 18.0},
                    uap_frn=7,
                    item_id="131",
                    fields=[
                        FieldDefinition(
                            id="latitude_deg",
                            label="Latitude",
                            field_type=FieldType.FLOAT,
                            default=59.0,
                            min_value=-90.0,
                            max_value=90.0,
                            unit="°",
                        ),
                        FieldDefinition(
                            id="longitude_deg",
                            label="Longitude",
                            field_type=FieldType.FLOAT,
                            default=18.0,
                            min_value=-180.0,
                            max_value=180.0,
                            unit="°",
                        ),
                    ],
                ),
                FieldDefinition(
                    id="target_address",
                    label=_frn_label(11, "080", "Target Address"),
                    field_type=FieldType.STRING,
                    default="4AC872",
                    description="24-bit ICAO address as 6-digit hex (e.g. 4AC872)",
                    uap_frn=11,
                    item_id="080",
                ),
                FieldDefinition(
                    id="include_mode3a",
                    label="Include Mode 3/A (FRN 19)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_YES_NO,
                    uap_frn=19,
                    item_id="070",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="mode3a",
                    label=_frn_label(19, "070", "Mode 3/A Code"),
                    field_type=FieldType.UINT16,
                    default=0,
                    description="Octal Mode 3/A code (0–7777)",
                    min_value=0,
                    max_value=7777,
                    uap_frn=19,
                    item_id="070",
                ),
                FieldDefinition(
                    id="include_flight_level",
                    label="Include Flight Level (FRN 21)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_YES_NO,
                    uap_frn=21,
                    item_id="145",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="flight_level",
                    label=_frn_label(21, "145", "Flight Level"),
                    field_type=FieldType.FLOAT,
                    default=350.0,
                    description="Barometric flight level (LSB = ¼ FL)",
                    min_value=-15.0,
                    max_value=1500.0,
                    unit="FL",
                    uap_frn=21,
                    item_id="145",
                ),
                FieldDefinition(
                    id="include_geometric_height",
                    label="Include Geometric Height (FRN 16)",
                    field_type=FieldType.ENUM,
                    default=0,
                    options=_YES_NO,
                    uap_frn=16,
                    item_id="140",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="geometric_height_ft",
                    label=_frn_label(16, "140", "Geometric Height"),
                    field_type=FieldType.FLOAT,
                    default=35000.0,
                    description="Height above WGS-84 ellipsoid (LSB = 6.25 ft)",
                    min_value=-1500.0,
                    max_value=150000.0,
                    unit="ft",
                    uap_frn=16,
                    item_id="140",
                ),
                FieldDefinition(
                    id="include_target_identification",
                    label="Include Target Identification (FRN 29)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_YES_NO,
                    uap_frn=29,
                    item_id="170",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="target_identification",
                    label=_frn_label(29, "170", "Target Identification"),
                    field_type=FieldType.STRING,
                    default="UNKNOWN",
                    description="Up to 8 characters (callsign or registration)",
                    uap_frn=29,
                    item_id="170",
                ),
                FieldDefinition(
                    id="include_time_of_report_transmission",
                    label="Include Time of Report Transmission (FRN 28)",
                    field_type=FieldType.ENUM,
                    default=0,
                    options=_YES_NO,
                    uap_frn=28,
                    item_id="077",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="time_of_report_transmission",
                    label=_frn_label(28, "077", "Time of ASTERIX Report Transmission"),
                    field_type=FieldType.FLOAT,
                    default=36000.0,
                    min_value=0.0,
                    max_value=86400.0,
                    unit="s",
                    uap_frn=28,
                    item_id="077",
                ),
            ],
            uap=uap_to_dicts(CAT021_UAP),
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        present_frns: list[int] = [1, 2]
        items_by_frn: dict[int, bytes] = {
            1: encode_data_source(field_values.get("data_source", {})),
            2: encode_target_report_descriptor(field_values.get("target_report_descriptor", {})),
        }

        wgs84 = field_values.get("wgs84", {})
        if wgs84:
            present_frns.append(5)
            items_by_frn[5] = encode_time_seconds(
                float(field_values.get("time_of_applicability_position", 0.0))
            )
            resolution = str(field_values.get("position_resolution", "high"))
            if resolution == "low":
                present_frns.append(6)
                items_by_frn[6] = encode_wgs84_low(wgs84)
            else:
                present_frns.append(7)
                items_by_frn[7] = encode_wgs84_high(wgs84)

        target_address = str(field_values.get("target_address", "")).strip()
        if target_address:
            present_frns.append(11)
            items_by_frn[11] = encode_target_address(target_address)

        if int(field_values.get("include_geometric_height", 0)) == 1:
            present_frns.append(16)
            items_by_frn[16] = encode_geometric_height(
                float(field_values.get("geometric_height_ft", 0.0))
            )

        if int(field_values.get("include_mode3a", 0)) == 1:
            present_frns.append(19)
            items_by_frn[19] = encode_mode3a(int(field_values.get("mode3a", 0)))

        if int(field_values.get("include_flight_level", 0)) == 1:
            present_frns.append(21)
            items_by_frn[21] = encode_flight_level(float(field_values.get("flight_level", 0.0)))

        if int(field_values.get("include_time_of_report_transmission", 0)) == 1:
            present_frns.append(28)
            items_by_frn[28] = encode_time_seconds(
                float(field_values.get("time_of_report_transmission", 0.0))
            )

        if int(field_values.get("include_target_identification", 0)) == 1:
            present_frns.append(29)
            items_by_frn[29] = encode_target_identification(
                str(field_values.get("target_identification", ""))
            )

        present_frns.sort()
        ordered = [items_by_frn[frn] for frn in present_frns]
        return build_fspec(present_frns) + b"".join(ordered)
