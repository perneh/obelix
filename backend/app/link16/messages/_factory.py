"""Factory for Link 16 J-message encoder plugins."""

from __future__ import annotations

from typing import Any

from app.asterix.base import FieldDefinition
from app.link16.base import Link16Message, MessageDefinition, WordLayoutEntry
from app.link16.encoding.common import encode_field_block, encode_message_header


def make_j_message_class(
    *,
    j_series: str,
    name: str,
    description: str,
    npg: int,
    fields: list[FieldDefinition],
    word_layout: list[WordLayoutEntry] | None = None,
    edition: str = "STANAG 5516 Ed 11 (simulated)",
) -> type[Link16Message]:
    """Create a Link16Message plugin with schema-driven encoding."""
    family = j_series.split(".", 1)[0]
    layout = word_layout or _default_word_layout(fields)
    definition = MessageDefinition(
        j_series=j_series,
        family=family,
        name=name,
        edition=edition,
        description=description,
        npg=npg,
        fields=fields,
        word_layout=layout,
    )

    class _Message(Link16Message):
        @classmethod
        def definition(cls) -> MessageDefinition:
            return definition

        @classmethod
        def encode_record(cls, field_values: dict[str, Any]) -> bytes:
            body = encode_field_block(definition.fields, field_values)
            header = encode_message_header(j_series, max(1, (len(body) + 3) // 4))
            return header + body

    _Message.__name__ = f"J{j_series[1:].replace('.', '')}"
    _Message.__qualname__ = _Message.__name__
    return _Message


def _default_word_layout(fields: list[FieldDefinition]) -> list[WordLayoutEntry]:
    rows: list[WordLayoutEntry] = [
        WordLayoutEntry(frn=1, word=0, name="J-series / Message Label", length_bits=16, field_id=None),
    ]
    frn = 2
    word = 1
    for field in fields:
        rows.append(
            WordLayoutEntry(
                frn=frn,
                word=word,
                name=field.label,
                length_bits=32,
                field_id=field.id,
                implemented=True,
            )
        )
        frn += 1
        word += 1
    return rows
