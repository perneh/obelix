"""Shared User Application Profile (UAP) metadata for ASTERIX categories."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UapEntry:
    frn: int
    item_id: str | None
    name: str
    length: str
    field_id: str | None = None
    related_field_ids: tuple[str, ...] = ()
    mandatory: bool = False
    spare: bool = False

    def anchor_field_ids(self) -> list[str]:
        if self.spare or not self.field_id:
            return list(self.related_field_ids)
        ids = [self.field_id]
        for related in self.related_field_ids:
            if related not in ids:
                ids.append(related)
        return ids

    def to_dict(self) -> dict[str, Any]:
        anchors = self.anchor_field_ids()
        return {
            "frn": self.frn,
            "item_id": self.item_id,
            "name": self.name,
            "length": self.length,
            "field_id": self.field_id,
            "related_field_ids": list(self.related_field_ids),
            "anchor_field_ids": anchors,
            "mandatory": self.mandatory,
            "spare": self.spare,
            "implemented": bool(anchors) and not self.spare,
        }


def uap_to_dicts(entries: tuple[UapEntry, ...]) -> list[dict[str, Any]]:
    return [entry.to_dict() for entry in entries]
