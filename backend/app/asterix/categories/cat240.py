"""ASTERIX Category 240 – Radar Video Transmission (Eurocontrol Part 14, Edition 1.3)."""

from __future__ import annotations

from typing import Any

from app.asterix.base import (
    AsterixCategory,
    CategoryDefinition,
    FieldDefinition,
    FieldType,
    build_fspec,
)
from app.asterix.categories.cat240_encoders import (
    counters_from_block,
    encode_data_source,
    encode_message_type,
    encode_time_of_day,
    encode_video_block_high,
    encode_video_block_low,
    encode_video_block_medium,
    encode_video_counters,
    encode_video_header_femto,
    encode_video_header_nano,
    encode_video_resolution,
    encode_video_sequence,
    encode_video_summary,
)
from app.asterix.categories.cat240_uap import CAT240_UAP
from app.asterix.uap import uap_to_dicts

_MESSAGE_TYPES = [
    {"value": 1, "label": "1 — Video Summary message"},
    {"value": 2, "label": "2 — Video message"},
]

_HEADER_FORMAT = [
    {"value": "nano", "label": "Nano (I240/040 · FRN 5)"},
    {"value": "femto", "label": "Femto (I240/041 · FRN 6)"},
]

_BLOCK_FORMAT = [
    {"value": "low", "label": "Low volume (I240/050 · FRN 9, ≤1020 B)"},
    {"value": "medium", "label": "Medium volume (I240/051 · FRN 10)"},
    {"value": "high", "label": "High volume (I240/052 · FRN 11)"},
]

_RESOLUTION_OPTIONS = [
    {"value": 1, "label": "1 — Monobit (1 bit)"},
    {"value": 2, "label": "2 — Low (2 bits)"},
    {"value": 3, "label": "3 — Medium (4 bits)"},
    {"value": 4, "label": "4 — High (8 bits)"},
    {"value": 5, "label": "5 — Very high (16 bits)"},
    {"value": 6, "label": "6 — Ultra high (32 bits)"},
]

_YES_NO = [
    {"value": 1, "label": "Yes — set FRN in FSPEC"},
    {"value": 0, "label": "No"},
]


def _frn_label(frn: int, item_id: str, name: str) -> str:
    return f"FRN {frn} · I240/{item_id} {name}" if item_id else name


