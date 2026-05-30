"""Link 16 J-message API — list, encode, send."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.link16.base import j_series_from_slug, j_series_slug
from app.link16.registry import encode_message, encode_message_hex, get_message, list_messages
from app.models.link16_message_send import build_j_series_send_model
from app.core import link16_configuration_storage, link16_scenario_storage
from app.core.link16_scenario_runner import link16_scenario_runner
from app.models.link16_schemas import (
    Link16Configuration,
    Link16EncodeRequest,
    Link16EncodeResponse,
    Link16Scenario,
    Link16SendRequest,
    Link16SendResponse,
)
from app.models.schemas import ConfigurationScope, ScenarioRunState
from app.models.schemas import TransportProtocol
from app.transport.sender import send_tcp, send_udp

DOCS_LINK16_DIR = Path(__file__).resolve().parents[3] / "docs" / "link16"

router = APIRouter(prefix="/link16", tags=["link16"])


async def execute_link16_send(
    *,
    j_series: str,
    fields: dict[str, Any],
    host: str,
    port: int,
    protocol: TransportProtocol,
) -> Link16SendResponse:
    try:
        data = encode_message(j_series, fields)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        if protocol == TransportProtocol.UDP:
            await send_udp(data, host, port)
        else:
            await send_tcp(data, host, port)
    except OSError as exc:
        raise HTTPException(status_code=502, detail=f"Send failed: {exc}") from exc

    return Link16SendResponse(
        success=True,
        bytes_sent=len(data),
        host=host,
        port=port,
        protocol=protocol,
        j_series=j_series,
    )


@router.get("/messages")
def get_link16_messages() -> list[dict]:
    return [message.to_dict() for message in list_messages()]


@router.get("/families")
def get_link16_families() -> dict[str, list[str]]:
    families: dict[str, list[str]] = {}
    for message in list_messages():
        families.setdefault(message.family, []).append(message.j_series)
    for items in families.values():
        items.sort()
    return families


@router.get("/messages/{j_series}")
def get_link16_message_detail(j_series: str) -> dict:
    try:
        return get_message(j_series_from_slug(j_series)).definition().to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/messages/{j_series}/help")
def get_link16_message_help(j_series: str) -> dict:
    series = j_series_from_slug(j_series)
    try:
        get_message(series)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    slug = j_series_slug(series).lower()
    help_path = DOCS_LINK16_DIR / f"{slug}.md"
    if not help_path.is_file():
        readme = DOCS_LINK16_DIR / "README.md"
        content = readme.read_text(encoding="utf-8") if readme.is_file() else f"# {series}\n\nNo dedicated help page yet."
        return {"j_series": series, "format": "markdown", "content": content}

    return {
        "j_series": series,
        "format": "markdown",
        "content": help_path.read_text(encoding="utf-8"),
    }


@router.post("/encode", response_model=Link16EncodeResponse)
def encode_link16(request: Link16EncodeRequest) -> Link16EncodeResponse:
    series = request.message.j_series
    try:
        data = encode_message(series, request.message.fields)
        return Link16EncodeResponse(
            hex=encode_message_hex(series, request.message.fields),
            length=len(data),
            j_series=series,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/send", response_model=Link16SendResponse, summary="Send any Link 16 J-message")
async def send_link16(request: Link16SendRequest) -> Link16SendResponse:
    return await execute_link16_send(
        j_series=request.message.j_series,
        fields=request.message.fields,
        host=request.host,
        port=request.port,
        protocol=request.protocol,
    )


def _make_j_series_send_handler(j_series: str, RequestModel: type[BaseModel]):
    async def send_j_series_message(body: RequestModel) -> Link16SendResponse:
        payload = body.model_dump()
        fields = payload.pop("fields")
        return await execute_link16_send(j_series=j_series, fields=fields, **payload)

    slug = j_series_slug(j_series).replace("-", "")
    send_j_series_message.__name__ = f"send_{slug}"
    send_j_series_message.__annotations__["body"] = RequestModel
    return send_j_series_message


def _register_j_series_send_routes() -> None:
    for definition in list_messages():
        series = definition.j_series
        request_model = build_j_series_send_model(series)
        router.add_api_route(
            f"/send/{j_series_slug(series)}",
            _make_j_series_send_handler(series, request_model),
            methods=["POST"],
            response_model=Link16SendResponse,
            summary=f"Send {series} – {definition.name}",
            description=(
                f"Encode and send Link 16 {series} ({definition.name}) in a JREAP-C simple envelope. "
                "Includes typed field schema and Swagger example."
            ),
            name=f"send_{j_series_slug(series).replace('-', '_')}",
        )


_register_j_series_send_routes()


@router.get("/configurations", response_model=list[Link16Configuration])
def list_link16_configurations(
    j_series: str | None = None,
    scope: ConfigurationScope | None = None,
) -> list[Link16Configuration]:
    return [
        Link16Configuration.model_validate(item)
        for item in link16_configuration_storage.list_configurations(j_series=j_series, scope=scope)
    ]


@router.post("/configurations", response_model=Link16Configuration)
def save_link16_configuration(config: Link16Configuration) -> Link16Configuration:
    slug = link16_configuration_storage.validate_slug(config.id)
    link16_configuration_storage.save_configuration(
        config.scope,
        config.message.j_series,
        slug,
        config,
    )
    config.id = slug
    return config


@router.get("/configurations/{config_id:path}", response_model=Link16Configuration)
def get_link16_configuration(config_id: str) -> Link16Configuration:
    try:
        scope, j_series, slug = link16_configuration_storage.parse_config_id(config_id)
        return link16_configuration_storage.load_configuration(scope, j_series, slug, Link16Configuration)
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/configurations/{config_id:path}")
def delete_link16_configuration(config_id: str) -> dict[str, str]:
    try:
        scope, j_series, slug = link16_configuration_storage.parse_config_id(config_id)
        link16_configuration_storage.delete_configuration(scope, j_series, slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "deleted", "id": config_id}


@router.post("/scenarios/validate", response_model=Link16Scenario)
def validate_link16_scenario(scenario: Link16Scenario) -> Link16Scenario:
    if not scenario.steps:
        raise HTTPException(status_code=400, detail="Scenario must have at least one step")
    for step in scenario.steps:
        get_message(step.message.j_series)
    return scenario


@router.post("/scenarios/run", response_model=ScenarioRunState)
async def run_link16_scenario(scenario: Link16Scenario) -> ScenarioRunState:
    if not scenario.steps:
        raise HTTPException(status_code=400, detail="Scenario must have at least one step")
    try:
        return await link16_scenario_runner.start(scenario)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/scenarios/runs", response_model=list[ScenarioRunState])
def list_link16_runs() -> list[ScenarioRunState]:
    return link16_scenario_runner.list_states()


@router.get("/scenarios/runs/{scenario_id}", response_model=ScenarioRunState)
def get_link16_run_state(scenario_id: str) -> ScenarioRunState:
    state = link16_scenario_runner.get_state(scenario_id)
    if state is None:
        raise HTTPException(status_code=404, detail=f"No run found for scenario {scenario_id}")
    return state


@router.post("/scenarios/runs/{scenario_id}/pause", response_model=ScenarioRunState)
def pause_link16_run(scenario_id: str) -> ScenarioRunState:
    try:
        return link16_scenario_runner.pause(scenario_id)
    except (KeyError, RuntimeError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/scenarios/runs/{scenario_id}/resume", response_model=ScenarioRunState)
def resume_link16_run(scenario_id: str) -> ScenarioRunState:
    try:
        return link16_scenario_runner.resume(scenario_id)
    except (KeyError, RuntimeError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/scenarios/runs/{scenario_id}/stop", response_model=ScenarioRunState)
def stop_link16_run(scenario_id: str) -> ScenarioRunState:
    try:
        return link16_scenario_runner.stop(scenario_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/saved-scenarios", response_model=list[Link16Scenario])
def list_saved_link16_scenarios() -> list[Link16Scenario]:
    return link16_scenario_storage.list_scenarios()


@router.post("/saved-scenarios", response_model=Link16Scenario)
def save_link16_scenario(scenario: Link16Scenario) -> Link16Scenario:
    link16_scenario_storage.save_scenario(scenario.id, scenario)
    return scenario


@router.get("/saved-scenarios/{scenario_id}", response_model=Link16Scenario)
def get_saved_link16_scenario(scenario_id: str) -> Link16Scenario:
    try:
        return link16_scenario_storage.load_scenario(scenario_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete("/saved-scenarios/{scenario_id}")
def delete_saved_link16_scenario(scenario_id: str) -> dict[str, str]:
    link16_scenario_storage.delete_scenario(scenario_id)
    return {"status": "deleted", "id": scenario_id}
