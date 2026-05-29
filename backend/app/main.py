from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import categories, encode, scenarios, send, storage
from app.core.config import get_settings

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def create_app() -> FastAPI:
    settings = get_settings()
    settings.templates_dir.mkdir(parents=True, exist_ok=True)
    settings.scenarios_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(
        title="Obelix",
        description="Web-based tool for creating, editing and sending ASTERIX messages",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(categories.router, prefix="/api")
    app.include_router(encode.router, prefix="/api")
    app.include_router(send.router, prefix="/api")
    app.include_router(scenarios.router, prefix="/api")
    app.include_router(storage.router, prefix="/api")

    if FRONTEND_DIR.exists():
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    return app


app = create_app()
