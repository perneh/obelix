"""Persistence for message configurations (local and git-tracked shared)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.core.config import get_settings
from app.models.schemas import ConfigurationScope

T = TypeVar("T", bound=BaseModel)

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def category_dir_name(category: int) -> str:
    return f"cat{category:03d}"


def make_config_id(scope: ConfigurationScope, category: int, slug: str) -> str:
    return f"{scope.value}:{category_dir_name(category)}:{slug}"


def parse_config_id(config_id: str) -> tuple[ConfigurationScope, int, str]:
    parts = config_id.split(":", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid configuration id: {config_id}")
    scope_str, cat_dir, slug = parts
    if not cat_dir.startswith("cat") or len(cat_dir) != 6:
        raise ValueError(f"Invalid category in configuration id: {config_id}")
    category = int(cat_dir[3:])
    scope = ConfigurationScope(scope_str)
    return scope, category, slug


def validate_slug(slug: str) -> str:
    normalized = slug.strip().lower().replace("_", "-")
    if not _SLUG_RE.match(normalized):
        raise ValueError(
            "Configuration id must be lowercase alphanumeric with hyphens (e.g. system-track-wgs84)"
        )
    return normalized


def _scope_root(scope: ConfigurationScope) -> Path:
    settings = get_settings()
    if scope == ConfigurationScope.SHARED:
        return settings.shared_configurations_dir
    return settings.local_configurations_dir


def configuration_path(scope: ConfigurationScope, category: int, slug: str) -> Path:
    return _scope_root(scope) / category_dir_name(category) / f"{slug}.json"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def save_configuration(scope: ConfigurationScope, category: int, slug: str, data: BaseModel) -> Path:
    path = configuration_path(scope, category, slug)
    _ensure_parent(path)
    path.write_text(data.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_configuration(scope: ConfigurationScope, category: int, slug: str, model_cls: type[T]) -> T:
    path = configuration_path(scope, category, slug)
    if not path.exists():
        raise FileNotFoundError(f"Configuration {make_config_id(scope, category, slug)} not found")
    return model_cls.model_validate_json(path.read_text(encoding="utf-8"))


def delete_configuration(scope: ConfigurationScope, category: int, slug: str) -> None:
    path = configuration_path(scope, category, slug)
    if path.exists():
        path.unlink()


def list_configurations(
    model_cls: type[T],
    *,
    scope: ConfigurationScope | None = None,
    category: int | None = None,
) -> list[T]:
    scopes = [scope] if scope else list(ConfigurationScope)
    items: list[T] = []
    for current_scope in scopes:
        root = _scope_root(current_scope)
        if not root.exists():
            continue
        pattern = f"{category_dir_name(category)}/*.json" if category else "cat*/*.json"
        for path in sorted(root.glob(pattern)):
            try:
                items.append(model_cls.model_validate_json(path.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, ValueError):
                continue
    return items
