"""HTTP workflow actions."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HttpResult:
    status_code: int
    json: Any | None
    text: str


def run_list_categories(client) -> list[dict[str, Any]]:
    logger.debug("GET /api/categories")
    response = client.get("/api/categories")
    logger.debug("Response status=%s", response.status_code)
    if response.status_code >= 400:
        logger.error("List categories failed: status=%s body=%s", response.status_code, response.text)
    response.raise_for_status()
    return response.json()


def run_get_category_detail(client, category: int) -> dict[str, Any]:
    logger.debug("GET /api/categories/%s", category)
    response = client.get(f"/api/categories/{category}")
    logger.debug("Response status=%s", response.status_code)
    if response.status_code >= 400:
        logger.error("Get category failed: status=%s body=%s", response.status_code, response.text)
    response.raise_for_status()
    return response.json()


def run_get_category_help(client, category: int) -> HttpResult:
    logger.debug("GET /api/categories/%s/help", category)
    response = client.get(f"/api/categories/{category}/help")
    logger.debug("Response status=%s", response.status_code)
    body = response.json() if response.content else None
    if response.status_code >= 400:
        logger.error("Get category help failed: status=%s body=%s", response.status_code, response.text)
    return HttpResult(status_code=response.status_code, json=body, text=response.text)


def run_encode_message(client, payload: dict[str, Any]) -> HttpResult:
    logger.debug("POST /api/encode payload category=%s", payload.get("message", {}).get("category"))
    response = client.post("/api/encode", json=payload)
    logger.debug("Response status=%s body_len=%s", response.status_code, len(response.text))
    body = response.json() if response.content else None
    if response.status_code >= 400:
        logger.error("Encode failed: status=%s body=%s", response.status_code, response.text)
    return HttpResult(status_code=response.status_code, json=body, text=response.text)


def run_save_configuration(client, payload: dict[str, Any]) -> HttpResult:
    logger.debug("POST /api/configurations id=%s scope=%s", payload.get("id"), payload.get("scope"))
    response = client.post("/api/configurations", json=payload)
    logger.debug("Response status=%s", response.status_code)
    body = response.json() if response.content else None
    if response.status_code >= 400:
        logger.error("Save configuration failed: status=%s body=%s", response.status_code, response.text)
    return HttpResult(status_code=response.status_code, json=body, text=response.text)


def run_load_configuration(client, config_id: str) -> HttpResult:
    logger.debug("GET /api/configurations/%s", config_id)
    response = client.get(f"/api/configurations/{config_id}")
    logger.debug("Response status=%s", response.status_code)
    body = response.json() if response.content else None
    if response.status_code >= 400:
        logger.error("Load configuration failed: status=%s body=%s", response.status_code, response.text)
    return HttpResult(status_code=response.status_code, json=body, text=response.text)


def run_save_template(client, payload: dict[str, Any]) -> HttpResult:
    logger.debug("POST /api/templates id=%s", payload.get("id"))
    response = client.post("/api/templates", json=payload)
    logger.debug("Response status=%s", response.status_code)
    body = response.json() if response.content else None
    if response.status_code >= 400:
        logger.error("Save template failed: status=%s body=%s", response.status_code, response.text)
    return HttpResult(status_code=response.status_code, json=body, text=response.text)


def run_load_template(client, template_id: str) -> HttpResult:
    logger.debug("GET /api/templates/%s", template_id)
    response = client.get(f"/api/templates/{template_id}")
    logger.debug("Response status=%s", response.status_code)
    body = response.json() if response.content else None
    if response.status_code >= 400:
        logger.error("Load template failed: status=%s body=%s", response.status_code, response.text)
    return HttpResult(status_code=response.status_code, json=body, text=response.text)


def run_get_frontend(client) -> HttpResult:
    logger.debug("GET /")
    response = client.get("/")
    logger.debug("Response status=%s body_len=%s", response.status_code, len(response.text))
    return HttpResult(status_code=response.status_code, json=None, text=response.text)


def run_health_check(client) -> HttpResult:
    """Use category list as a lightweight health probe."""
    logger.info("Running health check against API")
    response = client.get("/api/categories")
    logger.debug("Health check status=%s", response.status_code)
    body = response.json() if response.content else None
    return HttpResult(status_code=response.status_code, json=body, text=response.text)
