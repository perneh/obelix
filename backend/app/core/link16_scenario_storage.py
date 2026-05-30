"""Link 16 scenario file storage (shared library + local saves)."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.config import get_settings
from app.models.link16_schemas import Link16Scenario


def _load_from_dir(root: Path) -> list[Link16Scenario]:
    if not root.exists():
        return []
    scenarios: list[Link16Scenario] = []
    for path in sorted(root.glob("*.json")):
        try:
            scenarios.append(Link16Scenario.model_validate_json(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError):
            continue
    return scenarios


def _find_scenario_path(scenario_id: str) -> Path | None:
    settings = get_settings()
    for root in (settings.link16_scenarios_dir, settings.shared_link16_scenarios_dir):
        path = root / f"{scenario_id}.json"
        if path.exists():
            return path
    return None


def save_scenario(scenario_id: str, scenario: Link16Scenario) -> Path:
    path = get_settings().link16_scenarios_dir / f"{scenario_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(scenario.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_scenario(scenario_id: str) -> Link16Scenario:
    path = _find_scenario_path(scenario_id)
    if path is None:
        raise FileNotFoundError(f"Link 16 scenario {scenario_id} not found")
    return Link16Scenario.model_validate_json(path.read_text(encoding="utf-8"))


def delete_scenario(scenario_id: str) -> None:
    path = get_settings().link16_scenarios_dir / f"{scenario_id}.json"
    if path.exists():
        path.unlink()


def list_scenarios() -> list[Link16Scenario]:
    settings = get_settings()
    shared = _load_from_dir(settings.shared_link16_scenarios_dir)
    local = _load_from_dir(settings.link16_scenarios_dir)
    seen = {item.id for item in shared}
    merged = list(shared)
    for item in local:
        if item.id not in seen:
            merged.append(item)
    return merged
