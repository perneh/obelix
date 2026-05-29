"""HTTP assertion helpers."""

from __future__ import annotations

from typing import Any

from tests.support.actions.http import HttpResult


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
