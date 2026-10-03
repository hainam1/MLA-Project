"""Tune, fit, export validation predictions, and save the four approved models.

The script reads only the official-train development feature table and the frozen split manifest.
It never reads official-test features or score columns.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess

import pandas as pd

from mla_project.pipelines.training_pipeline import (
    prepare_training_data,
    save_training_result,
    train_models,
)
from mla_project.utils.config import load_yaml

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
MANIFEST_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
RIDGE_CONFIG_PATH = ROOT / "configs" / "ridge.yaml"
FOREST_CONFIG_PATH = ROOT / "configs" / "random_forest.yaml"
TRAINING_CONFIG_PATH = ROOT / "configs" / "phase6_training.yaml"
CODE_PATHS = {
    "training_script": ROOT / "scripts" / "phase6_train_models.py",
    "training_pipeline": ROOT / "src" / "mla_project" / "pipelines" / "training_pipeline.py",
    "ridge_builder": ROOT / "src" / "mla_project" / "models" / "train_ridge.py",
    "random_forest_builder": ROOT / "src" / "mla_project" / "models" / "train_random_forest.py",
    "feature_schema": ROOT / "src" / "mla_project" / "features" / "build_features.py",
}
CONFIG_PATHS = {
    "ridge": RIDGE_CONFIG_PATH,
    "random_forest": FOREST_CONFIG_PATH,
    "phase6": TRAINING_CONFIG_PATH,
}


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    manifest = pd.read_csv(MANIFEST_PATH, dtype={"essay_id": "string"})
    return development, manifest


def preflight_summary(development: pd.DataFrame, manifest: pd.DataFrame) -> dict[str, object]:
    training_config = load_yaml(TRAINING_CONFIG_PATH)
    prepared = prepare_training_data(
        development,
        manifest,
        eligible_status=str(training_config["privacy"]["eligible_status"]),
    )
    return {
        "ready": True,
        "official_test_loaded": False,
        "model_train_rows": len(prepared.train),
        "validation_rows": len(prepared.validation),
        "feature_count": len(prepared.feature_columns),
        "cv_fold_counts": {
            str(int(fold)): int(count)
            for fold, count in prepared.train["cv_fold"].value_counts().sort_index().items()
        },
        "privacy_status_counts": prepared.privacy_counts,
        "development_sha256": file_sha256(DEVELOPMENT_PATH),
        "split_sha256": file_sha256(MANIFEST_PATH),
    }


def package_versions() -> dict[str, str]:
    packages = ("joblib", "numpy", "pandas", "scikit-learn")
    return {package: importlib.metadata.version(package) for package in packages}


def mapping_sha256(values: dict[str, str]) -> str:
    payload = json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest().upper()


def code_version() -> dict[str, object]:
    source_hashes = {
        path.relative_to(ROOT).as_posix(): file_sha256(path) for path in CODE_PATHS.values()
    }
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status_lines = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        commit = None
        status_lines = []
    return {
        "git_commit": commit,
        "git_worktree_dirty": bool(status_lines),
        "git_status_entry_count": len(status_lines),
        "source_sha256": source_hashes,
        "source_tree_sha256": mapping_sha256(source_hashes),
    }


def config_version() -> dict[str, object]:
    config_hashes = {
        path.relative_to(ROOT).as_posix(): file_sha256(path) for path in CONFIG_PATHS.values()
    }
    return {
        "config_sha256": config_hashes,
        "config_set_sha256": mapping_sha256(config_hashes),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate inputs and print counts without fitting any model.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Override the configured Phase 6 artifact directory.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacement of an existing Phase 6 artifact set.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    development, manifest = load_inputs()
    preflight = preflight_summary(development, manifest)
    if args.preflight_only:
        print(json.dumps(preflight, indent=2, sort_keys=True))
        return

    training_config = load_yaml(TRAINING_CONFIG_PATH)
    configured_output = ROOT / str(training_config["artifacts"]["output_dir"])
    output_dir = args.output_dir.resolve() if args.output_dir else configured_output
    if (output_dir / "artifact_manifest.json").exists() and not args.overwrite:
        raise FileExistsError(
            f"Training artifacts already exist at {output_dir}. Use --overwrite explicitly."
        )

    result = train_models(
        development,
        manifest,
        ridge_config=load_yaml(RIDGE_CONFIG_PATH),
        random_forest_config=load_yaml(FOREST_CONFIG_PATH),
        training_config=training_config,
    )
    run_metadata = {
        **preflight,
        "python_version": platform.python_version(),
        "package_versions": package_versions(),
        "code_version": code_version(),
        "config_version": config_version(),
        "cv_protocol": {
            "splitter": "PredefinedSplit",
            "folds": int(training_config["cv"]["folds"]),
            "seed": None,
            "seed_policy": "not_applicable_fixed_folds",
            "scoring": str(training_config["cv"]["scoring"]),
            "n_jobs": int(training_config["cv"]["n_jobs"]),
        },
    }
    manifest_path = save_training_result(result, output_dir, run_metadata=run_metadata)
    print(
        json.dumps(
            {
                **result.summary,
                "artifact_manifest": str(manifest_path),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
