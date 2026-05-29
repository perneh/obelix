"""API for built-in realistic scenario templates."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import Scenario, ScenarioTemplateParams
from app.scenarios.templates import TemplateParams, build_template, list_template_catalog

router = APIRouter(prefix="/scenario-templates", tags=["scenario-templates"])


@router.get("")
def get_template_catalog() -> list[dict]:
    return list_template_catalog()


@router.get("/{template_id}", response_model=Scenario)
def get_template_scenario(template_id: str) -> Scenario:
    try:
        return build_template(template_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{template_id}/build", response_model=Scenario)
def build_custom_scenario(template_id: str, params: ScenarioTemplateParams) -> Scenario:
    try:
        scenario = build_template(
            template_id,
            TemplateParams(
                tick_interval_ms=params.tick_interval_ms,
                ticks=params.ticks,
                jas_track_number=params.jas_track_number,
                mig_track_number=params.mig_track_number,
                jas_mode3a=params.jas_mode3a,
                mig_mode3a=params.mig_mode3a,
                jas_flight_level=params.jas_flight_level,
                mig_flight_level=params.mig_flight_level,
                loop_count=params.loop_count,
                host=params.host,
                port=params.port,
            ),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    scenario.template_id = template_id
    if params.scenario_id:
        scenario.id = params.scenario_id
    if params.scenario_name:
        scenario.name = params.scenario_name
    return scenario
