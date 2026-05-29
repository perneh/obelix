from fastapi import APIRouter, HTTPException

from app.asterix.registry import get_category
from app.core.motion import default_end_waypoint, default_step_distance, waypoint_from_fields
from app.models.schemas import MotionMode, StepMotion
from app.core.scenario_runner import scenario_runner
from app.models.schemas import AsterixMessage, Scenario, ScenarioRunState, StepMotion

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.post("/motion-defaults", response_model=StepMotion)
def get_motion_defaults(message: AsterixMessage) -> StepMotion:
    """Build default start/end waypoints from a message template."""
    try:
        get_category(message.category)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    start = waypoint_from_fields(message.category, message.fields)
    end = default_end_waypoint(message.category, message.fields)
    return StepMotion(
        enabled=False,
        mode=MotionMode.DIRECTION,
        waypoints=[start, end],
        heading_deg=90.0,
        step_distance=default_step_distance(message.category),
        ticks=10,
        tick_interval_ms=1000,
        update_time=True,
        derive_velocity=message.category == 62,
    )


@router.post("/run", response_model=ScenarioRunState)
async def run_scenario(scenario: Scenario) -> ScenarioRunState:
    if not scenario.steps:
        raise HTTPException(status_code=400, detail="Scenario must contain at least one step")
    try:
        return await scenario_runner.start(scenario)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/runs", response_model=list[ScenarioRunState])
def list_runs() -> list[ScenarioRunState]:
    return scenario_runner.list_states()


@router.get("/runs/{scenario_id}", response_model=ScenarioRunState)
def get_run_state(scenario_id: str) -> ScenarioRunState:
    state = scenario_runner.get_state(scenario_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"No run found for scenario {scenario_id}")
    return state


@router.post("/runs/{scenario_id}/pause", response_model=ScenarioRunState)
def pause_run(scenario_id: str) -> ScenarioRunState:
    try:
        return scenario_runner.pause(scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/runs/{scenario_id}/resume", response_model=ScenarioRunState)
def resume_run(scenario_id: str) -> ScenarioRunState:
    try:
        return scenario_runner.resume(scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/runs/{scenario_id}/stop", response_model=ScenarioRunState)
def stop_run(scenario_id: str) -> ScenarioRunState:
    try:
        return scenario_runner.stop(scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
