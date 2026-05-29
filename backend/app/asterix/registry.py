"""Registry of available ASTERIX categories."""

from __future__ import annotations

from typing import Type

from app.asterix.base import AsterixCategory, CategoryDefinition
from app.asterix.categories.cat015 import Cat015
from app.asterix.categories.cat016 import Cat016
from app.asterix.categories.cat021 import Cat021
from app.asterix.categories.cat034 import Cat034
from app.asterix.categories.cat048 import Cat048
from app.asterix.categories.cat062 import Cat062

_REGISTRY: dict[int, Type[AsterixCategory]] = {
    15: Cat015,
    16: Cat016,
    21: Cat021,
    34: Cat034,
    48: Cat048,
    62: Cat062,
}


def get_category(category: int) -> Type[AsterixCategory]:
    if category not in _REGISTRY:
        raise KeyError(f"ASTERIX category {category} is not supported")
    return _REGISTRY[category]


def list_categories() -> list[CategoryDefinition]:
    return [cls.definition() for cls in _REGISTRY.values()]


def encode_message(category: int, fields: dict) -> bytes:
    return get_category(category).encode_datablock(fields)


def encode_message_hex(category: int, fields: dict) -> str:
    return get_category(category).encode_hex(fields)
