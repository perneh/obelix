"""Link 16 scenario file storage."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from app.core.config import get_settings
from app.models.link16_schemas import Link16Scenario

T = TypeVar("T", bound=BaseModel)


def _scenarios_dir() -> Path:
    return get_settings().link16_scenarios_dir


def save_scenario(scenario_id: str, scenario: Link16Scenario) -> Path:
    path = _scenarios_dir() / f"{scenario_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scenario.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_scenario(scenario_id: str) -> Link16Scenario:
    path = _scenarios_dir() / f"{scenario_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Link 16 scenario {scenario_id} not found")
    return Link16Scenario.model_validate_json(path.read_text(encoding="utf-8"))


def delete_scenario(scenario_id: str) -> None:
    path = _scenarios_dir() / f"{scenario_id}.json"
    if path.exists():
        path.unlink()


def list_scenarios() -> list[Link16Scenario]:
    root = _scenarios_dir()
    if not root.exists():
        return []
    scenarios: list[Link16Scenario] = []
    for path in sorted(root.glob("*.json")):
        try:
            scenarios.append(Link16Scenario.model_validate_json(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError):
            continue
    return scenarios
