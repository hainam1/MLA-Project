"""Screen tail-bias improvements using only 3,050 model-train rows and frozen CV folds.

Validation and official test are not used for fitting, calibration, metrics, or selection. Linear
and isotonic calibration are nested: each outer-fit calibrator learns from inner out-of-fold
predictions created without the outer holdout.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import HuberRegressor, LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from mla_project.evaluation.improvement_study import (
    acceptance_table,
    band_metrics,
    fold_mae_interval,
    inverse_sqrt_band_weights,
    overall_metrics,
)
from mla_project.features.build_features import FEATURE_NAMES
from mla_project.models.train_ordinal import CumulativeLogitRegressor
from mla_project.models.train_random_forest import build_random_forest
from mla_project.models.train_ridge import build_ridge
from mla_project.pipelines.training_pipeline import prepare_training_data

ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PATH = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
SPLIT_PATH = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
PARAMETERS_PATH = ROOT / "outputs" / "phase6" / "selected_parameters.json"
CONFIG_PATH = ROOT / "configs" / "improvement_study.yaml"
OUTPUT_DIR = ROOT / "outputs" / "improvement_study"
TABLE_DIR = ROOT / "docs" / "data" / "improvement_tables"
REPORT_PATH = ROOT / "docs" / "train_only_improvement_results.md"

TARGETS = ("Vocabulary", "Grammar")
STANDARD_VARIANTS = (
    "ridge_baseline",
    "ridge_weighted",
    "rf_baseline",
    "rf_weighted",
    "rf_absolute_error",
    "rf_absolute_error_weighted",
    "huber",
    "ordinal_logistic",
)
CALIBRATED_VARIANTS = ("rf_linear_calibrated", "rf_isotonic_calibrated")
ALL_VARIANTS = (*STANDARD_VARIANTS, *CALIBRATED_VARIANTS)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def build_variant(
    variant: str,
    target: str,
    parameters: dict[str, dict[str, object]],
) -> tuple[object, bool]:
    ridge_parameters = parameters[f"ridge_{target.lower()}"]
    forest_parameters = parameters[f"random_forest_{target.lower()}"]
    weighted = variant.endswith("_weighted")
    if variant.startswith("ridge_"):
        return build_ridge(alpha=float(ridge_parameters["alpha"])), weighted
    if variant.startswith("rf_"):
        criterion = "absolute_error" if "absolute_error" in variant else "squared_error"
        return (
            build_random_forest(
                **forest_parameters,
                criterion=criterion,
                random_state=42,
                n_jobs=-1,
            ),
            weighted,
        )
    if variant == "huber":
        return (
            Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                    ("model", HuberRegressor(max_iter=2_000)),
                ]
            ),
            False,
        )
    if variant == "ordinal_logistic":
        return CumulativeLogitRegressor(), False
    raise ValueError(f"Unsupported improvement variant: {variant}")


def fit_estimator(estimator, x: pd.DataFrame, y: pd.Series, *, weighted: bool):
    if weighted:
        weights = inverse_sqrt_band_weights(y)
        if isinstance(estimator, Pipeline):
            estimator.fit(x, y, model__sample_weight=weights)
        else:
            estimator.fit(x, y, sample_weight=weights)
    else:
        estimator.fit(x, y)
    return estimator


def nested_calibrated_predictions(
    x: pd.DataFrame,
    y: pd.Series,
    folds: pd.Series,
    baseline_predictions: np.ndarray,
    baseline_estimator,
) -> tuple[np.ndarray, np.ndarray]:
    linear_predictions = np.full(len(y), np.nan)
    isotonic_predictions = np.full(len(y), np.nan)
    fold_values = folds.to_numpy(dtype=int)
    for outer_fold in sorted(np.unique(fold_values)):
        outer_train = fold_values != outer_fold
        outer_holdout = fold_values == outer_fold
        inner_predictions = np.full(int(outer_train.sum()), np.nan)
        outer_train_positions = np.flatnonzero(outer_train)
        outer_train_folds = fold_values[outer_train]
        for inner_fold in sorted(np.unique(outer_train_folds)):
            inner_fit_local = outer_train_folds != inner_fold
            inner_holdout_local = outer_train_folds == inner_fold
            inner_model = clone(baseline_estimator)
            inner_model.fit(
                x.iloc[outer_train_positions[inner_fit_local]],
                y.iloc[outer_train_positions[inner_fit_local]],
            )
            inner_predictions[inner_holdout_local] = inner_model.predict(
                x.iloc[outer_train_positions[inner_holdout_local]]
            )
        if not np.isfinite(inner_predictions).all():
            raise RuntimeError(
                "Nested calibration failed to create complete inner OOF predictions."
            )
        inner_y = y.iloc[outer_train_positions].to_numpy(dtype=float)
        linear = LinearRegression().fit(inner_predictions.reshape(-1, 1), inner_y)
        isotonic = IsotonicRegression(out_of_bounds="clip").fit(inner_predictions, inner_y)
        outer_base = baseline_predictions[outer_holdout]
        linear_predictions[outer_holdout] = linear.predict(outer_base.reshape(-1, 1))
        isotonic_predictions[outer_holdout] = isotonic.predict(outer_base)
    return linear_predictions, isotonic_predictions


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    def render(value: object) -> str:
        if pd.isna(value):
            return ""
        if isinstance(value, (float, np.floating)):
            return f"{float(value):.6f}"
        return str(value)

    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join("---" for _ in columns) + "|"]
    for _, row in frame.loc[:, columns].iterrows():
        lines.append("| " + " | ".join(render(row[column]) for column in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    parameters = json.loads(PARAMETERS_PATH.read_text(encoding="utf-8"))
    development = pd.read_csv(DEVELOPMENT_PATH, dtype={"essay_id": "string"})
    manifest = pd.read_csv(SPLIT_PATH, dtype={"essay_id": "string"})
    prepared = prepare_training_data(development, manifest)
    train = prepared.train.reset_index(drop=True)
    if len(train) != 3_050 or set(train["cv_fold"].astype(int)) != set(range(5)):
        raise ValueError("Improvement study requires the frozen 3,050-row, five-fold model train.")
    x = train.loc[:, list(FEATURE_NAMES)]
    folds = train["cv_fold"].astype(int)

    prediction_frame = train[["essay_id", "cv_fold", *TARGETS]].copy()
    overall_rows: list[dict[str, object]] = []
    band_rows: list[dict[str, object]] = []
    fold_rows: list[dict[str, object]] = []

    for target in TARGETS:
        y = train[target].astype(float)
        predictions: dict[str, np.ndarray] = {}
        for variant in STANDARD_VARIANTS:
            oof = np.full(len(train), np.nan)
            for fold in range(5):
                fit_mask = folds.ne(fold).to_numpy()
                holdout_mask = folds.eq(fold).to_numpy()
                estimator, weighted = build_variant(variant, target, parameters)
                fit_estimator(estimator, x.loc[fit_mask], y.loc[fit_mask], weighted=weighted)
                oof[holdout_mask] = estimator.predict(x.loc[holdout_mask])
            if not np.isfinite(oof).all():
                raise RuntimeError(f"Incomplete OOF predictions for {variant}/{target}.")
            predictions[variant] = oof

        baseline_estimator, _ = build_variant("rf_baseline", target, parameters)
        linear, isotonic = nested_calibrated_predictions(
            x,
            y,
            folds,
            predictions["rf_baseline"],
            baseline_estimator,
        )
        predictions["rf_linear_calibrated"] = linear
        predictions["rf_isotonic_calibrated"] = isotonic

        for variant in ALL_VARIANTS:
            prediction = predictions[variant]
            prediction_frame[f"{variant}_{target.lower()}"] = prediction
            summary = overall_metrics(y.to_numpy(dtype=float), prediction)
            variant_fold_maes = []
            for fold in range(5):
                mask = folds.eq(fold).to_numpy()
                fold_summary = overall_metrics(y.to_numpy(dtype=float)[mask], prediction[mask])
                variant_fold_maes.append(fold_summary["mae"])
                fold_rows.append(
                    {
                        "target": target,
                        "variant": variant,
                        "fold": fold,
                        "n_samples": int(mask.sum()),
                        **fold_summary,
                    }
                )
            fold_mean, fold_ci_lower, fold_ci_upper = fold_mae_interval(
                np.asarray(variant_fold_maes)
            )
            overall_rows.append(
                {
                    "target": target,
                    "variant": variant,
                    "n_samples": len(train),
                    **summary,
                    "fold_mean_mae": fold_mean,
                    "fold_mae_ci95_lower": fold_ci_lower,
                    "fold_mae_ci95_upper": fold_ci_upper,
                }
            )
            groups = band_metrics(y.to_numpy(dtype=float), prediction)
            groups.insert(0, "variant", variant)
            groups.insert(0, "target", target)
            band_rows.extend(groups.to_dict(orient="records"))

    overall = pd.DataFrame(overall_rows)
    bands = pd.DataFrame(band_rows)
    fold_metrics = pd.DataFrame(fold_rows)
    rules = config["acceptance"]
    acceptance = acceptance_table(
        overall,
        bands,
        fold_metrics,
        maximum_overall_mae_increase=float(rules["maximum_overall_mae_increase"]),
        minimum_macro_improvement=float(rules["minimum_macro_band_mae_improvement_fraction"]),
        minimum_tail_bias_reduction=float(rules["minimum_max_tail_bias_reduction_fraction"]),
        maximum_group_mae_increase=float(rules["maximum_group_mae_increase"]),
        minimum_improved_folds=int(rules["minimum_improved_folds"]),
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    prediction_frame.to_csv(
        OUTPUT_DIR / "train_oof_predictions.csv", index=False, float_format="%.12g"
    )
    overall.to_csv(TABLE_DIR / "train_oof_overall_metrics.csv", index=False, float_format="%.12g")
    bands.to_csv(TABLE_DIR / "train_oof_band_metrics.csv", index=False, float_format="%.12g")
    fold_metrics.to_csv(TABLE_DIR / "train_oof_fold_metrics.csv", index=False, float_format="%.12g")
    acceptance.to_csv(
        TABLE_DIR / "train_oof_acceptance_checks.csv", index=False, float_format="%.12g"
    )

    passed = acceptance.loc[acceptance["all_acceptance_rules_pass"]]
    summary = {
        "study_status": "train_only_screening_not_final_model_selection",
        "official_test_loaded": False,
        "validation_rows_used": 0,
        "model_train_rows": len(train),
        "feature_count": len(FEATURE_NAMES),
        "feature_schema_changed": False,
        "cv": {
            "outer_folds": 5,
            "splitter": "frozen_predefined_folds",
            "calibration": "inner OOF within each outer fit partition",
        },
        "variants": list(ALL_VARIANTS),
        "accepted_candidates": passed[["target", "variant"]].to_dict(orient="records"),
        "input_sha256": {
            "development": sha256(DEVELOPMENT_PATH),
            "split": sha256(SPLIT_PATH),
            "phase6_parameters": sha256(PARAMETERS_PATH),
            "config": sha256(CONFIG_PATH),
        },
        "output_sha256": {
            "oof_predictions": sha256(OUTPUT_DIR / "train_oof_predictions.csv"),
            "overall_metrics": sha256(TABLE_DIR / "train_oof_overall_metrics.csv"),
            "band_metrics": sha256(TABLE_DIR / "train_oof_band_metrics.csv"),
            "fold_metrics": sha256(TABLE_DIR / "train_oof_fold_metrics.csv"),
            "acceptance": sha256(TABLE_DIR / "train_oof_acceptance_checks.csv"),
        },
    }
    (TABLE_DIR / "train_only_improvement_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    ranked = overall.copy()
    ranked["macro_band_mae"] = ranked.apply(
        lambda row: bands.loc[
            bands["target"].eq(row["target"]) & bands["variant"].eq(row["variant"]), "mae"
        ].mean(),
        axis=1,
    )
    ranked = ranked.sort_values(["target", "macro_band_mae", "mae"], kind="stable")
    report = [
        "# Train-only Model Improvement Screening",
        "",
        "> Uses only 3,050 privacy-eligible model-train essays and frozen folds. Validation rows used: 0. Official-test rows used: 0.",
        "",
        "This is a predeclared challenger screening study, not a new independent performance estimate. "
        "Calibration is nested within each outer fold; all imputation, scaling, weighting, fitting, "
        "and calibration parameters are learned without the active holdout fold.",
        "",
        "## Overall OOF metrics",
        "",
        markdown_table(
            ranked,
            [
                "target",
                "variant",
                "mae",
                "macro_band_mae",
                "rmse",
                "r2",
                "within_0_5_points_rate",
                "within_1_0_point_rate",
                "calibration_slope",
                "fold_mae_ci95_lower",
                "fold_mae_ci95_upper",
            ],
        ),
        "",
        "## Predeclared acceptance checks",
        "",
        markdown_table(
            acceptance,
            [
                "target",
                "variant",
                "overall_mae_change",
                "macro_band_mae_improvement_fraction",
                "max_tail_bias_reduction_fraction",
                "maximum_band_mae_increase",
                "improved_folds",
                "all_acceptance_rules_pass",
            ],
        ),
        "",
        (
            f"Accepted candidates: {', '.join(f'{row.target}/{row.variant}' for row in passed.itertuples())}."
            if not passed.empty
            else "No challenger satisfies every predeclared acceptance rule; feature extractor v2 remains justified but is not started automatically."
        ),
        "",
        "No prediction was rounded or clipped.",
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
