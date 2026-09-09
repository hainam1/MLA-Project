"""Generate exploratory data analysis (EDA) figures and quantitative tables."""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import wordfreq

VALID_LEVELS = ("A1", "A2", "B1", "B2", "C1")
LEVEL_PALETTE = {
    "A1": "#4E79A7",
    "A2": "#59A14F",
    "B1": "#EDC948",
    "B2": "#F28E2B",
    "C1": "#E15759",
}


def compute_basic_properties(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    word_pattern = re.compile(r"\b[a-zA-Z]+\b")

    def analyze_row(text: str) -> dict:
        words = word_pattern.findall(text.lower())
        n_words = max(1, len(words))
        n_chars = len(text)
        zipfs = [wordfreq.zipf_frequency(w, "en") for w in words] or [4.0]
        mean_zipf = float(np.mean(zipfs))
        min_zipf = float(np.min(zipfs))
        rare_ratio = float(sum(1 for z in zipfs if z < 4.0) / n_words)
        return {
            "num_words": n_words,
            "num_chars": n_chars,
            "avg_word_zipf": round(mean_zipf, 3),
            "min_word_zipf": round(min_zipf, 3),
            "rare_word_ratio": round(rare_ratio, 3),
        }

    props = [analyze_row(t) for t in df["text"]]
    props_df = pd.DataFrame(props)
    return pd.concat([df.reset_index(drop=True), props_df], axis=1)


def generate_eda_figures(df: pd.DataFrame, figures_dir: Path) -> None:
    figures_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font="sans-serif")

    # 1. Overall CEFR Distribution
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    counts = df["cefr_level"].value_counts().reindex(VALID_LEVELS, fill_value=0)
    total = len(df)
    counts_df = pd.DataFrame({"level": list(counts.index), "count": list(counts.values)})
    sns.barplot(
        data=counts_df,
        x="level",
        y="count",
        hue="level",
        palette=LEVEL_PALETTE,
        legend=False,
        ax=ax,
    )
    ax.set_title(
        "English Sentence CEFR Level Distribution (N = 12,521)",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.set_xlabel("CEFR Level", fontsize=11, labelpad=8)
    ax.set_ylabel("Number of Sentences", fontsize=11, labelpad=8)
    for i, count in enumerate(counts.values):
        pct = count / total * 100
        ax.text(i, count + 60, f"{count:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=10)
    ax.set_ylim(0, max(counts.values) * 1.18)
    fig.tight_layout()
    fig.savefig(figures_dir / "cefr_sentence_distribution.png")
    plt.close(fig)

    # 2. CEFR Distribution by Source (cefr_sp_en vs readme_en)
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=200)
    source_pct = pd.crosstab(df["cefr_level"], df["source"], normalize="columns") * 100
    source_pct = source_pct.reindex(VALID_LEVELS, fill_value=0)

    plot_data = source_pct.reset_index().melt(
        id_vars="cefr_level",
        value_vars=["cefr_sp_en", "readme_en"],
        var_name="Source Dataset",
        value_name="Percentage (%)",
    )
    sns.barplot(
        data=plot_data,
        x="cefr_level",
        y="Percentage (%)",
        hue="Source Dataset",
        palette={"cefr_sp_en": "#4E79A7", "readme_en": "#F28E2B"},
        ax=ax,
    )
    ax.set_title("Label Distribution by Source Dataset", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("CEFR Level", fontsize=11, labelpad=8)
    ax.set_ylabel("Proportion within Source (%)", fontsize=11, labelpad=8)
    ax.set_ylim(0, 45)
    fig.tight_layout()
    fig.savefig(figures_dir / "cefr_distribution_by_source.png")
    plt.close(fig)

    # 3. Sentence Length Distribution (Word Count & Char Count)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)
    sns.boxplot(
        data=df,
        x="cefr_level",
        y="num_words",
        hue="cefr_level",
        order=VALID_LEVELS,
        palette=LEVEL_PALETTE,
        legend=False,
        showfliers=False,
        ax=ax1,
    )
    ax1.set_title("Sentence Length (Words) by CEFR Level", fontsize=12, fontweight="bold", pad=10)
    ax1.set_xlabel("CEFR Level", fontsize=11)
    ax1.set_ylabel("Word Count (excluding outliers)", fontsize=11)

    sns.boxplot(
        data=df,
        x="cefr_level",
        y="num_chars",
        hue="cefr_level",
        order=VALID_LEVELS,
        palette=LEVEL_PALETTE,
        legend=False,
        showfliers=False,
        ax=ax2,
    )
    ax2.set_title(
        "Sentence Length (Characters) by CEFR Level", fontsize=12, fontweight="bold", pad=10
    )
    ax2.set_xlabel("CEFR Level", fontsize=11)
    ax2.set_ylabel("Character Count (excluding outliers)", fontsize=11)
    fig.tight_layout()
    fig.savefig(figures_dir / "sentence_length_distribution.png")
    plt.close(fig)

    # 4. Lexical Rarity Distribution (Avg Zipf Frequency & Rare Word Ratio)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=200)
    sns.boxplot(
        data=df,
        x="cefr_level",
        y="avg_word_zipf",
        hue="cefr_level",
        order=VALID_LEVELS,
        palette=LEVEL_PALETTE,
        legend=False,
        showfliers=False,
        ax=ax1,
    )
    ax1.set_title(
        "Average Word Zipf Frequency by CEFR Level\n(Higher = More Common Words)",
        fontsize=11,
        fontweight="bold",
        pad=10,
    )
    ax1.set_xlabel("CEFR Level", fontsize=11)
    ax1.set_ylabel("Mean Zipf Frequency", fontsize=11)

    sns.boxplot(
        data=df,
        x="cefr_level",
        y="rare_word_ratio",
        hue="cefr_level",
        order=VALID_LEVELS,
        palette=LEVEL_PALETTE,
        legend=False,
        showfliers=False,
        ax=ax2,
    )
    ax2.set_title(
        "Proportion of Rare Words (Zipf < 4.0) by CEFR Level\n(Higher = More Advanced Vocabulary)",
        fontsize=11,
        fontweight="bold",
        pad=10,
    )
    ax2.set_xlabel("CEFR Level", fontsize=11)
    ax2.set_ylabel("Rare Word Ratio", fontsize=11)
    fig.tight_layout()
    fig.savefig(figures_dir / "lexical_rarity_distribution.png")
    plt.close(fig)


def summarize_eda(df: pd.DataFrame) -> dict:
    summary: dict = {
        "total_sentences": int(len(df)),
        "distribution_overall": {},
        "distribution_by_source": {},
        "sentence_length": {},
        "lexical_rarity": {},
    }

    # Overall label counts & percentages
    for level in VALID_LEVELS:
        cnt = int((df["cefr_level"] == level).sum())
        summary["distribution_overall"][level] = {
            "count": cnt,
            "percentage": round(cnt / len(df) * 100, 2),
        }

    # Cross-tab counts & source percentages
    for src in sorted(df["source"].unique()):
        src_df = df[df["source"] == src]
        summary["distribution_by_source"][src] = {
            "total": int(len(src_df)),
            "levels": {
                level: {
                    "count": int((src_df["cefr_level"] == level).sum()),
                    "percentage": round(
                        (src_df["cefr_level"] == level).sum() / len(src_df) * 100, 2
                    ),
                }
                for level in VALID_LEVELS
            },
        }

    # Length and rarity stats per level
    for level in VALID_LEVELS:
        sub = df[df["cefr_level"] == level]
        summary["sentence_length"][level] = {
            "words_mean": round(float(sub["num_words"].mean()), 2),
            "words_median": round(float(sub["num_words"].median()), 1),
            "words_std": round(float(sub["num_words"].std()), 2),
            "chars_mean": round(float(sub["num_chars"].mean()), 2),
            "chars_median": round(float(sub["num_chars"].median()), 1),
        }
        summary["lexical_rarity"][level] = {
            "avg_zipf_mean": round(float(sub["avg_word_zipf"].mean()), 3),
            "min_zipf_mean": round(float(sub["min_word_zipf"].mean()), 3),
            "rare_word_ratio_mean": round(float(sub["rare_word_ratio"].mean()), 3),
            "rare_word_ratio_median": round(float(sub["rare_word_ratio"].median()), 3),
        }

    return summary


def main() -> None:
    cleaned_path = Path("data/processed/cefr_sentences_clean.csv")
    if not cleaned_path.exists():
        raise FileNotFoundError(f"Missing {cleaned_path}; run clean_cefr_sentences first")

    df = pd.read_csv(cleaned_path)
    df_props = compute_basic_properties(df)

    figures_dir = Path("reports/figures")
    generate_eda_figures(df_props, figures_dir)
    print(f"Generated EDA figures in {figures_dir}")

    summary = summarize_eda(df_props)
    summary_path = Path("reports/eda_summary.json")
    summary_path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"Saved quantitative EDA summary to {summary_path}")


if __name__ == "__main__":
    main()
