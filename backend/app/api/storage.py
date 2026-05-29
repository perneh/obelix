from fastapi import APIRouter, HTTPException

from app.core import storage
from app.models.schemas import Scenario

router = APIRouter(tags=["storage"])


@router.get("/saved-scenarios", response_model=list[Scenario])
def list_saved_scenarios() -> list[Scenario]:
    return storage.list_scenarios(Scenario)


@router.post("/saved-scenarios", response_model=Scenario)
def save_scenario(scenario: Scenario) -> Scenario:
    storage.save_scenario(scenario.id, scenario)
    return scenario


@router.get("/saved-scenarios/{scenario_id}", response_model=Scenario)
def get_saved_scenario(scenario_id: str) -> Scenario:
    try:
        return storage.load_scenario(scenario_id, Scenario)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/saved-scenarios/{scenario_id}")
def delete_saved_scenario(scenario_id: str) -> dict[str, str]:
    storage.delete_scenario(scenario_id)
    return {"status": "deleted", "id": scenario_id}
