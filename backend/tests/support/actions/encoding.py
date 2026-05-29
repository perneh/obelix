"""Encoding workflow actions."""

from __future__ import annotations

import logging
from typing import Any

from app.asterix.categories.cat015 import Cat015
from app.asterix.categories.cat016 import Cat016
from app.asterix.categories.cat034 import Cat034
from app.asterix.categories.cat048 import Cat048
from app.asterix.categories.cat062 import Cat062
from app.asterix.registry import encode_message, encode_message_hex, get_category, list_categories

logger = logging.getLogger(__name__)


def run_encode_cat015_datablock(fields: dict[str, Any]) -> bytes:
    logger.debug("Encoding Cat015 datablock with keys: %s", list(fields.keys()))
    return Cat015.encode_datablock(fields)


def run_encode_cat016_datablock(fields: dict[str, Any]) -> bytes:
    logger.debug("Encoding Cat016 datablock with keys: %s", list(fields.keys()))
    return Cat016.encode_datablock(fields)


def run_encode_cat034_datablock(fields: dict[str, Any]) -> bytes:
    logger.debug("Encoding Cat034 datablock with keys: %s", list(fields.keys()))
    return Cat034.encode_datablock(fields)


def run_encode_cat034_record(fields: dict[str, Any]) -> bytes:
    logger.debug("Encoding Cat034 record with keys: %s", list(fields.keys()))
    return Cat034.encode_record(fields)


def run_encode_cat048_datablock(fields: dict[str, Any]) -> bytes:
    logger.debug("Encoding Cat048 datablock with keys: %s", list(fields.keys()))
    return Cat048.encode_datablock(fields)


def run_encode_cat062_datablock(fields: dict[str, Any]) -> bytes:
    logger.debug("Encoding Cat062 datablock with keys: %s", list(fields.keys()))
    return Cat062.encode_datablock(fields)


def run_encode_via_registry(category: int, fields: dict[str, Any]) -> bytes:
    logger.debug("Encoding via registry category=%s", category)
    return encode_message(category, fields)


def run_encode_hex_via_registry(category: int, fields: dict[str, Any]) -> str:
    logger.debug("Encoding hex via registry category=%s", category)
    return encode_message_hex(category, fields)


def run_get_category(category: int):
    logger.debug("Resolving category=%s", category)
    return get_category(category)


def run_list_categories():
    logger.debug("Listing registered categories")
    return list_categories()
