"""All categories expose a UAP table in their definition."""

import pytest

from app.asterix.registry import get_category


@pytest.mark.unit
@pytest.mark.parametrize("category", [15, 16, 34, 48, 62])
def test_category_definition_includes_uap(category):
    definition = get_category(category).definition().to_dict()
    uap = definition.get("uap")
    assert uap, f"Category {category} missing uap table"
    assert all("frn" in row for row in uap)
    assert uap[0]["frn"] == 1


@pytest.mark.unit
def test_uap_entries_link_implemented_fields_with_anchors():
    uap = get_category(62).definition().to_dict()["uap"]
    data_source = next(row for row in uap if row["frn"] == 1)
    assert data_source["field_id"] == "data_source"
    assert "data_source" in data_source["anchor_field_ids"]

    velocity = next(row for row in uap if row["frn"] == 7)
    assert "velocity" in velocity["anchor_field_ids"]
    assert "include_velocity" in velocity["anchor_field_ids"]
