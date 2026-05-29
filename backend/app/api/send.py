from fastapi import APIRouter, HTTPException

from app.asterix.registry import encode_message
from app.models.schemas import SendRequest, SendResponse
from app.transport.sender import TransportProtocol, send_tcp, send_udp

router = APIRouter(prefix="/send", tags=["send"])


@router.post("", response_model=SendResponse)
async def send_asterix(request: SendRequest) -> SendResponse:
    try:
        data = encode_message(request.message.category, request.message.fields)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        if request.protocol == TransportProtocol.UDP:
            await send_udp(data, request.host, request.port)
        else:
            await send_tcp(data, request.host, request.port)
    except OSError as exc:
        raise HTTPException(status_code=502, detail=f"Send failed: {exc}") from exc

    return SendResponse(
        success=True,
        bytes_sent=len(data),
        host=request.host,
        port=request.port,
        protocol=request.protocol,
    )
