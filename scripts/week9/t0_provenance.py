"""Task 0 only: reproduce frozen primary rankings from saved predictions; no models.

Default: read-only reproduction from tracked predictions and saved human targets.
Run --capture to repeat in fresh processes without writing reports.
Legacy external-data inventory/reproduction remains available with --external-data.
"""
from pathlib import Path
import csv
import hashlib
import io
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import scipy
from scipy.stats import hypergeom

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "reports/week9"
SEED = 42
COMMAND = '.venv/Scripts/python.exe scripts/week9/t0_provenance.py'
PATHS = [
    "docs/evaluation_protocol_freeze.md",
    "outputs/phase6/validation_predictions.csv",
    "outputs/predictions/phase7_validation_regression_predictions.csv",
    "outputs/predictions/official_test_predictions.csv",
    "scripts/phase8_evaluate_review_prioritization.py",
    "scripts/phase9_official_test_evaluation.py",
    "src/mla_project/evaluation/phase8.py",
    "src/mla_project/evaluation/phase9.py",
    "src/mla_project/review/baselines.py",
    "scripts/finalization_supplement.py",
    "docs/data/phase9_tables/artifact_manifest.json",
    "docs/data/phase8_tables/large_error_labels.csv",
    "docs/data/phase9_tables/large_error_labels.csv",
    "docs/data/phase8_tables/random_reference_distribution.csv",
    "docs/data/phase9_tables/random_reference_distribution.csv",
    "docs/data/phase8_tables/review_strategy_comparison.csv",
    "docs/data/phase9_tables/review_strategy_comparison.csv",
    "data/05_model_features/development_features_with_targets.csv",
    "data/05_model_features/official_test_features.csv",
    "data/03_clean_ready_to_use/official_test_2571.csv",
    "data/02_split_manifest/essay_split_manifest.csv",
]

def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT).decode("utf-8", errors="replace")

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path, cols=None):
    frame = pd.read_csv(ROOT / path, usecols=cols, dtype={"essay_id": str})
    if "essay_id" in frame:
        assert frame.essay_id.notna().all() and not frame.essay_id.duplicated().any(), path
    return frame

