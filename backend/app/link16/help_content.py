"""Link 16 message help — markdown files with schema-generated fallback."""

from __future__ import annotations

import json
from pathlib import Path

from app.asterix.base import FieldDefinition, FieldType
from app.link16.base import MessageDefinition, j_series_slug
from app.link16.registry import get_message

DOCS_LINK16_DIR = Path(__file__).resolve().parents[3] / "docs" / "link16"


def _field_type_label(field: FieldDefinition) -> str:
    if field.field_type == FieldType.ENUM and field.options:
        return "enum"
    if field.field_type == FieldType.COMPOUND:
        return "compound"
    return field.field_type.value


def _field_default_repr(field: FieldDefinition) -> str:
    if field.field_type == FieldType.COMPOUND:
        return json.dumps(field.default, ensure_ascii=False)
    if field.field_type == FieldType.ENUM and field.options:
        match = next((opt for opt in field.options if opt["value"] == field.default), None)
        if match:
            return match["label"]
    return repr(field.default)


def _render_fields_table(fields: list[FieldDefinition], indent: int = 0) -> list[str]:
    lines = [
        "| Field | Type | Default | Description |",
        "|-------|------|---------|-------------|",
    ]
    for field in fields:
        label = field.label or field.id
        if indent:
            label = f"{'  ' * indent}↳ {label}"
        description = field.description or "—"
        if field.unit:
            description = f"{description} ({field.unit})" if description != "—" else field.unit
        lines.append(
            f"| `{field.id}` | {_field_type_label(field)} | {_field_default_repr(field)} | {description} |"
        )
        if field.field_type == FieldType.COMPOUND and field.fields:
            lines.extend(_render_fields_table(field.fields, indent + 1)[2:])
    return lines


def render_message_help_markdown(definition: MessageDefinition) -> str:
    """Build markdown help from the J-message field schema."""
    lines = [
        f"# {definition.j_series} – {definition.name}",
        "",
        definition.description or "",
        "",
        f"**Family:** {definition.family}  ",
        f"**NPG:** {definition.npg}  ",
        f"**Edition:** {definition.edition or 'Obelix simulation subset'}",
        "",
        "## Key fields",
        "",
        *_render_fields_table(definition.fields),
        "",
        "## Transport",
        "",
        "Default Obelix Link 16 port: **8700** (JREAP-simple wrapper, magic `JREA`). "
        "Set **Source JU** to simulate different C2 participants on the same network.",
        "",
        "## Example",
        "",
        "Send via API:",
        "",
        "```bash",
        f"curl -X POST http://localhost:8000/api/link16/send/{j_series_slug(definition.j_series)} \\",
        "  -H 'Content-Type: application/json' \\",
        "  -d '{",
        '    "fields": {',
    ]

    for field in definition.fields:
        if field.field_type == FieldType.COMPOUND:
            lines.append(f'      "{field.id}": {json.dumps(field.default, ensure_ascii=False)},')
        elif field.field_type == FieldType.STRING:
            lines.append(f'      "{field.id}": {json.dumps(field.default)},')
        else:
            lines.append(f'      "{field.id}": {json.dumps(field.default)},')

    lines.extend(
        [
            "    },",
            '    "host": "host.docker.internal",',
            '    "port": 8700,',
            '    "protocol": "udp"',
            "  }'",
            "```",
            "",
            "Use **Link 16 → Message Editor** in Obelix for interactive editing.",
            "",
        ]
    )
    return "\n".join(lines)


def load_message_help_content(j_series: str) -> str:
    """Return help markdown: dedicated file if present, otherwise generated from schema."""
    message = get_message(j_series)
    definition = message.definition()
    slug = j_series_slug(definition.j_series).lower()
    help_path = DOCS_LINK16_DIR / f"{slug}.md"
    if help_path.is_file():
        return help_path.read_text(encoding="utf-8")
    return render_message_help_markdown(definition)
