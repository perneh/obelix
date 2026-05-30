"""Registry of Link 16 J-message encoders."""

from __future__ import annotations

from typing import Type

from app.link16.base import Link16Message, MessageDefinition, j_series_from_slug
from app.link16.messages.j0 import J0_MESSAGES
from app.link16.messages.j10_j15 import J10_MESSAGES, J11_MESSAGES, J14_MESSAGES, J15_MESSAGES
from app.link16.messages.j12 import J12_MESSAGES
from app.link16.messages.j13 import J13_MESSAGES
from app.link16.messages.j2 import J2_MESSAGES
from app.link16.messages.j3 import J3_MESSAGES
from app.link16.messages.j7 import J7_MESSAGES
from app.link16.messages.j9 import J9_MESSAGES

_ALL_MESSAGES: list[type[Link16Message]] = [
    *J0_MESSAGES,
    *J2_MESSAGES,
    *J3_MESSAGES,
    *J7_MESSAGES,
    *J9_MESSAGES,
    *J10_MESSAGES,
    *J11_MESSAGES,
    *J12_MESSAGES,
    *J13_MESSAGES,
    *J14_MESSAGES,
    *J15_MESSAGES,
]

_REGISTRY: dict[str, type[Link16Message]] = {cls.definition().j_series: cls for cls in _ALL_MESSAGES}


def get_message(j_series: str) -> type[Link16Message]:
    key = j_series_from_slug(j_series) if "-" in j_series and "." not in j_series else j_series
    if key not in _REGISTRY:
        raise KeyError(f"Link 16 message {j_series} is not supported")
    return _REGISTRY[key]


def list_messages() -> list[MessageDefinition]:
    return [cls.definition() for cls in _ALL_MESSAGES]


def list_families() -> list[str]:
    return sorted({definition.family for definition in list_messages()})


def encode_message(j_series: str, fields: dict) -> bytes:
    return get_message(j_series).encode_jreap(fields)


def encode_message_hex(j_series: str, fields: dict) -> str:
    return get_message(j_series).encode_hex(fields)
