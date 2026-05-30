"""Link 16 base types and J-message encoder interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.asterix.base import FieldDefinition, clamp


@dataclass
class WordLayoutEntry:
    """Word layout row for the Link 16 editor (mirrors ASTERIX UAP)."""

    frn: int
    word: int
    name: str
    length_bits: int
    field_id: str | None = None
    implemented: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "frn": self.frn,
            "word": self.word,
            "name": self.name,
            "length_bits": self.length_bits,
            "field_id": self.field_id,
            "implemented": self.implemented,
        }


@dataclass
class MessageDefinition:
    """Metadata and field schema for one J-series message."""

    j_series: str
    family: str
    name: str
    edition: str
    description: str
    npg: int
    fields: list[FieldDefinition]
    word_layout: list[WordLayoutEntry] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "j_series": self.j_series,
            "family": self.family,
            "name": self.name,
            "edition": self.edition,
            "description": self.description,
            "npg": self.npg,
            "fields": [f.to_dict() for f in self.fields],
            "word_layout": [w.to_dict() for w in self.word_layout],
        }


class Link16Message(ABC):
    """Base class for Link 16 J-message encoders."""

    @classmethod
    @abstractmethod
    def definition(cls) -> MessageDefinition:
        ...

    @classmethod
    @abstractmethod
    def encode_record(cls, field_values: dict[str, Any]) -> bytes:
        ...

    @classmethod
    def encode_jreap(
        cls,
        field_values: dict[str, Any],
        *,
        source_ju: int | None = None,
    ) -> bytes:
        from app.link16.jreap import wrap_jreap

        definition = cls.definition()
        payload = cls.encode_record(field_values)
        ju = source_ju if source_ju is not None else int(field_values.get("source_ju", 1))
        npg = int(field_values.get("npg", definition.npg))
        return wrap_jreap(definition.j_series, ju, npg, payload)

    @classmethod
    def encode_hex(cls, field_values: dict[str, Any], *, source_ju: int | None = None) -> str:
        return cls.encode_jreap(field_values, source_ju=source_ju).hex().upper()


def j_series_slug(j_series: str) -> str:
    """URL-safe slug: J3.2 -> J3-2."""
    return j_series.replace(".", "-")


def j_series_from_slug(slug: str) -> str:
    """J3-2 -> J3.2 (only first hyphen becomes dot)."""
    if "." in slug:
        return slug
    parts = slug.split("-", 1)
    if len(parts) == 2 and parts[0].startswith("J") and parts[1]:
        return f"{parts[0]}.{parts[1]}"
    return slug
