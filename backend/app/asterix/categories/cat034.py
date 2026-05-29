"""ASTERIX Category 034 – Monoradar Service Messages (Edition 1.29)."""

from __future__ import annotations

from typing import Any

from app.asterix.base import (
    AsterixCategory,
    CategoryDefinition,
    FieldDefinition,
    FieldType,
    build_fspec,
    clamp,
)
from app.asterix.categories.cat034_uap import CAT034_UAP
from app.asterix.uap import uap_to_dicts

MESSAGE_TYPES = [
    {"value": 1, "label": "North marker message"},
    {"value": 2, "label": "Sector crossing message"},
    {"value": 3, "label": "Geographical filtering message"},
    {"value": 4, "label": "Jamming strobe message"},
]


class Cat034(AsterixCategory):
    """Monoradar service messages – North marker and sector crossing."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=34,
            name="Monoradar Service Messages",
            edition="1.29",
            description=(
                "Service messages from a monoradar station, including north marker "
                "and sector crossing messages."
            ),
            fields=[
                FieldDefinition(
                    id="message_type",
                    label="Message Type (I034/000)",
                    field_type=FieldType.ENUM,
                    default=1,
                    description="Type of service message",
                    options=MESSAGE_TYPES,
                    uap_frn=1,
                    item_id="000",
                ),
                FieldDefinition(
                    id="data_source",
                    label="Data Source Identifier (I034/010)",
                    field_type=FieldType.COMPOUND,
                    default={"sac": 1, "sic": 1},
                    description="System Area Code and System Identification Code",
                    uap_frn=2,
                    item_id="010",
                    fields=[
                        FieldDefinition(
                            id="sac",
                            label="SAC",
                            field_type=FieldType.UINT8,
                            default=1,
                            min_value=0,
                            max_value=255,
                        ),
                        FieldDefinition(
                            id="sic",
                            label="SIC",
                            field_type=FieldType.UINT8,
                            default=1,
                            min_value=0,
                            max_value=255,
                        ),
                    ],
                ),
                FieldDefinition(
                    id="azimuth",
                    label="Antenna Azimuth (I034/020)",
                    field_type=FieldType.FLOAT,
                    default=0.0,
                    description="Antenna azimuth in degrees (required for sector crossing)",
                    min_value=0.0,
                    max_value=360.0,
                    unit="°",
                    uap_frn=3,
                    item_id="020",
                ),
            ],
            uap=uap_to_dicts(CAT034_UAP),
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        message_type = int(field_values.get("message_type", 1))
        data_source = field_values.get("data_source", {})
        sac = clamp(int(data_source.get("sac", 1)), 0, 255)
        sic = clamp(int(data_source.get("sic", 1)), 0, 255)

        present_frns = [1, 2]
        items: list[bytes] = [
            bytes([clamp(message_type, 1, 255)]),
            bytes([sac, sic]),
        ]

        if message_type == 2:
            azimuth_deg = float(field_values.get("azimuth", 0.0))
            azimuth_raw = clamp(int(round(azimuth_deg * 65536 / 360)), 0, 65535)
            present_frns.append(3)
            items.append(bytes([(azimuth_raw >> 8) & 0xFF, azimuth_raw & 0xFF]))

        return build_fspec(present_frns) + b"".join(items)
