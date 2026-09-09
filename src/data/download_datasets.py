"""Download the sentence datasets and, optionally, the auxiliary CEFR word lexicon."""

from __future__ import annotations

import argparse
import tarfile
import urllib.request
from pathlib import Path

import pandas as pd
from datasets import load_dataset

SENTENCE_DATASETS = {
    "cefr_sp_en": "UniversalCEFR/cefr_sp_en",
    "readme_en": "UniversalCEFR/readme_en",
}
PINNED_REVISIONS = {
    "cefr_sp_en": "b78901348bda9f5a823cd3da1f3fcb2dcc6c5725",
    "readme_en": "88ce5b3736bdb666b1f64f738451676b12028a33",
}
LEXICON_URL = "https://zenodo.org/records/12501/files/word-level-survey.tar.gz?download=1"


def download_sentence_datasets(
    output_dir: Path,
    revision: str | None = None,
    force: bool = False,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for source_name, dataset_id in SENTENCE_DATASETS.items():
        destination = output_dir / f"{source_name}_train.csv"
        if destination.exists() and not force:
            print(f"[skip] {destination}")
            continue
        rev = revision if revision is not None else PINNED_REVISIONS.get(source_name)
        dataset = load_dataset(dataset_id, revision=rev)
        frame = pd.DataFrame(dataset["train"])
        frame.to_csv(destination, index=False, encoding="utf-8")
        print(f"[saved] {destination}: {len(frame):,} rows (revision={rev})")


def _safe_extract_tar(archive: Path, output_dir: Path) -> None:
    output_root = output_dir.resolve()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle.getmembers():
            destination = (output_dir / member.name).resolve()
            if output_root not in destination.parents and destination != output_root:
                raise RuntimeError(f"Unsafe path in archive: {member.name}")
        bundle.extractall(output_dir, filter="data")


def download_auxiliary_lexicon(output_dir: Path, force: bool = False) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    target_csv = output_dir / "WordsTeachersLevelsGoogleFrequenciesPredictions.csv"
    if target_csv.exists() and not force:
        print(f"[skip] {target_csv}")
        return
    archive = output_dir / "word-level-survey.tar.gz"
    request = urllib.request.Request(LEXICON_URL, headers={"User-Agent": "cefr-course-project"})
    with urllib.request.urlopen(request) as response, archive.open("wb") as handle:
        handle.write(response.read())
    _safe_extract_tar(archive, output_dir)
    print(f"[saved] auxiliary lexicon under {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--revision", help="Pinned Hugging Face revision for reproducibility")
    parser.add_argument(
        "--include-auxiliary-lexicon",
        action="store_true",
        help="Download the optional word-level resource used by three aggregate features",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force redownload even if files already exist",
    )
    args = parser.parse_args()

    download_sentence_datasets(
        Path("data/raw/cefr_sentence"),
        revision=args.revision,
        force=args.force,
    )
    if args.include_auxiliary_lexicon:
        download_auxiliary_lexicon(Path("data/raw/cefr_wordlist"), force=args.force)


if __name__ == "__main__":
    main()
