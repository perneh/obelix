"""Unit tests for Link 16 help content generation."""

import pytest

from app.link16.help_content import load_message_help_content, render_message_help_markdown
from app.link16.registry import get_message


@pytest.mark.unit
def test_render_message_help_includes_title_and_fields():
    definition = get_message("J3.2").definition()
    content = render_message_help_markdown(definition)

    assert "# J3.2 – Air Track" in content
    assert "`source_ju`" in content
    assert "`track_number`" in content
    assert "8700" in content
    assert "/api/link16/send/J3-2" in content


@pytest.mark.unit
def test_load_message_help_uses_dedicated_file_for_j32():
    content = load_message_help_content("J3.2")
    assert "Air track report for the tactical picture" in content


@pytest.mark.unit
def test_load_message_help_generates_for_messages_without_file():
    content = load_message_help_content("J0.0")
    assert "# J0.0 – Network Status" in content
    assert "`network_status`" in content
