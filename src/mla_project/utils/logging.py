"""Project logging setup."""

from __future__ import annotations

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure concise console logging without creating repository log files."""
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")
