"""Pure builders for API request payloads."""

from __future__ import annotations

from typing import Any


def build_encode_request(*, category: int, fields: dict[str, Any]) -> dict[str, Any]:
    return {"message": {"category": category, "fields": fields}}


def build_category_send_request(
    *,
    fields: dict[str, Any],
    host: str = "127.0.0.1",
    port: int = 8600,
    protocol: str = "udp",
) -> dict[str, Any]:
    return {
        "fields": fields,
        "host": host,
        "port": port,
        "protocol": protocol,
    }


def build_configuration_payload(
    *,
    config_id: str,
    name: str,
    category: int,
    fields: dict[str, Any],
    scope: str = "local",
    description: str = "",
) -> dict[str, Any]:
    return {
        "id": config_id,
        "name": name,
        "description": description,
        "scope": scope,
        "message": {"category": category, "fields": fields},
    }


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
