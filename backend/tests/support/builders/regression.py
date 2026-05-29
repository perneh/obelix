"""Field builders for live API regression tests per ASTERIX category."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from tests.support.builders.encoding import (
    build_cat015_range_plot_fields,
    build_cat016_system_config_fields,
    build_cat021_adsb_fields,
    build_cat034_north_marker_fields,
    build_cat048_plot_fields,
    build_cat062_minimal_fields,
    build_cat065_sdps_status_fields,
    build_cat240_video_radial_fields,
    build_cat240_video_summary_fields,
)

FieldBuilder = Callable[[], dict[str, Any]]

# Primary encode payload per implemented category (used by regression suites).
CATEGORY_ENCODE_BUILDERS: dict[int, FieldBuilder] = {
    15: build_cat015_range_plot_fields,
    16: build_cat016_system_config_fields,
    21: build_cat021_adsb_fields,
    34: build_cat034_north_marker_fields,
    48: build_cat048_plot_fields,
    62: build_cat062_minimal_fields,
    65: build_cat065_sdps_status_fields,
    240: build_cat240_video_radial_fields,
}

IMPLEMENTED_CATEGORIES: tuple[int, ...] = tuple(sorted(CATEGORY_ENCODE_BUILDERS))


def fields_for_category(category: int) -> dict[str, Any]:
    builder = CATEGORY_ENCODE_BUILDERS.get(category)
    if builder is None:
        raise KeyError(f"No regression field builder for category {category}")
    return builder()


def cat240_summary_fields() -> dict[str, Any]:
    return build_cat240_video_summary_fields()