class Cat240(AsterixCategory):
    """Radar video transmission per Eurocontrol Cat 240 default UAP."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=240,
            name="Radar Video Transmission",
            edition="1.3",
            description=(
                "Monoradar primary video (radial video cells) per Eurocontrol "
                "ASTERIX Part 14 Category 240 Edition 1.3."
            ),
            fields=[
                FieldDefinition(
                    id="data_source",
                    label=_frn_label(1, "010", "Data Source Identifier"),
                    field_type=FieldType.COMPOUND,
                    default={"sac": 2, "sic": 1},
                    uap_frn=1,
                    item_id="010",
                    fields=[
                        FieldDefinition(id="sac", label="SAC", field_type=FieldType.UINT8, default=2),
                        FieldDefinition(id="sic", label="SIC", field_type=FieldType.UINT8, default=1),
                    ],
                ),
                FieldDefinition(
                    id="message_type",
                    label=_frn_label(2, "000", "Message Type"),
                    field_type=FieldType.ENUM,
                    default=2,
                    options=_MESSAGE_TYPES,
                    uap_frn=2,
                    item_id="000",
                ),
                FieldDefinition(
                    id="video_sequence",
                    label=_frn_label(3, "020", "Video Record Header"),
                    field_type=FieldType.UINT32,
                    default=1,
                    description="Message sequence identifier (video messages only)",
                    min_value=0,
                    max_value=0xFFFFFFFF,
                    uap_frn=3,
                    item_id="020",
                ),
                FieldDefinition(
                    id="video_summary",
                    label=_frn_label(4, "030", "Video Summary"),
                    field_type=FieldType.STRING,
                    default="OBELIX-RADAR-VIDEO-1.0",
                    description="ASCII metadata (video summary messages only)",
                    uap_frn=4,
                    item_id="030",
                ),
                FieldDefinition(
                    id="header_format",
                    label="Video header format",
                    field_type=FieldType.ENUM,
                    default="nano",
                    options=_HEADER_FORMAT,
                ),
                FieldDefinition(
                    id="video_header",
                    label="Video Header (Nano / Femto)",
                    field_type=FieldType.COMPOUND,
                    default={
                        "start_az_deg": 0.0,
                        "end_az_deg": 2.0,
                        "start_range_cells": 0,
                        "cell_duration_ns": 1000,
                        "cell_duration_fs": 1_000_000,
                    },
                    uap_frn=5,
                    item_id="040",
                    fields=[
                        FieldDefinition(
                            id="start_az_deg",
                            label="Start azimuth (°)",
                            field_type=FieldType.FLOAT,
                            default=0.0,
                            min_value=0.0,
                            max_value=360.0,
                            unit="°",
                        ),
                        FieldDefinition(
                            id="end_az_deg",
                            label="End azimuth (°)",
                            field_type=FieldType.FLOAT,
                            default=2.0,
                            min_value=0.0,
                            max_value=360.0,
                            unit="°",
                        ),
                        FieldDefinition(
                            id="start_range_cells",
                            label="Start range (cells)",
                            field_type=FieldType.UINT32,
                            default=0,
                            min_value=0,
                            max_value=0xFFFFFFFF,
                        ),
                        FieldDefinition(
                            id="cell_duration_ns",
                            label="Cell duration (ns)",
                            field_type=FieldType.UINT32,
                            default=1000,
                            description="Used with Nano header (I240/040)",
                            min_value=0,
                            max_value=0xFFFFFFFF,
                            unit="ns",
                        ),
                        FieldDefinition(
                            id="cell_duration_fs",
                            label="Cell duration (fs)",
                            field_type=FieldType.UINT32,
                            default=1_000_000,
                            description="Used with Femto header (I240/041)",
                            min_value=0,
                            max_value=0xFFFFFFFF,
                        ),
                    ],
                ),
                FieldDefinition(
                    id="video_resolution",
                    label=_frn_label(7, "048", "Video Resolution & Compression"),
                    field_type=FieldType.COMPOUND,
                    default={"compression": 0, "resolution": 4},
                    uap_frn=7,
                    item_id="048",
                    fields=[
                        FieldDefinition(
                            id="compression",
                            label="Compression applied (C)",
                            field_type=FieldType.ENUM,
                            default=0,
                            options=[
                                {"value": 0, "label": "No compression"},
                                {"value": 1, "label": "Compression applied"},
                            ],
                        ),
                        FieldDefinition(
                            id="resolution",
                            label="Bit resolution (RES)",
                            field_type=FieldType.ENUM,
                            default=4,
                            options=_RESOLUTION_OPTIONS,
                        ),
                    ],
                ),
                FieldDefinition(
                    id="video_block_format",
                    label="Video block format",
                    field_type=FieldType.ENUM,
                    default="low",
                    options=_BLOCK_FORMAT,
                ),
                FieldDefinition(
                    id="video_cells_hex",
                    label="Video cells (hex)",
                    field_type=FieldType.STRING,
                    default="",
                    description=(
                        "Concatenated cell payloads in hex. Low block: 8 hex digits (4 B) per cell. "
                        "Leave empty for a built-in synthetic radial."
                    ),
                ),
                FieldDefinition(
                    id="include_time_of_day",
                    label="Include Time of Day (FRN 12)",
                    field_type=FieldType.ENUM,
                    default=1,
                    options=_YES_NO,
                    uap_frn=12,
                    item_id="140",
                    include_flag=True,
                ),
                FieldDefinition(
                    id="time_of_day",
                    label=_frn_label(12, "140", "Time of Day"),
                    field_type=FieldType.FLOAT,
                    default=36000.0,
                    min_value=0.0,
                    max_value=86400.0,
                    unit="s",
                    uap_frn=12,
                    item_id="140",
                ),
            ],
            uap=uap_to_dicts(CAT240_UAP),
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        message_type = int(field_values.get("message_type", 2))
        present_frns: list[int] = [1, 2]
        items_by_frn: dict[int, bytes] = {
            1: encode_data_source(field_values.get("data_source", {})),
            2: encode_message_type(message_type),
        }

        if message_type == 1:
            present_frns.append(4)
            items_by_frn[4] = encode_video_summary(str(field_values.get("video_summary", "")))
        else:
            present_frns.extend([3, 7, 8])
            items_by_frn[3] = encode_video_sequence(int(field_values.get("video_sequence", 1)))

            header_format = str(field_values.get("header_format", "nano"))
            header = field_values.get("video_header", {})
            if header_format == "femto":
                present_frns.append(6)
                items_by_frn[6] = encode_video_header_femto(header)
            else:
                present_frns.append(5)
                items_by_frn[5] = encode_video_header_nano(header)

            items_by_frn[7] = encode_video_resolution(field_values.get("video_resolution", {}))

            cells_hex = str(field_values.get("video_cells_hex", ""))
            block_format = str(field_values.get("video_block_format", "low"))
            if block_format == "medium":
                block = encode_video_block_medium(cells_hex)
                present_frns.append(10)
                items_by_frn[10] = block
            elif block_format == "high":
                block = encode_video_block_high(cells_hex)
                present_frns.append(11)
                items_by_frn[11] = block
            else:
                block = encode_video_block_low(cells_hex)
                present_frns.append(9)
                items_by_frn[9] = block

            nb_octets, nb_cells = counters_from_block(block)
            items_by_frn[8] = encode_video_counters(nb_octets, nb_cells)

            if int(field_values.get("include_time_of_day", 0)) == 1:
                present_frns.append(12)
                items_by_frn[12] = encode_time_of_day(float(field_values.get("time_of_day", 0.0)))

        present_frns.sort()
        ordered = [items_by_frn[frn] for frn in present_frns]
        return build_fspec(present_frns) + b"".join(ordered)
