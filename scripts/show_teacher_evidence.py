"""Read-only teacher demo: verify saved evidence without fitting or predicting.

Official Test is inspected only through its existing label/comparison tables.
Pipeline source is parsed as text, never imported or executed.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pandas as pd
import yaml
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from mla_project.evaluation.rater_reliability import (
    load_allowlisted_rater_scores,
    rater_reliability_metrics,
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def csv(path):
    frame = pd.read_csv(ROOT / path, dtype={"essay_id": "string"})
    if "essay_id" in frame:
        require(
            frame.essay_id.notna().all() and frame.essay_id.is_unique,
            f"Missing/duplicate IDs: {path}",
        )
    return frame


def tree(path):
    return ast.parse((ROOT / path).read_text(encoding="utf-8-sig"))


def function(module, name):
    return next(
        node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == name
    )


def contains(node, expression):
    """Check an exact AST subtree, ignoring formatting and source line numbers."""
    expected = ast.dump(ast.parse(expression).body[0])
    require(
        any(ast.dump(child) == expected for child in ast.walk(node)),
        f"Implementation evidence changed: {expression}",
    )


def constant(module, name):
    for node in module.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise ValueError(f"Missing source constant: {name}")


def sources(items):
    print("\nEvidence sources:")
    for path, purpose in items:
        print(f"- {path} ({purpose})")


def main():
    config_path = "configs/experiment.yaml"
    config = yaml.safe_load((ROOT / config_path).read_text(encoding="utf-8"))["evaluation"]
    threshold = float(config["large_error_threshold"])
    references = config["selected_reference_predictors"]
    helper8_path = "src/mla_project/evaluation/phase8.py"
    helper9_path = "src/mla_project/evaluation/phase9.py"
    pipeline8_path = "scripts/phase8_evaluate_review_prioritization.py"
    pipeline9_path = "scripts/phase9_official_test_evaluation.py"
    helper8, helper9 = tree(helper8_path), tree(helper9_path)
    require(threshold == constant(helper9, "PRIMARY_ERROR_THRESHOLD"), "Threshold mismatch")
    require(references == constant(helper9, "REFERENCE_PREDICTORS"), "Reference mismatch")
    require(
        set(references.values()) == {"random_forest_vocabulary", "random_forest_grammar"},
        "Reference is no longer Random Forest",
    )
    for module, name in ((helper8, "add_review_signals"), (helper9, "add_frozen_test_signals")):
        signal = function(module, name)
        for target in ("Vocabulary", "Grammar"):
            lower = target.lower()
            contains(
                signal,
                f"result['error_{lower}'] = "
                f"(result['{references[target]}'] - result['{target}']).abs()",
            )
        contains(
            signal,
            "result['max_rf_absolute_error'] = "
            "result[['error_vocabulary', 'error_grammar']].max(axis=1)",
        )
        arg = "float(error_threshold)" if name == "add_review_signals" else "error_threshold"
        contains(signal, f"result['large_error'] = result['max_rf_absolute_error'].ge({arg})")

    # Verify the same mask flows to Random and the loop over all fixed rankings.
    contains(
        function(helper8, "metrics_for_selected_ids"),
        "metrics = review_queue_metrics(frame['large_error'].to_numpy(dtype=bool), selected)",
    )
    contains(
        function(helper8, "random_reference_draws"),
        "error_mask = np.asarray(large_errors, dtype=bool)",
    )
    contains(
        function(helper8, "random_reference_draws"),
        "rows.append({'repetition': repetition, **review_queue_metrics(error_mask, selected)})",
    )
    strategies = ("Random", "Shortest-first", "Ridge extremity", "Ridge-RF disagreement")
    for path, mask_name, ranking_name in (
        (pipeline8_path, "signals", "_rankings"),
        (pipeline9_path, "threshold_signals", "rankings"),
    ):
        module = tree(path)
        require(
            threshold
            == constant(module if path == pipeline8_path else helper9, "PRIMARY_ERROR_THRESHOLD"),
            "Pipeline threshold mismatch",
        )
        ranking = function(module, ranking_name)
        names = {node.value for node in ast.walk(ranking) if isinstance(node, ast.Constant)}
        require(set(strategies[1:]).issubset(names), "Fixed ranking strategies changed")
        calls = [
            node
            for node in ast.walk(function(module, "main"))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        ]
        require(
            any(
                call.func.id == "random_reference_draws"
                and ast.unparse(call.args[0]) == f"{mask_name}['large_error'].to_numpy(dtype=bool)"
                for call in calls
            ),
            "Random does not receive the common mask",
        )
        require(
            any(
                call.func.id == "metrics_for_selected_ids"
                and ast.unparse(call.args[0]) == mask_name
                and any(
                    k.arg == "strategy" and ast.unparse(k.value) == "strategy"
                    for k in call.keywords
                )
                for call in calls
            ),
            "Fixed rankings do not receive the common frame",
        )

    prediction_path = "outputs/predictions/phase7_validation_regression_predictions.csv"
    phase6_path = "outputs/phase6/validation_predictions.csv"
    manifest_path = "data/02_split_manifest/essay_split_manifest.csv"
    validation = csv(prediction_path).set_index("essay_id").sort_index()
    phase6 = csv(phase6_path).set_index("essay_id").sort_index()
    pd.testing.assert_frame_equal(validation[phase6.columns], phase6)
    manifest = csv(manifest_path)
    eligible = manifest.split.eq("validation") & manifest.privacy_review_status.eq("not_flagged")
    require(
        set(validation.index) == set(manifest.loc[eligible, "essay_id"]),
        "Predictions do not match eligible Validation IDs",
    )
    label_paths = []
    populations = []
    for phase, population in ((8, "Validation"), (9, "Official Test (saved artifacts only)")):
        path = f"docs/data/phase{phase}_tables/large_error_labels.csv"
        labels = csv(path).set_index("essay_id").sort_index()
        errors = np.column_stack(
            [abs(labels[target] - labels[references[target]]) for target in references]
        )
        require(np.isfinite(errors).all(), "Nonfinite saved errors")
        mask = errors.max(axis=1) >= threshold
        require(labels.large_error.dtype == bool, "Saved mask must be boolean")
        require(np.array_equal(mask, labels.large_error), f"Saved mask mismatch: {path}")
        if phase == 8:
            pd.testing.assert_frame_equal(
                labels[validation.columns.intersection(labels.columns)],
                validation[validation.columns.intersection(labels.columns)],
            )
        else:
            official = manifest.split.eq("official_test") & manifest.privacy_review_status.eq(
                "not_flagged"
            )
            require(
                set(labels.index) == set(manifest.loc[official, "essay_id"]),
                "Saved Official Test population mismatch",
            )
        comparison_path = f"docs/data/phase{phase}_tables/review_strategy_comparison.csv"
        comparison = csv(comparison_path)
        primary = comparison[
            comparison.error_threshold.eq(threshold)
            & comparison.review_budget.eq(config["primary_review_budget"])
        ]
        require(
            len(primary) == len(strategies) and set(primary.strategy) == set(strategies),
            "Saved primary strategies mismatch",
        )
        n_column = "validation_rows" if phase == 8 else "test_rows"
        require(
            primary.large_error_count.eq(int(mask.sum())).all()
            and primary[n_column].eq(len(labels)).all(),
            "Saved shared population mismatch",
        )
        label_paths.extend(
            [
                (path, f"{population}: formula, N, count"),
                (comparison_path, "all four strategies: shared count"),
            ]
        )
        populations.append((population, len(labels), int(mask.sum())))

    print("=== 1. LARGE ERROR DEFINITION ===\n")
    print("Reference predictor: Random Forest")
    print(f"Threshold: {threshold:.1f} point")
    print(f"Formula: max(abs(y_vocab - rf_vocab), abs(y_grammar - rf_grammar)) >= {threshold:.1f}")
    print("Meaning: Vocabulary error >= threshold OR Grammar error >= threshold\n")
    for name, n, count in populations:
        print(f"{name}: Total essays: {n}; Large-error essays: {count}")
    print("\nRanking strategies using the same large-error mask (Validation + Official Test):")
    for strategy in strategies:
        print(f"[PASS] {strategy}")
    sources(
        [
            (config_path, "reference, threshold, budget"),
            *label_paths,
            (helper8_path, "formula and common-mask metric helpers"),
            (helper9_path, "frozen formula and reference constants"),
            (pipeline8_path, "static verification of mask routing; not executed"),
            (pipeline9_path, "static verification of mask routing; not executed"),
            (manifest_path, "eligible population IDs"),
        ]
    )

    rater_path = "data/01_original_source/rater_scores/ellipsis_raw_rater_scores_anon_all_essay.csv"
    raters = load_allowlisted_rater_scores(
        ROOT / rater_path,
        validation.index,
        forbidden_ids=manifest.loc[manifest.split.eq("official_test"), "essay_id"],
    )
    require(set(raters.essay_id) == set(validation.index), "Incomplete paired Validation ratings")
    print("\n=== 2. HUMAN-RATER DISAGREEMENT ===\n")
    print(f"Number of essays: {len(raters)} (eligible Validation, two raters)")
    for target in references:
        metrics = rater_reliability_metrics(
            raters, rater_1_column=f"{target}_1", rater_2_column=f"{target}_2"
        )
        diff = abs(raters[f"{target}_1"] - raters[f"{target}_2"])
        print(f"\n{target}")
        print(f"Human-human MAE: {metrics['human_human_mae']:.4f}")
        print(f"QWK: {metrics['quadratic_weighted_kappa']:.4f}")
        print(f"ICC(A,1): {metrics['icc_a_1']:.4f}")
        print(f"Agreement within 0.5 point: {metrics['within_0_5_points_rate']:.2%}")
        print(f"Agreement within 1.0 point: {metrics['within_1_0_point_rate']:.2%}")
        for relation, mask in (
            ("<", diff.lt(threshold)),
            ("=", diff.eq(threshold)),
            (">", diff.gt(threshold)),
        ):
            print(f"difference {relation} {threshold:.1f}: {int(mask.sum())} ({mask.mean():.2%})")
    print("\nContext: A one-point deviation is a practical flag, not proof the model is wrong.")
    sources(
        [
            (rater_path, "raw paired scores; all agreement metrics and difference counts"),
            (prediction_path, "Validation ID allowlist"),
            (manifest_path, "Validation eligibility; exclude Official Test IDs"),
            ("src/mla_project/evaluation/rater_reliability.py", "existing QWK/ICC/MAE definitions"),
        ]
    )

    metrics_path = "docs/data/phase7_tables/regression_metrics.csv"
    summary_path = "outputs/phase6/training_summary.json"
    saved_metrics = csv(metrics_path)
    summary = json.loads((ROOT / summary_path).read_text(encoding="utf-8"))
    require(summary["validation_prediction_rows"] == len(validation), "Validation N mismatch")
    require(summary["official_test_loaded"] is False, "Training used Official Test")
    train_rows = int(
        (manifest.split.eq("model_train") & manifest.privacy_review_status.eq("not_flagged")).sum()
    )
    require(summary["model_train_rows"] == train_rows, "Training population mismatch")
    folds = set()
    print("\n=== 3. RIDGE VALIDATION RESULTS ===\n")
    print(f"Validation N: {len(validation)}")
    for target in references:
        name = f"ridge_{target.lower()}"
        metadata = summary["model_metadata"][name]
        require(metadata["eligible_fit_rows"] == train_rows, "Ridge fit population mismatch")
        require(sum(metadata["cv"]["fold_counts"].values()) == train_rows, "CV population mismatch")
        folds.add(metadata["cv"]["folds"])
        actual = {
            "mae": mean_absolute_error(validation[target], validation[name]),
            "rmse": np.sqrt(mean_squared_error(validation[target], validation[name])),
            "r2": r2_score(validation[target], validation[name]),
        }
        row = saved_metrics[saved_metrics.model.eq("Ridge") & saved_metrics.target.eq(target)]
        require(len(row) == 1, "Missing/duplicate saved Ridge metrics")
        row = row.iloc[0]
        require(row.n_samples == len(validation), "Saved metric N mismatch")
        print(f"\n{target}")
        for key, label in (("mae", "MAE "), ("rmse", "RMSE"), ("r2", "R2  ")):
            require(
                np.isclose(actual[key], row[key], rtol=0, atol=1e-10),
                f"Recomputed Ridge {target} {key} differs from saved metric",
            )
            print(f"{label}: {actual[key]:.7f}")
        qwk = next(
            (
                key
                for key in ("qwk", "quadratic_weighted_kappa")
                if key in row.index and pd.notna(row[key])
            ),
            None,
        )
        print(
            f"QWK : {row[qwk]:.7f}" if qwk else "QWK : Not available in saved Validation artifact"
        )
        alpha = metadata["best_parameters"]["alpha"]
        require(alpha == summary["selected_parameters"][name]["alpha"], "Saved alpha mismatch")
        print(f"Alpha: {alpha:g}")
    require(len(folds) == 1, "Ridge CV protocols differ")
    print(f"\nHyperparameter selection: {folds.pop()}-fold CV on model_train ({train_rows} essays)")
    print(f"Official Test used for tuning: {'YES' if summary['official_test_loaded'] else 'NO'}")
    sources(
        [
            (prediction_path, "Validation targets; recomputed MAE/RMSE/R2"),
            (phase6_path, "exact cross-check of saved Validation predictions"),
            (metrics_path, "cross-check MAE/RMSE/R2; QWK availability"),
            (summary_path, "alpha, CV folds, fit population, Official Test exclusion"),
            (manifest_path, "model_train and Validation population IDs"),
        ]
    )


if __name__ == "__main__":
    main()