def save_csv(name, rows):
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / name, index=False, lineterminator="\n", float_format="%.17g")
    return frame

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"COMMAND: {COMMAND}")
    print(f"seed={SEED}; draws=1000; threshold=1.0; budget=0.20; aggregation=max; tie=essay_id string ascending")
    print(f"Python={sys.version.split()[0]}; numpy={np.__version__}; pandas={pd.__version__}; scipy={scipy.__version__}")
    before = {p: digest((ROOT / p).read_bytes()) for p in PATHS}
    inventory = []
    for path in PATHS:
        history = git("log", "--follow", "--format=%H|%aI|%cI|%s", "--", path).splitlines()
        stat = (ROOT / path).stat()
        row = dict(path=path, bytes=stat.st_size,
                   modified_utc=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                   first_commit=history[-1] if history else "NO GIT HISTORY",
                   last_commit=history[0] if history else "NO GIT HISTORY", sha256=before[path])
        inventory.append(row)
        print("INVENTORY " + json.dumps(row, ensure_ascii=True))
    save_csv("t0_inventory.csv", inventory)
    history = git("log", "--since=2026-10-01", "--stat", "--date=iso-strict", "--format=fuller")
    (OUT / "t0_git_since_freeze.txt").write_text(history, encoding="utf-8")
    print("COMMAND: git log --since=2026-10-01 --stat --date=iso-strict --format=fuller")
    print(history, end="" if history.endswith("\n") else "\n")
    changes = []
    for commit in git("log", "--since=2026-10-01", "--format=%H").splitlines():
        for line in git("diff-tree", "--root", "--no-commit-id", "--name-status", "-r", commit).splitlines():
            changes.append(dict(commit=commit, change=line,
                classification="UNKNOWN: first Test evaluation date not established"))
    save_csv("t0_committed_changes.csv", changes)
    status = git("status", "--porcelain=v1", "--untracked-files=all")
    (OUT / "t0_worktree_status.txt").write_text(status, encoding="utf-8")
    print("CHRONOLOGY: first Test evaluation date cannot be determined from available Git history; file mtimes are not execution timestamps.")
    print("CHRONOLOGY: docs/phase9_official_test_evaluation.md first/last history:")
    print(git("log", "--follow", "--format=%H|%aI|%cI|%s", "--", "docs/phase9_official_test_evaluation.md"), end="")
    print("WORKTREE: existing uncommitted/untracked changes have no reliable modification chronology; see t0_worktree_status.txt.")
    manifest = json.loads((ROOT / "docs/data/phase9_tables/artifact_manifest.json").read_text())
    assert before["docs/evaluation_protocol_freeze.md"].upper() == manifest["protocol_sha256"]
    for path, expected in manifest["output_sha256"].items():
        assert digest((ROOT / path).read_bytes()).upper() == expected.upper(), path
    for name, path in [("official_test_features", PATHS[18]), ("official_test_labels", PATHS[19]), ("split_manifest", PATHS[20])]:
        assert before[path].upper() == manifest["input_sha256"][name].upper(), path
    print("INTEGRITY: frozen protocol, saved Test outputs, Test feature/label sources and split manifest match saved manifest SHA256.")
    centers = manifest["frozen_ridge_centers"]
    print("FROZEN_CENTERS " + json.dumps(centers, sort_keys=True))
    results = []
    predcols = ["essay_id", "ridge_vocabulary", "ridge_grammar", "random_forest_vocabulary", "random_forest_grammar"]
    for split, phase, expected in [("Validation", 8, (762, 69, 153, 15, 13.946)), ("Test", 9, (2518, 208, 504, 47, 41.427))]:
        predpath = PATHS[1] if phase == 8 else PATHS[3]
        pred = read(predpath, predcols)
        # Saved labels supply y only; never reuse precomputed error flags as the calculation.
        labels = read(f"docs/data/phase{phase}_tables/large_error_labels.csv", ["essay_id", "Vocabulary", "Grammar"])
        assert set(pred.essay_id) == set(labels.essay_id), split
        if phase == 8:
            features = read(PATHS[17], ["essay_id", "word_count"])
        else:
            features = read(PATHS[18], ["essay_id", "word_count"])
        # Original Test population follows eligible manifest order; Validation follows development order.
        if phase == 8:
            base = features.loc[features.essay_id.isin(set(pred.essay_id))]
        else:
            population = read(PATHS[20], ["essay_id", "split", "privacy_review_status"])
            base = population.loc[population.split.eq("official_test") & population.privacy_review_status.eq("not_flagged"), ["essay_id"]].merge(features, on="essay_id", validate="one_to_one", sort=False)
        assert set(base.essay_id) == set(pred.essay_id), split
        frame = base.merge(labels, on="essay_id", validate="one_to_one", sort=False).merge(pred, on="essay_id", validate="one_to_one", sort=False)
        large = np.maximum(abs(frame.Vocabulary - frame.random_forest_vocabulary), abs(frame.Grammar - frame.random_forest_grammar)) >= 1.0
        frame["D"] = np.maximum(abs(frame.ridge_vocabulary-frame.random_forest_vocabulary), abs(frame.ridge_grammar-frame.random_forest_grammar))
        frame["E"] = np.maximum(abs(frame.ridge_vocabulary-centers["median_ridge_vocabulary"]), abs(frame.ridge_grammar-centers["median_ridge_grammar"]))
        frame["L"] = large
        n, K = len(frame), int(large.sum())
        k = math.ceil(0.2*n)
        caught = {}
        for name, col, asc in [("Shortest-first", "word_count", True), ("Ridge extremity", "E", False), ("Disagreement", "D", False)]:
            caught[name] = int(frame.sort_values([col,"essay_id"], ascending=[asc, True], kind="stable").head(k).L.sum())
        rng = np.random.default_rng(SEED)
        draws = np.array([int(large.iloc[rng.choice(n, size=k, replace=False)].sum()) for _ in range(1000)])
        saved = read(f"docs/data/phase{phase}_tables/random_reference_distribution.csv")
        saved = saved.loc[saved.error_threshold.eq(1) & saved.review_budget.eq(0.2)]
        assert np.array_equal(draws, saved.captured_count.to_numpy()), f"{split}: random draws do not reproduce"
        assert (n,K,k,caught["Disagreement"],float(draws.mean())) == expected, f"{split}: reported numbers differ"
        if phase == 9:
            assert int((draws >= 47).sum()) == 165
        saved_metrics = read(f"docs/data/phase{phase}_tables/review_strategy_comparison.csv")
        saved_metrics = saved_metrics.loc[saved_metrics.error_threshold.eq(1) & saved_metrics.review_budget.eq(0.2)]
        for name, count in caught.items():
            original_name = "Ridge-RF disagreement" if name == "Disagreement" else name
            assert float(saved_metrics.loc[saved_metrics.strategy.eq(original_name),"captured_count"].iloc[0]) == count
        save_csv(f"t0_{split.lower()}_draws.csv", [dict(draw=i+1,caught=int(x)) for i,x in enumerate(draws)])
        d = caught["Disagreement"]
        row = dict(split=split,N=n,K=K,k=k,shortest=caught["Shortest-first"],ridge_extremity=caught["Ridge extremity"],disagreement=d,random_mean=float(draws.mean()),random_first_draw=int(draws[0]),random_p2_5=float(np.percentile(draws,2.5)),random_p97_5=float(np.percentile(draws,97.5)),tail_draws=int((draws>=d).sum()),draws=1000,seed=SEED,hypergeom_p=float(hypergeom.sf(d-1,n,K,k)),expected_random=k*K/n)
        results.append(row)
        print("RESULT " + json.dumps(row,sort_keys=True))
        print(f"ARITHMETIC {split}: random_mean={int(draws.sum())}/1000={draws.mean():.12g}; empirical_p={row['tail_draws']}/1000={row['tail_draws']/1000:.12g}; expected={k}*{K}/{n}={k*K/n:.12g}; capture={d}/{K}={d/K:.12g}; exact_p=hypergeom.sf({d-1},{n},{K},{k})={row['hypergeom_p']:.12g}")
    save_csv("t0_metrics.csv", results)
    assert before == {p: digest((ROOT/p).read_bytes()) for p in PATHS}
    print("INTEGRITY: all inventoried source files unchanged after reproduction.")
    print("INTERPRETATION: disagreement is NOT demonstrated better than random.")
    print("STATUS: PARTIAL provenance chronology; numerical reproduction complete. Missing: independently established first Test execution date and before/after classification of changes.")

