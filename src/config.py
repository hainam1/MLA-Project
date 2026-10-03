"""Backward-compatible imports; use :mod:`mla_project.utils.config`."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mla_project.utils.config import load_project_config, load_yaml
from mla_project.utils.paths import PROJECT_ROOT, project_path

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "configs" / "experiment.yaml"


def load_config(path: str | Path = DEFAULT_CONFIG_PATH) -> dict[str, Any]:
    """Return a parsed experiment configuration with required sections checked."""
    config = load_yaml(path)

    if not isinstance(config, dict):
        raise ValueError("Experiment configuration must be a YAML mapping.")

    required_sections = {"project", "task", "data", "split", "config_files", "evaluation"}
    missing = required_sections.difference(config)
    if missing:
        raise ValueError(f"Configuration is missing sections: {sorted(missing)}")
    return config


def resolve_project_path(path: str | Path) -> Path:
    """Resolve a configured relative path from the repository root."""
    return project_path(path)


__all__ = ["load_config", "load_project_config", "resolve_project_path"]
