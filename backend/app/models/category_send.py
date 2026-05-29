"""Per-category send request models with OpenAPI examples for FastAPI."""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from app.asterix.base import FieldDefinition, FieldType
from app.asterix.registry import get_category, list_categories
from app.models.schemas import TransportProtocol


def example_from_field_definitions(fields: list[FieldDefinition]) -> dict[str, Any]:
    """Build a JSON example from category field defaults."""
    result: dict[str, Any] = {}
    for field in fields:
        if field.field_type == FieldType.COMPOUND and field.fields:
            result[field.id] = example_from_field_definitions(field.fields)
        else:
            result[field.id] = field.default
    return result


def _model_name(category: int, suffix: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]", "", suffix.title().replace("_", "")) or "Fields"
    return f"Cat{category:03d}{safe}"


def _field_annotation(field: FieldDefinition, category: int, prefix: str) -> tuple[Any, Any]:
    if field.field_type == FieldType.COMPOUND and field.fields:
        nested = build_fields_model(category, field.fields, suffix=field.id)
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

    if field.field_type in {FieldType.UINT8, FieldType.UINT16, FieldType.UINT32}:
        return int, Field(default=field.default, **constraints)
    if field.field_type == FieldType.INT16:
        return int, Field(default=field.default, **constraints)
    if field.field_type == FieldType.FLOAT:
        return float, Field(default=field.default, **constraints)
    if field.field_type == FieldType.STRING:
        return str, Field(default=field.default, **constraints)

    return Any, Field(default=field.default, **constraints)


def build_fields_model(category: int, field_defs: list[FieldDefinition], *, suffix: str = "Fields") -> type[BaseModel]:
    """Create a typed Pydantic model for one category's field schema."""
    attrs: dict[str, Any] = {}
    for field_def in field_defs:
        attrs[field_def.id] = _field_annotation(field_def, category, suffix)
    return create_model(_model_name(category, suffix), **attrs)


def build_category_send_model(category: int) -> type[BaseModel]:
    """Create POST /api/send/{category} body model with a working OpenAPI example."""
    definition = get_category(category).definition()
    fields_model = build_fields_model(category, definition.fields)
    fields_example = example_from_field_definitions(definition.fields)
    request_example = {
        "fields": fields_example,
        "host": "host.docker.internal",
        "port": 8600,
        "protocol": "udp",
    }

    model = create_model(
        f"Cat{category:03d}SendRequest",
        __config__=ConfigDict(json_schema_extra={"examples": [request_example]}),
        fields=(
            fields_model,
            Field(description=f"Cat {category:03d} field values"),
        ),
        host=(str, Field(default="host.docker.internal", description="Destination host")),
        port=(int, Field(default=8600, ge=1, le=65535, description="Destination port")),
        protocol=(TransportProtocol, Field(default=TransportProtocol.UDP)),
    )
    return model


def all_category_send_models() -> dict[int, type[BaseModel]]:
    return {definition.category: build_category_send_model(definition.category) for definition in list_categories()}
