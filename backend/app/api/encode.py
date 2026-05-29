from fastapi import APIRouter, HTTPException

from app.asterix.registry import encode_message, encode_message_hex
from app.models.schemas import EncodeRequest, EncodeResponse

router = APIRouter(prefix="/encode", tags=["encode"])


@router.post("", response_model=EncodeResponse)
def encode_asterix(request: EncodeRequest) -> EncodeResponse:
    try:
        data = encode_message(request.message.category, request.message.fields)
        return EncodeResponse(
            hex=encode_message_hex(request.message.category, request.message.fields),
            length=len(data),
            category=request.message.category,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
