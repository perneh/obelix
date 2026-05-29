"""HTTP assertion helpers."""

from __future__ import annotations

from typing import Any

from tests.support.actions.http import HttpResult


def assert_status(result: HttpResult, expected: int) -> None:
    assert result.status_code == expected, (
        f"Expected status {expected}, got {result.status_code}: {result.text}"
    )


def assert_status_ok(result: HttpResult) -> None:
    assert result.status_code == 200, f"Expected status 200, got {result.status_code}: {result.text}"


def assert_status_not_found(result: HttpResult) -> None:
    assert result.status_code == 404, f"Expected status 404, got {result.status_code}: {result.text}"


def assert_json_field(result: HttpResult, field: str, expected: Any) -> None:
    assert result.json is not None, "Expected JSON body"
    actual = result.json.get(field)
    assert actual == expected, f"Expected {field}={expected!r}, got {actual!r}"


def assert_categories_include_category(categories: list[dict[str, Any]], category: int) -> None:
    ids = {item["category"] for item in categories}
    assert category in ids, f"Expected category {category} in {ids}"


def assert_category_detail(category: dict[str, Any], *, category_id: int) -> None:
    assert category["category"] == category_id, f"Expected category {category_id}"
    assert "fields" in category, "Expected fields in category detail"


def assert_health_ok(result: HttpResult) -> None:
    assert_status_ok(result)
    assert isinstance(result.json, list), "Health check should return category list"


def assert_frontend_contains(result: HttpResult, text: str) -> None:
    assert_status_ok(result)
    assert text in result.text, f"Expected {text!r} in frontend response"


def assert_category_schema(result: HttpResult, *, category: int) -> None:
    assert_json_field(result, "category", category)
    fields = result.json["fields"]
    uap = result.json["uap"]
    assert isinstance(fields, list), "Expected fields to be a list"
    assert len(fields) >= 1, f"Expected at least one field definition for category {category}"
    assert isinstance(uap, list), "Expected uap to be a list"
    assert len(uap) >= 1, f"Expected at least one UAP entry for category {category}"


def assert_category_help_markdown(result: HttpResult, *, category: int) -> None:
    assert_json_field(result, "category", category)
    assert_json_field(result, "format", "markdown")
    content = result.json["content"]
    assert isinstance(content, str), "Expected markdown help content as string"
    assert f"Category {category:03d}" in content, (
        f"Expected help heading for category {category:03d} in content"
    )


def assert_encoded_datablock(result: HttpResult, *, category: int) -> None:
    assert_json_field(result, "category", category)
    length = result.json["length"]
    hex_value = result.json["hex"]
    assert isinstance(length, int) and length > 0, "Expected positive datablock length"
    assert isinstance(hex_value, str) and len(hex_value) == length * 2, (
        f"Expected hex length {length * 2}, got {len(hex_value)}"
    )
    assert all(ch in "0123456789ABCDEF" for ch in hex_value), "Expected uppercase hex payload"
