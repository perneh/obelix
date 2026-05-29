from fastapi import APIRouter, HTTPException

from app.core import storage
from app.models.schemas import Scenario

router = APIRouter(tags=["storage"])


@router.get("/saved-scenarios", response_model=list[Scenario])
def list_saved_scenarios() -> list[Scenario]:
    return storage.list_scenarios(Scenario)


@router.post("/saved-scenarios", response_model=Scenario)
def save_scenario(scenario: Scenario, scope: str = "local") -> Scenario:
    shared = scope == "shared"
    storage.save_scenario(scenario.id, scenario, shared=shared)
    return scenario


@router.get("/saved-scenarios/{scenario_id}", response_model=Scenario)
def get_saved_scenario(scenario_id: str) -> Scenario:
    for shared in (True, False):
        try:
            return storage.load_scenario(scenario_id, Scenario, shared=shared)
        except FileNotFoundError:
            continue
    raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")


@router.delete("/saved-scenarios/{scenario_id}")
def delete_saved_scenario(scenario_id: str) -> dict[str, str]:
    storage.delete_scenario(scenario_id)
    return {"status": "deleted", "id": scenario_id}
