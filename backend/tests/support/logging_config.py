"""Configure logging for the test run."""

from __future__ import annotations

import logging
import os


def configure_test_logging(level: str | None = None) -> None:
    """Set up root logging for pytest sessions."""
    resolved = (level or os.environ.get("LOG_LEVEL", "WARNING")).upper()
    numeric = getattr(logging, resolved, logging.WARNING)

    logging.basicConfig(
        level=numeric,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        force=True,
    )
