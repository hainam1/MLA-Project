"""Regenerate human-versus-machine validation figures from frozen text-free artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PREDICTIONS_PATH = ROOT / "outputs" / "predictions" / "phase7_validation_regression_predictions.csv"
BY_SCORE_PATH = ROOT / "docs" / "data" / "phase7_tables" / "machine_by_human_score.csv"
RELIABILITY_PATH = ROOT / "docs" / "data" / "improvement_tables" / "human_machine_reliability.csv"
FIGURE_DIR = ROOT / "outputs" / "figures" / "human_machine_comparison"
MANIFEST_PATH = ROOT / "docs" / "data" / "improvement_tables" / "human_machine_figure_manifest.json"

TARGETS = ("Vocabulary", "Grammar")
MODEL_COLUMNS = {
    "Vocabulary": {
        "Ridge": "ridge_vocabulary",
        "Random Forest": "random_forest_vocabulary",
    },
    "Grammar": {
        "Ridge": "ridge_grammar",
        "Random Forest": "random_forest_grammar",
    },
}
COLORS = {"Human": "#4D4D4D", "Ridge": "#2C7FB8", "Random Forest": "#D95F02"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    predictions = pd.read_csv(PREDICTIONS_PATH, dtype={"essay_id": "string"})
    by_score = pd.read_csv(BY_SCORE_PATH)
    reliability = pd.read_csv(RELIABILITY_PATH)
    if len(predictions) != 762 or predictions["essay_id"].duplicated().any():
        raise ValueError("Human-machine figures require 762 unique frozen validation predictions.")
    required_predictions = {
        "essay_id",
        *TARGETS,
        *(column for columns in MODEL_COLUMNS.values() for column in columns.values()),
    }
    if not required_predictions.issubset(predictions.columns):
        raise ValueError("Frozen validation predictions are missing required columns.")
    if set(by_score["target"]) != set(TARGETS) or set(reliability["trait"]) != set(TARGETS):
        raise ValueError("Human-machine summary tables do not contain both frozen targets.")
    return predictions, by_score, reliability


def style_axis(axis: plt.Axes) -> None:
    axis.grid(alpha=0.2, linewidth=0.8)
    axis.spines[["top", "right"]].set_visible(False)


def plot_score_distributions(predictions: pd.DataFrame) -> Path:
    figure, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True, constrained_layout=True)
    bins = np.arange(0.875, 5.126, 0.25)
    for axis, target in zip(axes, TARGETS, strict=True):
        axis.hist(
            predictions[target],
            bins=bins,
            density=True,
            color=COLORS["Human"],
            alpha=0.28,
            label="Human aggregate",
        )
        for model, column in MODEL_COLUMNS[target].items():
            axis.hist(
                predictions[column],
                bins=bins,
                density=True,
                histtype="step",
                linewidth=2.0,
                color=COLORS[model],
                label=model,
            )
        axis.set_title(f"{target}: score distribution")
        axis.set_xlabel("Score")
        axis.set_xlim(0.75, 5.25)
        axis.set_xticks(np.arange(1, 5.1, 0.5))
        axis.legend(frameon=False)
        style_axis(axis)
    axes[0].set_ylabel("Density")
    path = FIGURE_DIR / "human_machine_score_distributions.png"
    figure.savefig(path, dpi=200, metadata={"Software": "matplotlib"})
    plt.close(figure)
    return path


def plot_calibration(by_score: pd.DataFrame) -> Path:
    figure, axes = plt.subplots(
        1, 2, figsize=(13, 5), sharex=True, sharey=True, constrained_layout=True
    )
    for axis, target in zip(axes, TARGETS, strict=True):
        target_rows = by_score.loc[by_score["target"].eq(target)]
        for model in ("Ridge", "Random Forest"):
            rows = target_rows.loc[target_rows["model"].eq(model)].sort_values("human_score")
            standard_error = rows["standard_deviation_machine_score"].fillna(0.0) / np.sqrt(
                rows["n_samples"]
            )
            marker_sizes = 28 + 92 * np.sqrt(rows["n_samples"] / target_rows["n_samples"].max())
            axis.errorbar(
                rows["human_score"],
                rows["mean_machine_score"],
                yerr=1.96 * standard_error,
                color=COLORS[model],
                linewidth=1.8,
                capsize=3,
                alpha=0.9,
            )
            axis.scatter(
                rows["human_score"],
                rows["mean_machine_score"],
                s=marker_sizes,
                color=COLORS[model],
                edgecolor="white",
                linewidth=0.7,
                label=model,
                zorder=3,
            )
        axis.plot([1, 5], [1, 5], "--", color="black", linewidth=1.2, label="Perfect agreement")
        axis.set_title(f"{target}: calibration")
        axis.set_xlabel("Human aggregate score")
        axis.set_xlim(0.8, 5.2)
        axis.set_ylim(0.8, 5.2)
        axis.set_xticks(np.arange(1, 5.1, 0.5))
        axis.set_yticks(np.arange(1, 5.1, 0.5))
        axis.legend(frameon=False)
        style_axis(axis)
    axes[0].set_ylabel("Mean machine score (95% CI)")
    path = FIGURE_DIR / "human_machine_calibration_by_score.png"
    figure.savefig(path, dpi=200, metadata={"Software": "matplotlib"})
    plt.close(figure)
    return path


def plot_bias_by_score(by_score: pd.DataFrame) -> Path:
    figure, axes = plt.subplots(
        1, 2, figsize=(13, 5), sharex=True, sharey=True, constrained_layout=True
    )
    for axis, target in zip(axes, TARGETS, strict=True):
        target_rows = by_score.loc[by_score["target"].eq(target)]
        for model in ("Ridge", "Random Forest"):
            rows = target_rows.loc[target_rows["model"].eq(model)].sort_values("human_score")
            axis.plot(
                rows["human_score"],
                rows["mean_difference_machine_minus_human"],
                marker="o",
                markersize=6,
                linewidth=2,
                color=COLORS[model],
                label=model,
            )
        axis.axhline(0.0, color="black", linestyle="--", linewidth=1.2)
        axis.fill_between([0.8, 5.2], -0.5, 0.5, color="#BBBBBB", alpha=0.12)
        axis.set_title(f"{target}: signed bias by human score")
        axis.set_xlabel("Human aggregate score")
        axis.set_xlim(0.8, 5.2)
        axis.set_ylim(-1.6, 2.2)
        axis.set_xticks(np.arange(1, 5.1, 0.5))
        axis.legend(frameon=False)
        style_axis(axis)
    axes[0].set_ylabel("Machine minus human score")
    path = FIGURE_DIR / "human_machine_bias_by_score.png"
    figure.savefig(path, dpi=200, metadata={"Software": "matplotlib"})
    plt.close(figure)
    return path


def plot_reliability_mae(reliability: pd.DataFrame) -> Path:
    figure, axis = plt.subplots(figsize=(9, 5.5), constrained_layout=True)
    labels = ["Human–human", "RF–aggregate human", "RF–individual human"]
    columns = [
        "human_human_mae",
        "model_aggregate_human_mae",
        "model_individual_human_mae",
    ]
    colors = ["#7F7F7F", "#D95F02", "#E6AB02"]
    x = np.arange(len(TARGETS), dtype=float)
    width = 0.23
    for index, (label, column, color) in enumerate(zip(labels, columns, colors, strict=True)):
        values = [
            float(reliability.loc[reliability["trait"].eq(target), column].iloc[0])
            for target in TARGETS
        ]
        bars = axis.bar(x + (index - 1) * width, values, width, label=label, color=color)
        axis.bar_label(bars, labels=[f"{value:.3f}" for value in values], padding=3, fontsize=9)
    axis.set_xticks(x, TARGETS)
    axis.set_ylabel("Mean absolute error (score points)")
    axis.set_title("Human–human and machine–human disagreement")
    axis.set_ylim(0, 0.65)
    axis.legend(frameon=False, ncols=3, loc="upper center")
    axis.text(
        0.5,
        -0.13,
        "RF–aggregate uses the released consensus target; RF–individual averages error against each raw rater.",
        ha="center",
        va="top",
        transform=axis.transAxes,
        fontsize=9,
        color="#444444",
    )
    style_axis(axis)
    path = FIGURE_DIR / "human_machine_reliability_mae.png"
    figure.savefig(path, dpi=200, metadata={"Software": "matplotlib"})
    plt.close(figure)
    return path


def main() -> None:
    predictions, by_score, reliability = load_inputs()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    figure_paths = [
        plot_score_distributions(predictions),
        plot_calibration(by_score),
        plot_bias_by_score(by_score),
        plot_reliability_mae(reliability),
    ]
    manifest = {
        "official_test_loaded": False,
        "population": "762 privacy-eligible validation essays",
        "predictions_are_continuous_unrounded": True,
        "input_sha256": {
            "phase7_predictions": sha256(PREDICTIONS_PATH),
            "machine_by_human_score": sha256(BY_SCORE_PATH),
            "human_machine_reliability": sha256(RELIABILITY_PATH),
        },
        "figures": {
            path.name: {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
            for path in figure_paths
        },
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