def capture():
    (OUT / "logs").mkdir(parents=True,exist_ok=True)
    outputs = []
    for i in (1,2):
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve())],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        outputs.append(proc.stdout)
        (OUT / f"logs/t0_run{i}.log").write_bytes(proc.stdout)
        sys.stdout.buffer.write(proc.stdout)
        sys.stdout.buffer.flush()
        if proc.returncode:
            (OUT / "logs/t0.log").write_bytes(b"\n".join(outputs))
            raise SystemExit("DISCREPANCY: Task 0 stopped; see raw log. No further evaluation performed.")
    hashes = [digest(x) for x in outputs]
    proof = f"RUN1_SHA256={hashes[0]}\nRUN2_SHA256={hashes[1]}\nIDENTICAL_RAW_OUTPUT={outputs[0]==outputs[1]}\n"
    (OUT / "logs/t0.log").write_bytes(b"RUN 1\n"+outputs[0]+b"RUN 2\n"+outputs[1]+proof.encode())
    print(proof,end="")
    assert outputs[0] == outputs[1]
    # Quote actual raw evidence rather than a narrative substituted for terminal output.
    lines = outputs[0].decode().splitlines()
    relevant = [x for x in lines if x.startswith(("seed=","Python=","RESULT ","ARITHMETIC ","CHRONOLOGY:","INTEGRITY:","STATUS:"))]
    inventory = pd.read_csv(OUT / "t0_inventory.csv").fillna("")
    md = ["# Task 0 — PARTIAL (chronology limitation)", "", "Numerical reproduction complete. Disagreement is NOT demonstrated better than random. The date Test was first evaluated cannot be established from the available history; therefore committed and uncommitted changes cannot honestly be classified before/after first access.", "", "## Reproduction and evidence", "", f"Script: `scripts/week9/t0_provenance.py`. Exact entry command: `.venv/Scripts/python.exe scripts/week9/t0_provenance.py --capture`. Each child command: `{COMMAND}`. Saved predictions only; no fitting, model loading or prediction. Test reads are confined to this Task 0 reproduction. Frozen primary definitions only.", "", "Raw combined terminal output: `logs/t0.log`; individual fresh-process outputs: `logs/t0_run1.log`, `logs/t0_run2.log`. CSV row references below mean data rows, excluding the header.", "", "```text", *relevant, "```", "", "[src: reports/week9/logs/t0_run1.log RESULT, ARITHMETIC, CHRONOLOGY, INTEGRITY and STATUS lines]", "", "Random is represented by the mean over the frozen draws; the first draw is also provided in the metrics CSV. Percentiles use NumPy's default linear interpolation. Exact p is the hypergeometric survival function, not the empirical tail proportion. Arithmetic for means, capture, expected counts and empirical p is printed verbatim above. No new Test design or sensitivity analysis was run.", ""]
    for i,row in enumerate(pd.read_csv(OUT / "t0_metrics.csv").to_dict("records"),1):
        md += [f"{row['split']}: see the verbatim RESULT and ARITHMETIC lines above. [src: reports/week9/t0_metrics.csv row {i}]", ""]
    md += ["## Artifact inventory", "", "Dates are filesystem modification times in UTC and Git author/committer timestamps. Git first/last means oldest/newest entry from `git log --follow`, not an execution date. Empty history is explicitly reported. The original scripts are inventoried but were not executed, because the Test script generates predictions and existing outputs.", "", "| Path | Bytes | Modified UTC | First commit (hash, author, committer, subject) | Last commit | Evidence |", "|---|---:|---|---|---|---|"]
    for i,row in enumerate(inventory.to_dict("records"),1):
        md.append("| "+" | ".join([f"`{row['path']}`",str(row['bytes']),row['modified_utc'],row['first_commit'].replace('|',' / '),row['last_commit'].replace('|',' / '),f"[src: reports/week9/t0_inventory.csv row {i}]"])+" |")
    md += ["", "SHA256 values for all listed sources are in the same inventory. Validation's Phase 6 file is the prediction source used by the original ranking script; the Phase 7 copy is inventoried for discovery completeness. Saved large-error tables supply human target means; error flags are recomputed directly from the saved RF predictions. Saved manifest medians supply the frozen Ridge extremity centers.", "", "## Changes since freeze and chronology", "", "Full requested Git stat output is preserved in `t0_git_since_freeze.txt` and printed verbatim in both raw runs. Every committed changed path is enumerated in `t0_committed_changes.csv`, with classification UNKNOWN because first Test access is undated. The Test report's first/last commit evidence is in the CHRONOLOGY section of the raw log. A commit containing an existing Test report establishes report presence at that commit; it does not date first Test access or order edits within that commit. The protocol's stated freeze date is a document assertion rather than independently timestamped execution evidence.", "", "`t0_worktree_status.txt` separately records current tracked edits and untracked paths, including pre-existing work. Git log cannot date those changes; filesystem mtimes cannot prove whether they precede Test access. No before/after labels have been guessed. No existing result, protocol, README or manual sample was modified; no commit or push was performed.", "", "## Fresh-process repeat proof", "", "```text", proof.rstrip(), "```", "", "[src: reports/week9/logs/t0.log final hash lines]", "", "Missing for full completion: independent evidence of the first Test evaluation timestamp and a defensible before/after classification of each change. All numerical checks and frozen saved-output comparisons passed, as shown by the raw logs.", ""]
    (OUT / "t0_provenance.md").write_text("\n".join(md),encoding="utf-8")

