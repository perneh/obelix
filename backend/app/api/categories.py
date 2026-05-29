from fastapi import APIRouter, HTTPException

from app.asterix.registry import encode_message_hex, get_category, list_categories

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
def get_categories() -> list[dict]:
    return [cat.to_dict() for cat in list_categories()]


@router.get("/{category}")
def get_category_detail(category: int) -> dict:
    try:
        return get_category(category).definition().to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
