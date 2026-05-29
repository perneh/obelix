from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.asterix.registry import encode_message, list_categories
from app.models.category_send import build_category_send_model
from app.models.schemas import SendRequest, SendResponse, TransportProtocol
from app.transport.sender import send_tcp, send_udp

router = APIRouter(prefix="/send", tags=["send"])


async def execute_send(
    *,
    category: int,
    fields: dict[str, Any],
    host: str,
    port: int,
    protocol: TransportProtocol,
) -> SendResponse:
    try:
        data = encode_message(category, fields)
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

    return SendResponse(
        success=True,
        bytes_sent=len(data),
        host=host,
        port=port,
        protocol=protocol,
    )


@router.post("", response_model=SendResponse, summary="Send any ASTERIX category")
async def send_asterix(request: SendRequest) -> SendResponse:
    return await execute_send(
        category=request.message.category,
        fields=request.message.fields,
        host=request.host,
        port=request.port,
        protocol=request.protocol,
    )


def _make_category_send_handler(category: int, RequestModel: type[BaseModel]):
    async def send_category_message(body: RequestModel) -> SendResponse:
        payload = body.model_dump()
        fields = payload.pop("fields")
        return await execute_send(category=category, fields=fields, **payload)

    send_category_message.__name__ = f"send_cat_{category:03d}"
    send_category_message.__annotations__["body"] = RequestModel
    return send_category_message


def _register_category_send_routes() -> None:
    for definition in list_categories():
        category = definition.category
        request_model = build_category_send_model(category)
        router.add_api_route(
            f"/{category}",
            _make_category_send_handler(category, request_model),
            methods=["POST"],
            response_model=SendResponse,
            summary=f"Send Cat {category:03d} – {definition.name}",
            description=(
                f"Encode and send ASTERIX Category {category:03d} ({definition.name}). "
                "The request body includes a typed field schema and a ready-to-use example for /docs."
            ),
            name=f"send_cat_{category:03d}",
        )


_register_category_send_routes()