PREDICTION_HASHES = {
    "outputs/phase6/validation_predictions.csv": "6e86fe84b32219a6798a523c0e11c1e28b5f4036e31e182d3c349631c29ec3ab",
    "outputs/predictions/phase7_validation_regression_predictions.csv": "da86cf4be3b05790db65ceb6381d75ad77fce695694e8c62a9a03dcf7493c1d0",
    "outputs/predictions/official_test_predictions.csv": "48eb85d8bda27dd6261179d839fd5377d694741c5740f94ac88029b0593393e8",
}


def prediction_only():
    """Recompute the existing primary results; never write artifacts or fit models."""
    print("COMMAND: python scripts/week9/t0_provenance.py")
    print(f"Python={sys.version.split()[0]}; numpy={np.__version__}; pandas={pd.__version__}; scipy={scipy.__version__}")
    print("SKIPPED: requires external ELLIPSE data (not distributed)")
    print("External dataset/feature inventory, shortest-first and original source checks remain in --external-data; no fitting or prediction is run.")
    print("INPUTS: three tracked prediction CSVs; tracked Phase 8/9 label tables (human Vocabulary/Grammar only); reports/week9/RESULTS_week9.md (expected values).")
    print("DEPENDENCY: finalization_supplement.py was inventoried only, never imported/called; not needed or published.")
    paths = [*PREDICTION_HASHES, "docs/data/phase8_tables/large_error_labels.csv",
             "docs/data/phase9_tables/large_error_labels.csv", "reports/week9/RESULTS_week9.md"]
    before = {path: digest((ROOT / path).read_bytes()) for path in paths}

    def check(name, actual, expected, close=False):
        ok = math.isclose(actual, expected, rel_tol=1e-13, abs_tol=1e-15) if close else actual == expected
        print(f"{'PASS' if ok else 'FAIL'} | {name} | actual={actual} | expected={expected}")
        if not ok:
            raise SystemExit(1)

    for path, expected in PREDICTION_HASHES.items():
        check("SHA256 " + path, before[path], expected)
    report = (ROOT / "reports/week9/RESULTS_week9.md").read_text(encoding="utf-8")
    rounded = float(re.search(r"rounded to one decimal place `([0-9.]+)`", report).group(1))
    print("FORMULAS: L_i = max(abs(y_V-RF_V),abs(y_G-RF_G)) >= 1; D_i = max(abs(Ridge_V-RF_V),abs(Ridge_G-RF_G)); top ceil(.20*N), D descending, essay_id string ascending.")
    for split, phase, path in [("Validation", 8, PATHS[1]), ("Test", 9, PATHS[3])]:
        cells = next(line for line in report.splitlines() if line.startswith(f"| {split} |" )).strip("| ").split("|")
        cells = [cell.strip() for cell in cells]
        n0, K0, k0 = map(int, cells[1:4])
        d0, mean0, p0 = int(cells[6]), float(cells[7]), float(cells[10])
        labels = read(f"docs/data/phase{phase}_tables/large_error_labels.csv", ["essay_id", "Vocabulary", "Grammar"])
        pred = read(path)
        assert set(pred.essay_id) == set(labels.essay_id), split
        frame = pred.merge(labels, on="essay_id", validate="one_to_one", sort=False)
        large = np.maximum(abs(frame.Vocabulary-frame.random_forest_vocabulary), abs(frame.Grammar-frame.random_forest_grammar)) >= 1.0
        frame["L"] = large
        frame["D"] = np.maximum(abs(frame.ridge_vocabulary-frame.random_forest_vocabulary), abs(frame.ridge_grammar-frame.random_forest_grammar))
        n, K = len(frame), int(large.sum())
        k = math.ceil(.20*n)
        caught = int(frame.sort_values(["D", "essay_id"], ascending=[False, True], kind="stable").head(k).L.sum())
        rng = np.random.default_rng(SEED)
        draws = np.array([int(large.iloc[rng.choice(n, size=k, replace=False)].sum()) for _ in range(1000)])
        mean = float(draws.mean())
        p = float(hypergeom.sf(caught-1, n, K, k))
        print(f"ARITHMETIC {split}: N={n}; K=sum(L_i)={K}; k=ceil(0.20*{n})={k}; caught=sum(L_i in top {k})={caught}; capture={caught}/{K}={caught/K:.12g}")
        print(f"ARITHMETIC {split}: random_mean={int(draws.sum())}/1000={mean}; rounded_1dp={mean:.1f}; expected_random={k}*{K}/{n}={k*K/n}; empirical_tail={int((draws>=caught).sum())}/1000={float((draws>=caught).mean())}")
        print(f"ARITHMETIC {split}: exact_p=sum(comb({K},x)*comb({n-K},{k}-x)/comb({n},{k}), x={caught}..{min(K,k)})=hypergeom.sf({caught-1},{n},{K},{k})={p!r}")
        check(split + " N,K,k", (n,K,k), (n0,K0,k0))
        check(split + " caught count", caught, d0)
        check(split + " caught/K", f"{caught}/{K}", f"{d0}/{K0}")
        check(split + " random mean", mean, mean0)
        if split == "Test":
            check("Test rounded random mean", float(f"{mean:.1f}"), rounded)
        check(split + " exact hypergeometric p", p, p0, close=True)
    check("all input hashes unchanged", all(digest((ROOT/path).read_bytes()) == before[path] for path in paths), True)
    print("CHRONOLOGY: first Test evaluation date cannot be determined from available Git history; file mtimes are not execution timestamps.")
    print("STATUS: PASS numerical reproduction; chronology unresolved; public repo is not an independent replication")


def repeat_read_only():
    outputs = []
    for _ in range(2):
        proc = subprocess.run([sys.executable, str(Path(__file__).resolve())], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sys.stdout.buffer.write(proc.stdout)
        sys.stdout.buffer.flush()
        if proc.returncode:
            raise SystemExit(proc.returncode)
        outputs.append(proc.stdout)
    print(f"RUN1_SHA256={digest(outputs[0])}\nRUN2_SHA256={digest(outputs[1])}\nIDENTICAL_RAW_OUTPUT={outputs[0] == outputs[1]}")
    if outputs[0] != outputs[1]:
        raise SystemExit(1)


if __name__ == "__main__":
    if "--external-data" in sys.argv:
        if not all((ROOT / path).is_file() for path in PATHS):
            print("SKIPPED: requires external ELLIPSE data (not distributed)")
        else:
            main()
    elif "--capture" in sys.argv:
        repeat_read_only()
    else:
        prediction_only()
