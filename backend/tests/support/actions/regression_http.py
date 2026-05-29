"""Thin httpx helpers for regression tests — endpoint path is passed by the test."""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TIMEOUT = 10.0


def _url(address: str, port: int, path: str) -> str:
    return f"http://{address}:{port}{path}"


def _json_ok(response: httpx.Response, path: str) -> Any:
    if response.status_code != 200:
        raise RuntimeError(f"{path}: HTTP {response.status_code}: {response.text}")
    return response.json() if response.content else None


def _text_ok(response: httpx.Response, path: str) -> str:
    if response.status_code != 200:
        raise RuntimeError(f"{path}: HTTP {response.status_code}: {response.text}")
    return response.text


def get(address: str, port: int, path: str, **params: Any) -> Any:
    logger.debug("GET %s at %s:%s", path, address, port)
    response = httpx.get(_url(address, port, path), params=params or None, timeout=TIMEOUT)
    return _json_ok(response, path)


def get_text(address: str, port: int, path: str) -> str:
    logger.debug("GET %s at %s:%s", path, address, port)
    response = httpx.get(_url(address, port, path), timeout=TIMEOUT)
    return _text_ok(response, path)


def post(address: str, port: int, path: str, body: dict[str, Any], **params: Any) -> Any:
    logger.debug("POST %s at %s:%s", path, address, port)
    response = httpx.post(
        _url(address, port, path),
        json=body,
        params=params or None,
        timeout=TIMEOUT,
    )
    return _json_ok(response, path)


def delete(address: str, port: int, path: str) -> Any:
    logger.debug("DELETE %s at %s:%s", path, address, port)
    response = httpx.delete(_url(address, port, path), timeout=TIMEOUT)
    return _json_ok(response, path)


def status(address: str, port: int, method: str, path: str, **kwargs: Any) -> int:
    logger.debug("%s %s at %s:%s", method, path, address, port)
    response = httpx.request(method, _url(address, port, path), timeout=TIMEOUT, **kwargs)
    return response.status_code
