"""Persistence for Link 16 message configurations."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.core.config import get_settings
from app.link16.base import j_series_slug
from app.models.schemas import ConfigurationScope

T = TypeVar("T", bound=BaseModel)

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def j_series_dir_name(j_series: str) -> str:
    return j_series_slug(j_series)


def make_config_id(scope: ConfigurationScope, j_series: str, slug: str) -> str:
    return f"{scope.value}:{j_series_dir_name(j_series)}:{slug}"


def parse_config_id(config_id: str) -> tuple[ConfigurationScope, str, str]:
    parts = config_id.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid configuration id: {config_id}")
    scope_str, series_dir, slug = parts
    if not series_dir.upper().startswith("J"):
        raise ValueError(f"Invalid J-series in configuration id: {config_id}")
    j_series = series_dir.replace("-", ".", 1) if "-" in series_dir else series_dir
    scope = ConfigurationScope(scope_str)
    return scope, j_series, slug


def validate_slug(slug: str) -> str:
    normalized = slug.strip().lower().replace("_", "-")
    if not _SLUG_RE.match(normalized):
        raise ValueError("Configuration id must be lowercase alphanumeric with hyphens")
    return normalized


def _scope_root(scope: ConfigurationScope) -> Path:
    settings = get_settings()
    if scope == ConfigurationScope.SHARED:
        return settings.shared_link16_configurations_dir
    return settings.local_link16_configurations_dir


def configuration_path(scope: ConfigurationScope, j_series: str, slug: str) -> Path:
    return _scope_root(scope) / j_series_dir_name(j_series) / f"{slug}.json"


def save_configuration(scope: ConfigurationScope, j_series: str, slug: str, data: BaseModel) -> Path:
    path = configuration_path(scope, j_series, slug)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_configuration(scope: ConfigurationScope, j_series: str, slug: str, model_cls: type[T]) -> T:
    path = configuration_path(scope, j_series, slug)
    if not path.exists():
        raise FileNotFoundError(f"Configuration {make_config_id(scope, j_series, slug)} not found")
    return model_cls.model_validate_json(path.read_text(encoding="utf-8"))


def delete_configuration(scope: ConfigurationScope, j_series: str, slug: str) -> None:
    path = configuration_path(scope, j_series, slug)
    if path.exists():
        path.unlink()


def list_configurations(*, j_series: str | None = None, scope: ConfigurationScope | None = None) -> list[dict]:
    from app.models.link16_schemas import Link16Configuration

    results: list[dict] = []
    scopes = [scope] if scope else list(ConfigurationScope)
    for scope_item in scopes:
        root = _scope_root(scope_item)
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            try:
                config = Link16Configuration.model_validate_json(path.read_text(encoding="utf-8"))
                if j_series and config.message.j_series != j_series:
                    continue
                item = config.model_dump()
                item["scope"] = scope_item.value
                item["config_id"] = make_config_id(scope_item, config.message.j_series, config.id)
                results.append(item)
            except (json.JSONDecodeError, ValueError):
                continue
    return sorted(results, key=lambda item: (item["message"]["j_series"], item["name"]))
