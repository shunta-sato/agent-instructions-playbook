#!/usr/bin/env python3
"""Synchronize .agents/skills (source of truth) to .github/skills mirror."""

from __future__ import annotations

import argparse
import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path


MAX_DIFFS_TO_PRINT = 50


@dataclass(frozen=True)
class DiffEntry:
    kind: str
    path: str


def _file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _collect_files(root: Path) -> dict[str, str]:
    if not root.exists():
        return {}

    files: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = p.relative_to(root).as_posix()
            files[rel] = _file_hash(p)
    return files


def _diff(src: Path, dst: Path) -> list[DiffEntry]:
    src_files = _collect_files(src)
    dst_files = _collect_files(dst)

    diffs: list[DiffEntry] = []

    for rel in sorted(src_files.keys() - dst_files.keys()):
        diffs.append(DiffEntry("missing_in_mirror", rel))

    for rel in sorted(dst_files.keys() - src_files.keys()):
        diffs.append(DiffEntry("extra_in_mirror", rel))

    for rel in sorted(src_files.keys() & dst_files.keys()):
        if src_files[rel] != dst_files[rel]:
            diffs.append(DiffEntry("content_mismatch", rel))

    return diffs


def _write(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Fail if mirror is out of sync")
    ap.add_argument("--write", action="store_true", help="Rewrite mirror from source")
    ap.add_argument(
        "--repo-root",
        type=str,
        default="",
        help="Repo root (default: parent of scripts/)",
    )
    args = ap.parse_args()

    if args.check == args.write:
        ap.error("Specify exactly one mode: --check or --write")

    repo_root = (
        Path(args.repo_root).resolve()
        if args.repo_root
        else Path(__file__).resolve().parent.parent
    )
    src = repo_root / ".agents" / "skills"
    dst = repo_root / ".github" / "skills"

    if not src.exists():
        print(f"Source skills directory does not exist: {src}")
        return 2

    if args.write:
        _write(src, dst)
        print(f"Synchronized {src} -> {dst}")
        return 0

    diffs = _diff(src, dst)
    if not diffs:
        print("Skill directories are in sync.")
        return 0

    print("Skill mirror is out of sync (.agents/skills -> .github/skills).")
    print("Run: python scripts/sync_agent_skills.py --write")
    print(f"Differences: {len(diffs)}")
    for d in diffs[:MAX_DIFFS_TO_PRINT]:
        print(f"- {d.kind}: {d.path}")
    if len(diffs) > MAX_DIFFS_TO_PRINT:
        print(f"... and {len(diffs) - MAX_DIFFS_TO_PRINT} more")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
