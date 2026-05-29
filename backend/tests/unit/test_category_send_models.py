"""Unit tests for per-category send request models."""

import pytest

from app.models.category_send import all_category_send_models, build_category_send_model


@pytest.mark.unit
def test_build_category_send_models_for_all_categories():
    models = all_category_send_models()
    assert set(models) == {15, 16, 21, 34, 48, 62, 65, 240}


@pytest.mark.unit
def test_cat034_send_request_example_round_trips():
    model = build_category_send_model(34)
    example = model.model_config["json_schema_extra"]["examples"][0]
    request = model.model_validate(example)

    payload = request.model_dump()
    assert payload["fields"]["message_type"] == 1
    assert payload["fields"]["data_source"]["sac"] == 1
    assert payload["protocol"] == "udp"


@pytest.mark.unit
def test_cat021_send_request_accepts_string_enum_defaults():
    model = build_category_send_model(21)
    example = model.model_config["json_schema_extra"]["examples"][0]
    request = model.model_validate(example)
    assert request.model_dump()["fields"]["position_resolution"] == "high"


@pytest.mark.unit
def test_cat240_send_request_accepts_string_enum_defaults():
    model = build_category_send_model(240)
    example = model.model_config["json_schema_extra"]["examples"][0]
    request = model.model_validate(example)
    payload = request.model_dump()["fields"]
    assert payload["header_format"] == "nano"
    assert payload["video_block_format"] == "low"
