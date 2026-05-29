"""Cat 065 helper encoders."""

from __future__ import annotations

from typing import Any

from app.asterix.base import clamp

_TIME_LSB = 1.0 / 128.0


def encode_data_source(data_source: dict[str, Any]) -> bytes:
    sac = clamp(int(data_source.get("sac", 1)), 0, 255)
    sic = clamp(int(data_source.get("sic", 1)), 0, 255)
    return bytes([sac, sic])


def encode_message_type(message_type: int) -> bytes:
    return bytes([clamp(message_type, 1, 3)])


def encode_service_id(service_id: int) -> bytes:
    return bytes([clamp(service_id, 0, 255)])


def encode_time_of_message(seconds: float) -> bytes:
    raw = clamp(int(round(seconds / _TIME_LSB)), 0, 0xFFFFFF)
    return _pack_uint24_be(raw)


def encode_batch_number(batch_number: int) -> bytes:
    return bytes([clamp(batch_number, 0, 255)])


def encode_sdps_configuration(status: dict[str, Any]) -> bytes:
    nogo = clamp(int(status.get("nogo", 0)), 0, 3)
    ovl = 1 if int(status.get("ovl", 0)) else 0
    tsv = 1 if int(status.get("tsv", 0)) else 0
    pss = clamp(int(status.get("pss", 1)), 0, 3)
    sttn = 1 if int(status.get("sttn", 0)) else 0
    value = (nogo << 6) | (ovl << 5) | (tsv << 4) | (pss << 2) | (sttn << 1)
    return bytes([value & 0xFF])


def encode_service_status_report(report: int) -> bytes:
    return bytes([clamp(report, 1, 16)])


def _pack_uint24_be(value: int) -> bytes:
    value &= 0xFFFFFF
    return bytes([(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])
