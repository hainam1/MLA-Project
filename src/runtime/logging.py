"""Consistent application logging without third-party global state."""

from __future__ import annotations

import logging
import os


def configure_logging(level: str | None = None) -> None:
    logging.basicConfig(
        level=(level or os.getenv("CAPYVOCAB_LOG_LEVEL", "INFO")).upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        force=True,
    )
