"""Repository-relative path helpers."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def project_path(value: str | Path) -> Path:
    """Resolve a configured path relative to the repository root."""
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path
