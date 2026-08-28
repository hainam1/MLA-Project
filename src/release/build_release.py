"""Build and verify reproducible source/model release bundles."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from src.artifacts.build_manifest import PROJECT_ROOT, verify_manifest
from src.version import __version__

FIXED_ZIP_TIME = (2020, 1, 1, 0, 0, 0)
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
SOURCE_FILES = [
    ".flake8",
    ".gitignore",
    "README.md",
    "HANDOFF.md",
    "TASKS.md",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "configs/config.yaml",
    "artifacts/manifest.json",
    "reports/00_dataset_licenses.md",
    "reports/model4_failure_review_guide.md",
    "src/web/index.html",
    "data/external/nltk_data/SOURCE.md",
    "data/external/vi_en_dictionary/SOURCE.md",
    "data/evaluation/vocabulary_translation_gold.csv",
    "src/models/semantic_reranker/SOURCE.md",
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_paths(root: Path) -> list[Path]:
    paths = [root / relative for relative in SOURCE_FILES if (root / relative).is_file()]
    paths.extend(path for path in (root / "src").rglob("*.py") if "__pycache__" not in path.parts)
    return sorted(set(paths), key=lambda path: path.relative_to(root).as_posix())


def write_reproducible_zip(destination: Path, root: Path, paths: list[Path]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED) as archive:
        for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix()):
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            with path.open("rb") as source, archive.open(info, "w") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)


def git_state(root: Path) -> dict:
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                capture_output=True,
                text=True,
                check=True,
            ).stdout.strip()
        )
        return {"commit": commit, "dirty_worktree": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_worktree": None}


def build_release(
    version: str,
    output_root: Path,
    *,
    source_only: bool = False,
    allow_noncommercial: bool = False,
    overwrite: bool = False,
    require_clean: bool = False,
) -> Path:
    if not VERSION_PATTERN.fullmatch(version):
        raise ValueError("version must be SemVer, for example 0.1.0")
    if not source_only and not allow_noncommercial:
        raise ValueError("model bundle contains non-commercial data; pass --allow-noncommercial")

    artifact_manifest = PROJECT_ROOT / "artifacts/manifest.json"
    if not source_only:
        failures = verify_manifest(artifact_manifest)
        if failures:
            raise ValueError("artifact manifest verification failed: " + "; ".join(failures))
    repository_state = git_state(PROJECT_ROOT)
    if require_clean and repository_state["dirty_worktree"] is not False:
        raise ValueError("release requires a clean Git worktree")

    release_dir = output_root / f"capyvocab-ml-{version}"
    if release_dir.exists() and not overwrite:
        raise FileExistsError(f"release directory already exists: {release_dir}")
    release_dir.mkdir(parents=True, exist_ok=overwrite)

    source_archive = release_dir / f"capyvocab-ml-source-{version}.zip"
    write_reproducible_zip(source_archive, PROJECT_ROOT, source_paths(PROJECT_ROOT))
    archives = [source_archive]

    if not source_only:
        manifest = json.loads(artifact_manifest.read_text(encoding="utf-8"))
        model_paths = [PROJECT_ROOT / item["path"] for item in manifest["artifacts"]]
        model_paths.append(artifact_manifest)
        model_archive = release_dir / f"capyvocab-ml-models-{version}.zip"
        write_reproducible_zip(model_archive, PROJECT_ROOT, model_paths)
        archives.append(model_archive)

    release_metadata = {
        "schema_version": 1,
        "project": "capyvocab-ml",
        "version": version,
        "code_version": __version__,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "git": repository_state,
        "source_only": source_only,
        "commercial_use_allowed": False,
        "license_notice": "Contains or references non-commercial corpora; research use only.",
        "model4_included": False,
        "archives": [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in archives
        ],
        "artifact_manifest_sha256": sha256(artifact_manifest),
    }
    metadata_path = release_dir / "release.json"
    metadata_path.write_text(
        json.dumps(release_metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    checksum_paths = [*archives, metadata_path]
    checksum_text = "".join(f"{sha256(path)}  {path.name}\n" for path in checksum_paths)
    (release_dir / "checksums.sha256").write_text(checksum_text, encoding="utf-8")
    return release_dir


def verify_release(release_dir: Path) -> list[str]:
    checksum_file = release_dir / "checksums.sha256"
    if not checksum_file.exists():
        return ["missing: checksums.sha256"]
    failures = []
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        path = release_dir / name
        if not path.exists():
            failures.append(f"missing: {name}")
        elif sha256(path) != expected:
            failures.append(f"hash mismatch: {name}")
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build")
    build.add_argument("--version", default=__version__)
    build.add_argument("--output", type=Path, default=PROJECT_ROOT / "dist")
    build.add_argument("--source-only", action="store_true")
    build.add_argument("--allow-noncommercial", action="store_true")
    build.add_argument("--overwrite", action="store_true")
    build.add_argument("--require-clean", action="store_true")
    verify = subparsers.add_parser("verify")
    verify.add_argument("release_dir", type=Path)
    args = parser.parse_args()

    if args.command == "build":
        destination = build_release(
            args.version,
            args.output,
            source_only=args.source_only,
            allow_noncommercial=args.allow_noncommercial,
            overwrite=args.overwrite,
            require_clean=args.require_clean,
        )
        try:
            print(destination.relative_to(PROJECT_ROOT))
        except ValueError:
            print(destination.name)
    else:
        failures = verify_release(args.release_dir)
        if failures:
            raise SystemExit("\n".join(failures))
        print("Release verification passed")


if __name__ == "__main__":
    main()
