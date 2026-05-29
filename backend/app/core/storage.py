"""Persistence for message templates and scenarios."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.core.config import get_settings

T = TypeVar("T", bound=BaseModel)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _save_model(path: Path, model: BaseModel) -> None:
    _ensure_dir(path.parent)
    path.write_text(model.model_dump_json(indent=2), encoding="utf-8")


def _load_model(path: Path, model_cls: type[T]) -> T:
    return model_cls.model_validate_json(path.read_text(encoding="utf-8"))


def _list_models(directory: Path, model_cls: type[T]) -> list[T]:
    if not directory.exists():
        return []
    items: list[T] = []
    for path in sorted(directory.glob("*.json")):
        try:
            items.append(_load_model(path, model_cls))
        except (json.JSONDecodeError, ValueError):
            continue
    return items


def save_template(template_id: str, data: BaseModel) -> Path:
    path = get_settings().templates_dir / f"{template_id}.json"
    _save_model(path, data)
    return path


def load_template(template_id: str, model_cls: type[T]) -> T:
    path = get_settings().templates_dir / f"{template_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Template {template_id} not found")
    return _load_model(path, model_cls)


def list_templates(model_cls: type[T]) -> list[T]:
    return _list_models(get_settings().templates_dir, model_cls)


def delete_template(template_id: str) -> None:
    path = get_settings().templates_dir / f"{template_id}.json"
    if path.exists():
        path.unlink()


def save_scenario(scenario_id: str, data: BaseModel, *, shared: bool = False) -> Path:
    root = get_settings().shared_scenarios_dir if shared else get_settings().scenarios_dir
    path = root / f"{scenario_id}.json"
    _save_model(path, data)
    return path


def load_scenario(scenario_id: str, model_cls: type[T], *, shared: bool = False) -> T:
    root = get_settings().shared_scenarios_dir if shared else get_settings().scenarios_dir
    path = root / f"{scenario_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Scenario {scenario_id} not found")
    return _load_model(path, model_cls)


def list_scenarios(model_cls: type[T]) -> list[T]:
    local = _list_models(get_settings().scenarios_dir, model_cls)
    shared = _list_models(get_settings().shared_scenarios_dir, model_cls)
    for item in shared:
        if hasattr(item, "tags") and "shared" not in item.tags:
            item.tags.append("shared")
    seen = {item.id for item in shared}
    merged = list(shared)
    for item in local:
        if item.id not in seen:
            merged.append(item)
    return merged


def delete_scenario(scenario_id: str) -> None:
    for shared in (True, False):
        root = get_settings().shared_scenarios_dir if shared else get_settings().scenarios_dir
        path = root / f"{scenario_id}.json"
        if path.exists():
            path.unlink()
            return
