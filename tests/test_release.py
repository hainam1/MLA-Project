import json

import pytest

from src.release.build_release import sha256, verify_release, write_reproducible_zip


def test_reproducible_zip_has_stable_checksum(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "a.txt").write_text("same content", encoding="utf-8")
    first, second = tmp_path / "first.zip", tmp_path / "second.zip"
    write_reproducible_zip(first, source, [source / "a.txt"])
    write_reproducible_zip(second, source, [source / "a.txt"])
    assert sha256(first) == sha256(second)


def test_verify_release_detects_tampering(tmp_path):
    archive = tmp_path / "source.zip"
    archive.write_bytes(b"release")
    (tmp_path / "release.json").write_text(json.dumps({"version": "0.1.0"}))
    (tmp_path / "checksums.sha256").write_text(f"{sha256(archive)}  source.zip\n", encoding="utf-8")
    assert verify_release(tmp_path) == []
    archive.write_bytes(b"tampered")
    assert verify_release(tmp_path) == ["hash mismatch: source.zip"]


def test_full_bundle_requires_noncommercial_acknowledgement(tmp_path):
    from src.release.build_release import build_release

    with pytest.raises(ValueError, match="non-commercial"):
        build_release("0.1.0", tmp_path)


def test_source_only_release_builds_and_verifies(tmp_path):
    from src.release.build_release import build_release

    release_dir = build_release("0.1.0", tmp_path, source_only=True)
    assert verify_release(release_dir) == []
    metadata = json.loads((release_dir / "release.json").read_text(encoding="utf-8"))
    assert metadata["source_only"] is True
    assert metadata["commercial_use_allowed"] is False
