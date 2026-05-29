from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.asterix.registry import get_category, list_categories

DOCS_CATEGORIES_DIR = Path(__file__).resolve().parents[3] / "docs" / "categories"

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


@router.get("/{category}/help")
def get_category_help(category: int) -> dict:
    """Return markdown help for a supported category."""
    try:
        get_category(category)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    help_path = DOCS_CATEGORIES_DIR / f"cat{category:03d}.md"
    if not help_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"No help document for category {category}",
        )

    return {
        "category": category,
        "format": "markdown",
        "content": help_path.read_text(encoding="utf-8"),
    }
