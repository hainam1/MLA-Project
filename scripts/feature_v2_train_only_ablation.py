"""Compare v2 feature groups for Ridge and RF using frozen train-only folds.

Only privacy-eligible model-train rows enter the comparisons. The source
development table also contains validation rows, which are filtered out before
fitting or metrics. Baseline OOF predictions were created by the prior frozen
train-only study with the same rows and folds.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from mla_project.evaluation.improvement_study import (
    acceptance_table,
    band_metrics,
    fold_mae_interval,
    inverse_sqrt_band_weights,
    overall_metrics,
)
from mla_project.features.build_features import FEATURE_NAMES
from mla_project.features.feature_v2 import V2_FEATURE_NAMES
from mla_project.models.train_random_forest import build_random_forest
from mla_project.models.train_ridge import build_ridge

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "data" / "05_model_features" / "development_features_with_targets.csv"
V2 = ROOT / "data" / "05_model_features" / "feature_v2_model_train_3050.csv"
MANIFEST = ROOT / "data" / "02_split_manifest" / "essay_split_manifest.csv"
PARAMETERS = ROOT / "outputs" / "phase6" / "selected_parameters.json"
BASELINE_OOF = ROOT / "outputs" / "improvement_study" / "train_oof_predictions.csv"
OUTPUT = ROOT / "outputs" / "improvement_study" / "feature_v2_oof_predictions.csv"
TABLE_DIR = ROOT / "docs" / "data" / "improvement_tables"
TARGETS = ("Vocabulary", "Grammar")
GROUPS = {
    "lexical": V2_FEATURE_NAMES[:3],
    "spelling": V2_FEATURE_NAMES[3:5],
    "grammar_rules": V2_FEATURE_NAMES[5:7],
    "syntax": V2_FEATURE_NAMES[7:],
    "all": V2_FEATURE_NAMES,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _load_train() -> pd.DataFrame:
    v1 = pd.read_csv(V1, dtype={"essay_id": "string"})
    v2 = pd.read_csv(V2, dtype={"essay_id": "string"})
    manifest = pd.read_csv(
        MANIFEST,
        usecols=["essay_id", "split", "privacy_review_status", "cv_fold"],
        dtype={"essay_id": "string"},
    )
    eligible = manifest.loc[
        manifest["split"].eq("model_train")
        & manifest["privacy_review_status"].eq("not_flagged"),
        ["essay_id", "cv_fold"],
    ]
    if len(eligible) != 3_050 or set(v2["essay_id"]) != set(eligible["essay_id"]):
        raise ValueError("V2 rows must equal the frozen eligible model-train IDs.")
    train = eligible.merge(v1.drop(columns=["cv_fold"]), on="essay_id", validate="one_to_one")
    train = train.merge(v2, on="essay_id", validate="one_to_one")
    if len(train) != 3_050 or set(train["split"]) != {"model_train"}:
        raise ValueError("The ablation must contain model-train rows only.")
    numeric = train[[*FEATURE_NAMES, *V2_FEATURE_NAMES, *TARGETS]].to_numpy(dtype=float)
    if not np.isfinite(numeric).all():
        raise ValueError("Ablation features and targets must be finite.")
    return train


def main() -> None:
    train = _load_train()
    parameters = json.loads(PARAMETERS.read_text(encoding="utf-8"))
    baseline = pd.read_csv(BASELINE_OOF, dtype={"essay_id": "string"})
    if len(baseline) != len(train) or set(baseline["essay_id"]) != set(train["essay_id"]):
        raise ValueError("Frozen baseline OOF IDs do not match model-train rows.")
    baseline = train[["essay_id", "cv_fold", *TARGETS]].merge(
        baseline, on="essay_id", validate="one_to_one", suffixes=("", "_baseline")
    )
    if not (baseline["cv_fold"].astype(int) == baseline["cv_fold_baseline"].astype(int)).all():
        raise ValueError("Frozen OOF folds changed.")
    for target in TARGETS:
        if not np.allclose(baseline[target], baseline[f"{target}_baseline"]):
            raise ValueError(f"Frozen OOF {target} labels changed.")

    folds = train["cv_fold"].astype(int).to_numpy()
    predictions = train[["essay_id", "cv_fold", *TARGETS]].copy()
    overall_rows: list[dict[str, object]] = []
    band_rows: list[dict[str, object]] = []
    fold_rows: list[dict[str, object]] = []
    variants = ["ridge_baseline", "rf_baseline"] + [
        f"{family}_v2_{group}" for family in ("ridge", "rf") for group in GROUPS
    ] + ["ridge_v2_all_weighted", "rf_v2_all_weighted"]

    for target in TARGETS:
        y = train[target].to_numpy(dtype=float)
        for variant in variants:
            if variant in {"ridge_baseline", "rf_baseline"}:
                output = baseline[f"{variant}_{target.lower()}"].to_numpy(dtype=float)
            else:
                family, group = variant.split("_v2_", maxsplit=1)
                weighted = group.endswith("_weighted")
                if weighted:
                    group = group.removesuffix("_weighted")
                columns = [*FEATURE_NAMES, *GROUPS[group]]
                x = train[columns]
                output = np.full(len(train), np.nan)
                for fold in range(5):
                    fit = folds != fold
                    holdout = folds == fold
                    selected = parameters[f"{'random_forest' if family == 'rf' else 'ridge'}_{target.lower()}"]
                    if family == "ridge":
                        model = build_ridge(alpha=float(selected["alpha"]))
                    else:
                        model = build_random_forest(**selected, random_state=42, n_jobs=-1)
                    if weighted:
                        model.fit(
                            x.loc[fit],
                            y[fit],
                            model__sample_weight=inverse_sqrt_band_weights(y[fit]),
                        )
                    else:
                        model.fit(x.loc[fit], y[fit])
                    output[holdout] = model.predict(x.loc[holdout])
                    print(f"{target} {variant}: fold {fold} complete", flush=True)
                if not np.isfinite(output).all():
                    raise ValueError(f"Incomplete OOF predictions: {target}/{variant}")
            predictions[f"{variant}_{target.lower()}"] = output
            metrics = overall_metrics(y, output)
            fold_maes = []
            for fold in range(5):
                mask = folds == fold
                fold_metrics = overall_metrics(y[mask], output[mask])
                fold_maes.append(fold_metrics["mae"])
                fold_rows.append(
                    {"target": target, "variant": variant, "fold": fold, "n_samples": int(mask.sum()), **fold_metrics}
                )
            _, ci_low, ci_high = fold_mae_interval(np.asarray(fold_maes))
            overall_rows.append(
                {"target": target, "variant": variant, "n_samples": len(train), **metrics,
                 "fold_mae_ci95_lower": ci_low, "fold_mae_ci95_upper": ci_high}
            )
            bands = band_metrics(y, output)
            bands.insert(0, "variant", variant)
            bands.insert(0, "target", target)
            band_rows.extend(bands.to_dict(orient="records"))

    overall = pd.DataFrame(overall_rows)
    bands = pd.DataFrame(band_rows)
    fold_results = pd.DataFrame(fold_rows)
    acceptance = acceptance_table(
        overall,
        bands,
        fold_results,
        baseline_variant="rf_baseline",
        maximum_overall_mae_increase=0.005,
        minimum_macro_improvement=0.10,
        minimum_tail_bias_reduction=0.20,
        maximum_group_mae_increase=0.05,
        minimum_improved_folds=4,
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(OUTPUT, index=False, float_format="%.12g")
    overall.to_csv(TABLE_DIR / "feature_v2_oof_overall.csv", index=False, float_format="%.12g")
    bands.to_csv(TABLE_DIR / "feature_v2_oof_bands.csv", index=False, float_format="%.12g")
    fold_results.to_csv(TABLE_DIR / "feature_v2_oof_folds.csv", index=False, float_format="%.12g")
    acceptance.to_csv(TABLE_DIR / "feature_v2_acceptance.csv", index=False, float_format="%.12g")
    summary = {
        "status": "experimental_train_only_ablation",
        "rows": len(train),
        "folds": 5,
        "feature_groups": {key: list(value) for key, value in GROUPS.items()},
        "validation_rows_present_in_source_csv_but_filtered_before_analysis": True,
        "validation_used_for_fit_metrics_or_selection": False,
        "official_test_loaded": False,
        "accepted": acceptance.loc[acceptance["all_acceptance_rules_pass"], ["target", "variant"]].to_dict("records"),
        "input_sha256": {"v1": sha256(V1), "v2": sha256(V2), "manifest": sha256(MANIFEST), "baseline_oof": sha256(BASELINE_OOF)},
        "output_sha256": sha256(OUTPUT),
    }
    (TABLE_DIR / "feature_v2_ablation_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
