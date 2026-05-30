"""Per J-series send request models with OpenAPI examples."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from app.asterix.base import FieldDefinition, FieldType
from app.link16.base import j_series_slug
from app.link16.registry import get_message, list_messages
from app.models.schemas import TransportProtocol


def example_from_field_definitions(fields: list[FieldDefinition]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for field in fields:
        if field.field_type == FieldType.COMPOUND and field.fields:
            result[field.id] = example_from_field_definitions(field.fields)
        else:
            result[field.id] = field.default
    return result


def _model_name(j_series: str, suffix: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]", "", j_series.replace(".", "") + suffix.title())
    return f"Link16{safe}"


def _field_annotation(field: FieldDefinition, j_series: str, prefix: str) -> tuple[Any, Any]:
    if field.field_type == FieldType.COMPOUND and field.fields:
        nested = build_fields_model(j_series, field.fields, suffix=field.id)
        example = example_from_field_definitions(field.fields)
        return (
            nested,
            Field(
                default_factory=lambda model=nested, values=example: model.model_validate(values),
                description=field.description or field.label,
            ),
        )

    if field.field_type == FieldType.COMPOUND:
        return (
            dict[str, Any],
            Field(default_factory=lambda value=field.default: dict(value), description=field.description or field.label),
        )

    constraints: dict[str, Any] = {"description": field.description or field.label}
    if field.min_value is not None:
        constraints["ge"] = field.min_value
    if field.max_value is not None:
        constraints["le"] = field.max_value

    if field.field_type == FieldType.ENUM:
        if isinstance(field.default, str) or any(isinstance(opt.get("value"), str) for opt in field.options):
            return str, Field(default=field.default, **constraints)
        return int, Field(default=field.default, **constraints)

    if field.field_type in {FieldType.UINT8, FieldType.UINT16, FieldType.UINT32, FieldType.INT16}:
        return int, Field(default=field.default, **constraints)
    if field.field_type == FieldType.FLOAT:
        return float, Field(default=field.default, **constraints)
    if field.field_type == FieldType.STRING:
        return str, Field(default=field.default, **constraints)

    return Any, Field(default=field.default, **constraints)


def build_fields_model(j_series: str, field_defs: list[FieldDefinition], *, suffix: str = "Fields") -> type[BaseModel]:
    attrs: dict[str, Any] = {}
    for field_def in field_defs:
        attrs[field_def.id] = _field_annotation(field_def, j_series, suffix)
    return create_model(_model_name(j_series, suffix), **attrs)


def build_j_series_send_model(j_series: str) -> type[BaseModel]:
    definition = get_message(j_series).definition()
    fields_model = build_fields_model(j_series, definition.fields)
    fields_example = example_from_field_definitions(definition.fields)
    request_example = {
        "fields": fields_example,
        "host": "host.docker.internal",
        "port": 8700,
        "protocol": "udp",
    }

    slug = j_series_slug(j_series).replace("-", "")
    return create_model(
        f"Link16{slug}SendRequest",
        __config__=ConfigDict(json_schema_extra={"examples": [request_example]}),
        fields=(fields_model, Field(description=f"{j_series} field values")),
        host=(str, Field(default="host.docker.internal", description="Destination host")),
        port=(int, Field(default=8700, ge=1, le=65535, description="JREAP destination port")),
        protocol=(TransportProtocol, Field(default=TransportProtocol.UDP)),
    )
