"""Pure builders for API request payloads."""

from __future__ import annotations

from typing import Any


def build_encode_request(*, category: int, fields: dict[str, Any]) -> dict[str, Any]:
    return {"message": {"category": category, "fields": fields}}


def build_template_payload(
    *,
    template_id: str,
    name: str,
    category: int,
    fields: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": template_id,
        "name": name,
        "message": {"category": category, "fields": fields},
    }
