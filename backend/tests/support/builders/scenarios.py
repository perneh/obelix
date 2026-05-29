"""Pure builders for scenario API payloads."""

from __future__ import annotations

from typing import Any

from tests.support.builders.encoding import build_cat034_north_marker_fields

BALTIC_TEMPLATE_IDS = frozenset({"jas-bromma-visby", "mig-kaliningrad-visby", "baltic-combined"})


def build_minimal_scenario(scenario_id: str = "regression-validate") -> dict[str, Any]:
    return {
        "id": scenario_id,
        "name": "Regression validate",
        "transport": {"host": "127.0.0.1", "port": 8600, "protocol": "udp"},
        "loop_count": 1,
        "interval_ms": 1000,
        "steps": [
            {
                "id": "step-1",
                "name": "Cat 034",
                "message": {"category": 34, "fields": build_cat034_north_marker_fields()},
                "delay_ms": 0,
                "repeat": 1,
            }
        ],
    }
