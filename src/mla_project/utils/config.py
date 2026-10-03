"""YAML configuration loading with repository-relative defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from mla_project.utils.paths import PROJECT_ROOT, project_path

CONFIG_DIR = PROJECT_ROOT / "configs"


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load one YAML mapping."""
    resolved = project_path(path)
    with resolved.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"Configuration must be a YAML mapping: {resolved}")
    return value


def load_project_config() -> dict[str, dict[str, Any]]:
    """Load the four canonical project configuration files."""
    return {
        name: load_yaml(CONFIG_DIR / f"{name}.yaml")
        for name in ("paths", "features", "ridge", "random_forest")
    }
