"""Encoding assertion helpers."""

from __future__ import annotations


def assert_datablock_category(data: bytes, expected: int) -> None:
    assert data[0] == expected, f"Expected category {expected}, got {data[0]}"


def assert_datablock_length(data: bytes, expected: int) -> None:
    assert len(data) == expected, f"Expected length {expected}, got {len(data)}"


def assert_hex_equals(data: bytes, expected_hex: str) -> None:
    actual = data.hex().upper()
    assert actual == expected_hex.upper(), f"Expected hex {expected_hex.upper()}, got {actual}"


def assert_length_field_matches(data: bytes) -> None:
    length = (data[1] << 8) | data[2]
    assert length == len(data), f"Length field {length} does not match datablock size {len(data)}"


def assert_fspec_byte(data: bytes, index: int, expected: int) -> None:
    assert data[index] == expected, f"Expected FSPEC byte 0x{expected:02X} at index {index}, got 0x{data[index]:02X}"


def assert_record_shorter_than(first: bytes, second: bytes) -> None:
    assert len(first) < len(second), f"Expected first record ({len(first)} B) shorter than second ({len(second)} B)"


def assert_hex_matches_bytes(hex_value: str, raw: bytes) -> None:
    assert bytes.fromhex(hex_value) == raw, "Hex string does not match raw bytes"


def assert_categories_include(categories: set[int], expected: set[int]) -> None:
    assert categories == expected, f"Expected categories {expected}, got {categories}"
