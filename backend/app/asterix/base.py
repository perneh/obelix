"""Base types and encoder for ASTERIX categories."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class FieldType(str, Enum):
    UINT8 = "uint8"
    UINT16 = "uint16"
    UINT32 = "uint32"
    INT16 = "int16"
    FLOAT = "float"
    ENUM = "enum"
    COMPOUND = "compound"


@dataclass
class FieldDefinition:
    """Schema field exposed to the frontend and used during encoding."""

    id: str
    label: str
    field_type: FieldType
    default: Any
    description: str = ""
    min_value: float | None = None
    max_value: float | None = None
    unit: str | None = None
    options: list[dict[str, Any]] = field(default_factory=list)
    fields: list[FieldDefinition] = field(default_factory=list)
    uap_frn: int | None = None
    item_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "id": self.id,
            "label": self.label,
            "type": self.field_type.value,
            "default": self.default,
            "description": self.description,
        }
        if self.min_value is not None:
            result["min"] = self.min_value
        if self.max_value is not None:
            result["max"] = self.max_value
        if self.unit:
            result["unit"] = self.unit
        if self.options:
            result["options"] = self.options
        if self.fields:
            result["fields"] = [f.to_dict() for f in self.fields]
        return result


@dataclass
class CategoryDefinition:
    """Metadata and field schema for one ASTERIX category."""

    category: int
    name: str
    edition: str
    description: str
    fields: list[FieldDefinition]

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "edition": self.edition,
            "description": self.description,
            "fields": [f.to_dict() for f in self.fields],
        }


class AsterixCategory(ABC):
    """Base class for ASTERIX category encoders."""

    @classmethod
    @abstractmethod
    def definition(cls) -> CategoryDefinition:
        """Return category metadata and editable field schema."""

    @classmethod
    @abstractmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        """Encode a single ASTERIX record (FSPEC + data items, no block header)."""

    @classmethod
    def encode_datablock(cls, field_values: dict[str, Any]) -> bytes:
        """Encode a complete ASTERIX data block including CAT and LEN."""
        category = cls.definition().category
        record = cls.encode_record(field_values)
        length = 3 + len(record)
        return bytes([category, (length >> 8) & 0xFF, length & 0xFF]) + record

    @classmethod
    def encode_hex(cls, field_values: dict[str, Any]) -> str:
        return cls.encode_datablock(field_values).hex().upper()


def build_fspec(present_frns: list[int]) -> bytes:
    """Build FSPEC bytes from 1-based FRN indices."""
    if not present_frns:
        raise ValueError("At least one data item must be present")

    max_frn = max(present_frns)
    num_bytes = (max_frn + 6) // 7
    fspec = bytearray(num_bytes)

    for frn in present_frns:
        byte_index = (frn - 1) // 7
        bit_index = 7 - ((frn - 1) % 7)
        fspec[byte_index] |= 1 << bit_index

    for i in range(num_bytes - 1):
        fspec[i] |= 0x01

    return bytes(fspec)


def clamp(value: int, min_val: int, max_val: int) -> int:
    return max(min_val, min(max_val, value))
