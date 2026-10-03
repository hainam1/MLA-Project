"""Render presentation-ready, train-only feature-v2 comparison figures.

Inputs are the public, text-free 5-fold OOF summary tables. No essay text,
individual predictions, validation labels, or official test data are read.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TABLE_DIR = ROOT / "docs" / "data" / "improvement_tables"
FIGURE_DIR = ROOT / "docs" / "assets" / "feature_v2_comparison"

BLUE = "#2563A6"
ORANGE = "#D97732"
TEAL = "#168C86"
INK = "#172334"
MUTED = "#526275"
GRID = "#DDE4EC"
BACKGROUND = "#FFFFFF"

VARIANT_LABELS = {
    "ridge_baseline": "Ridge v1",
    "ridge_v2_all": "Ridge v1 + v2",
    "rf_baseline": "RF v1",
    "rf_v2_all": "RF v1 + v2",
    "rf_v2_all_weighted": "RF v1 + v2, có trọng số",
}


def read_indexed_csv(name: str, key_fields: tuple[str, ...]) -> dict[tuple[str, ...], dict]:
    with (TABLE_DIR / name).open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    index = {tuple(row[field] for field in key_fields): row for row in rows}
    if len(index) != len(rows):
        raise ValueError(f"Duplicate keys in {name}")
    return index


def value(rows: dict, *key: str, field: str) -> float:
    return float(rows[key][field])


def setup_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
            "font.size": 11,
            "axes.labelcolor": INK,
            "axes.edgecolor": GRID,
            "text.color": INK,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": BACKGROUND,
            "axes.facecolor": BACKGROUND,
            "savefig.facecolor": BACKGROUND,
            "svg.fonttype": "none",
        }
    )


def save(fig: plt.Figure, stem: str) -> None:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURE_DIR / f"{stem}.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIGURE_DIR / f"{stem}.svg", bbox_inches="tight")
    plt.close(fig)


def add_note(fig: plt.Figure, note: str) -> None:
    fig.text(0.04, 0.015, note, fontsize=9.5, color=MUTED, va="bottom")


def plot_overall_mae(overall: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.1), sharey=True)
    fig.suptitle("Sai số trung bình giảm khi thêm 9 đặc trưng v2", x=0.04, ha="left", fontsize=17, weight="bold")
    fig.text(0.04, 0.895, "MAE trên 3.050 bài model-train · 5-fold OOF · thấp hơn là tốt hơn", fontsize=10.5, color=MUTED)

    for ax, target in zip(axes, ("Vocabulary", "Grammar")):
        for y, model in ((1, "ridge"), (0, "rf")):
            baseline = value(overall, target, f"{model}_baseline", field="mae")
            improved = value(overall, target, f"{model}_v2_all", field="mae")
            ax.barh(y + 0.16, baseline, height=0.26, color=BLUE, label="v1" if y == 1 else None)
            ax.barh(y - 0.16, improved, height=0.26, color=ORANGE, label="v1 + v2" if y == 1 else None)
            ax.text(baseline + 0.004, y + 0.16, f"{baseline:.4f}", va="center", fontsize=10, color=INK)
            ax.text(improved + 0.004, y - 0.16, f"{improved:.4f}", va="center", fontsize=10, color=INK)
            relative_gain = (baseline - improved) / baseline * 100
            ax.text(0.027, y - 0.48, f"Giảm {relative_gain:.1f}%", color=TEAL, fontsize=10, weight="bold")
        ax.set_title(target, loc="left", fontsize=13, weight="bold", pad=12)
        ax.set_xlim(0, 0.54)
        ax.set_ylim(-0.8, 1.65)
        ax.set_yticks([0, 1], ["Random Forest", "Ridge"])
        ax.set_xticks(np.arange(0, 0.56, 0.1))
        ax.xaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", length=0)
        ax.spines["left"].set_visible(False)
    axes[0].legend(loc="upper right", frameon=False, ncol=2, bbox_to_anchor=(1, 1.17))
    add_note(fig, "Nguồn: feature_v2_oof_overall.csv · Thử nghiệm trên train, chưa kiểm định độc lập trên validation/test.")
    fig.subplots_adjust(left=0.16, right=0.98, top=0.79, bottom=0.16, wspace=0.15)
    save(fig, "01_mae_truoc_sau")


def plot_tail_bias(bands: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.45), sharey=True)
    fig.suptitle("Độ lệch có hướng ở hai đầu thang điểm vẫn còn lớn", x=0.04, ha="left", fontsize=17, weight="bold")
    fig.text(0.04, 0.905, "Bias = điểm máy − điểm người · dương: chấm dư · âm: chấm thiếu", fontsize=10.5, color=MUTED)
    variants = ["ridge_baseline", "ridge_v2_all", "rf_baseline", "rf_v2_all"]
    colors = [BLUE, ORANGE, BLUE, ORANGE]
    hatches = ["", "", "//", "//"]

    for ax, target in zip(axes, ("Vocabulary", "Grammar")):
        positions = np.array([0, 1.05, 2.55, 3.6])
        for score_band, shift in (("low", -0.22), ("high", 0.22)):
            vals = [value(bands, target, variant, score_band, field="signed_bias") for variant in variants]
            for i, (pos, val) in enumerate(zip(positions, vals)):
                ax.bar(pos + shift, val, width=0.37, color=colors[i], hatch=hatches[i], edgecolor=INK if i >= 2 else "none", linewidth=0.5)
                ax.text(pos + shift, val + (0.035 if val >= 0 else -0.035), f"{val:+.2f}",
                        ha="center", va="bottom" if val >= 0 else "top", fontsize=9.2)
        ax.axhline(0, color=INK, linewidth=1)
        ax.set_title(target, loc="left", fontsize=13, weight="bold", pad=12)
        ax.set_xticks(positions, ["Ridge v1", "Ridge\nv1 + v2", "RF v1", "RF\nv1 + v2"])
        ax.set_xlim(-0.65, 4.25)
        ax.set_ylim(-1.02, 0.83)
        ax.set_yticks(np.arange(-1.0, 0.81, 0.2))
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("Sai lệch trung bình (điểm)")
    add_note(fig, "Nguồn: feature_v2_oof_bands.csv · Mỗi cặp cột là điểm thấp (dương) và điểm cao (âm); chưa kiểm định độc lập.")
    fig.subplots_adjust(left=0.09, right=0.985, top=0.79, bottom=0.19, wspace=0.13)
    save(fig, "02_lech_diem_thap_cao")


def plot_weighting_tradeoff(bands: dict) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.3), sharey=True)
    fig.suptitle("Tăng trọng số hai đầu: tốt hơn ở điểm cao, kém hơn ở giữa", x=0.04, ha="left", fontsize=17, weight="bold")
    fig.text(0.04, 0.9, "Random Forest · MAE theo nhóm điểm người chấm · thấp hơn là tốt hơn", fontsize=10.5, color=MUTED)
    variants = ["rf_baseline", "rf_v2_all", "rf_v2_all_weighted"]
    labels = ["v1", "v1 + v2", "v1 + v2 có trọng số"]
    colors = [BLUE, ORANGE, TEAL]
    band_names = [("low", "Điểm thấp"), ("middle", "Điểm giữa"), ("high", "Điểm cao")]
    x = np.arange(3)
    width = 0.24

    for ax, target in zip(axes, ("Vocabulary", "Grammar")):
        for i, (variant, label, color) in enumerate(zip(variants, labels, colors)):
            vals = [value(bands, target, variant, band, field="mae") for band, _ in band_names]
            ax.bar(x + (i - 1) * width, vals, width, color=color, label=label)
            for xpos, val in zip(x + (i - 1) * width, vals):
                ax.text(xpos, val + 0.018, f"{val:.3f}", ha="center", va="bottom", rotation=90, fontsize=8.7)
        counts = [int(bands[(target, "rf_baseline", band)]["n_samples"]) for band, _ in band_names]
        ax.set_xticks(x, [f"{name}\n(n={count:,})" for (_, name), count in zip(band_names, counts)])
        ax.set_title(target, loc="left", fontsize=13, weight="bold", pad=12)
        ax.set_ylim(0, 0.94)
        ax.set_yticks(np.arange(0, 1.0, 0.2))
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("MAE (điểm)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", bbox_to_anchor=(0.98, 0.88), ncol=3, frameon=False)
    add_note(fig, "Nguồn: feature_v2_oof_bands.csv · Không phương án nào đạt đủ tiêu chí chấp nhận đã định trước.")
    fig.subplots_adjust(left=0.075, right=0.985, top=0.74, bottom=0.2, wspace=0.13)
    save(fig, "03_danh_doi_trong_so_rf")


def main() -> None:
    setup_style()
    overall = read_indexed_csv("feature_v2_oof_overall.csv", ("target", "variant"))
    bands = read_indexed_csv("feature_v2_oof_bands.csv", ("target", "variant", "score_band"))
    plot_overall_mae(overall)
    plot_tail_bias(bands)
    plot_weighting_tradeoff(bands)
    for path in sorted(FIGURE_DIR.glob("*.png")):
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
