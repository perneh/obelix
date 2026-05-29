"""ASTERIX Category 048 – Monoradar Target Reports (Edition 1.32)."""

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
from app.asterix.categories.cat048_uap import CAT048_UAP
from app.asterix.uap import uap_to_dicts


class Cat048(AsterixCategory):
    """Monoradar target reports – basic plot with range and azimuth."""

    @classmethod
    def definition(cls) -> CategoryDefinition:
        return CategoryDefinition(
            category=48,
            name="Monoradar Target Reports",
            edition="1.32",
            description="Target reports from a monoradar including range and azimuth.",
            fields=[
                FieldDefinition(
                    id="data_source",
                    label="Data Source Identifier (I048/010)",
                    field_type=FieldType.COMPOUND,
                    default={"sac": 1, "sic": 1},
                    uap_frn=1,
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
                    id="position",
                    label="Measured Position (I048/040)",
                    field_type=FieldType.COMPOUND,
                    default={"rho_nm": 10.0, "theta_deg": 45.0},
                    description="Polar coordinates: range in NM and azimuth in degrees",
                    uap_frn=2,
                    item_id="040",
                    fields=[
                        FieldDefinition(
                            id="rho_nm",
                            label="Range (RHO)",
                            field_type=FieldType.FLOAT,
                            default=10.0,
                            min_value=0.0,
                            max_value=256.0,
                            unit="NM",
                        ),
                        FieldDefinition(
                            id="theta_deg",
                            label="Azimuth (THETA)",
                            field_type=FieldType.FLOAT,
                            default=45.0,
                            min_value=0.0,
                            max_value=360.0,
                            unit="°",
                        ),
                    ],
                ),
                FieldDefinition(
                    id="mode3a",
                    label="Mode 3/A Code (I048/070)",
                    field_type=FieldType.UINT16,
                    default=0,
                    description="SSR Mode 3/A code in octal representation (0–7777)",
                    min_value=0,
                    max_value=7777,
                    uap_frn=3,
                    item_id="070",
                ),
            ],
            uap=uap_to_dicts(CAT048_UAP),
        )

    @classmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        data_source = field_values.get("data_source", {})
        sac = clamp(int(data_source.get("sac", 1)), 0, 255)
        sic = clamp(int(data_source.get("sic", 1)), 0, 255)

        position = field_values.get("position", {})
        rho_nm = float(position.get("rho_nm", 10.0))
        theta_deg = float(position.get("theta_deg", 45.0))
        rho_raw = clamp(int(round(rho_nm * 256)), 0, 65535)
        theta_raw = clamp(int(round(theta_deg * 65536 / 360)), 0, 65535)

        mode3a = int(field_values.get("mode3a", 0))
        mode3a_octal = clamp(mode3a, 0, 7777)
        mode3a_bcd = _octal_to_bcd(mode3a_octal)

        present_frns = [1, 2, 3]
        items = [
            bytes([sac, sic]),
            bytes([(rho_raw >> 8) & 0xFF, rho_raw & 0xFF, (theta_raw >> 8) & 0xFF, theta_raw & 0xFF]),
            bytes([0x00, 0x00, 0x00, mode3a_bcd]),
        ]

        return build_fspec(present_frns) + b"".join(items)


def _octal_to_bcd(octal_value: int) -> int:
    """Convert octal Mode 3/A code to 12-bit BCD as used in I048/070."""
    digits: list[int] = []
    value = octal_value
    for _ in range(4):
        digits.append(value & 0x7)
        value >>= 3
    bcd = 0
    for digit in reversed(digits):
        bcd = (bcd << 4) | (digit & 0xF)
    return bcd & 0xFF
