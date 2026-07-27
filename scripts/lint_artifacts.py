#!/usr/bin/env python3
"""Lint artifact instances against `.agents/artifact-registry.json`.

Continues the lint-migration program (`plans/20260725-lint-migration.md`,
`plans/20260726-artifact-registry.md`): SKILLs own the judgment of when/why
to produce an artifact; this registry + lint own acceptability. Each
registered kind declares a detection rule and a `checker` name; checker
modules share one signature and return stable finding-id strings:

    run_checks(repo_root: Path, artifact_path: Path, spec: dict,
               registry: dict) -> list[str]

"docs" -> `artifact_checks_docs.run_checks` (heading structure).
"packs" -> `artifact_checks_packs.run_checks` (self-contained pack structure).
Both are imported with the dual-path pattern used by
`scripts/report_skill_inventory.py`, but resolved per declared checker name
(not unconditionally): a registry kind that declares a checker this tool
cannot import is a silent coverage gap, so resolution happens for every
checker name any kind declares, regardless of that kind's current instance
count, and fails loudly naming the module rather than skipping silently.

Findings are ratcheted against a committed baseline (default
`scripts/artifact_lint_baseline.json`, map: repo-relative artifact path ->
sorted finding ids; exact membership, same shrink-the-list semantics as
`scripts/instruction_graph_baseline.json` / `skill_inventory_baseline.json`).
A current finding absent from its path's baseline entry is a new finding
(error under normal run); a baseline finding id no longer produced is
reported as informational `stale-baseline` (shrinkage is the goal).
`--write-baseline` writes the current findings and exits without ratcheting.

Exit code 0 when clean (or writing the baseline), 1 when new findings exist.
Only Python stdlib is used.
"""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Callable

REGISTRY_RELPATH = ".agents/artifact-registry.json"
DEFAULT_BASELINE_RELPATH = "scripts/artifact_lint_baseline.json"

# checker name -> (dotted module path, bare module name) for the dual-path
# import pattern (package execution vs. direct script execution).
CHECKER_MODULES: dict[str, tuple[str, str]] = {
    "docs": ("scripts.artifact_checks_docs", "artifact_checks_docs"),
    "packs": ("scripts.artifact_checks_packs", "artifact_checks_packs"),
    "learning": ("scripts.artifact_checks_learning", "artifact_checks_learning"),
}

Checker = Callable[[Path, Path, dict, dict], list]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lint artifact instances against the artifact registry."
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root to scan (default: inferred from this script location).",
    )
    parser.add_argument(
        "--write-baseline",
        action="store_true",
        help=(
            "Write the current findings to the baseline path "
            f"(default {DEFAULT_BASELINE_RELPATH}) and exit; does not ratchet."
        ),
    )
    return parser.parse_args(argv)


def repo_root_from_args(explicit_root: str) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()
    return Path(__file__).resolve().parent.parent


def repo_relative(repo_root: Path, path: Path) -> str:
    # No .resolve(): paths come from repo_root.glob, and resolving would key
    # a symlinked artifact under its target instead of the path that was
    # linted (and crash on out-of-repo targets).
    return path.relative_to(repo_root).as_posix()


def load_registry(repo_root: Path) -> dict:
    path = repo_root / REGISTRY_RELPATH
    if not path.is_file():
        raise SystemExit(f"artifact-lint: registry not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"artifact-lint: invalid JSON in {path}: {exc}")
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise SystemExit(
            f"artifact-lint: unsupported schema_version "
            f"{data.get('schema_version') if isinstance(data, dict) else None!r} "
            f"in {path} (expected 1)"
        )
    return data


def _import_checker(checker_name: str) -> Checker:
    if checker_name not in CHECKER_MODULES:
        raise SystemExit(f"artifact-lint: unknown checker {checker_name!r}")
    dotted, bare = CHECKER_MODULES[checker_name]
    try:
        module = importlib.import_module(dotted)
    except ImportError:
        try:
            module = importlib.import_module(bare)
        except ImportError as exc:
            raise SystemExit(
                f"artifact-lint: checker module for {checker_name!r} is not "
                f"importable ({dotted} / {bare}): {exc}. A registered artifact "
                "kind cannot be checked until that module lands -- refusing "
                "to silently skip it."
            )
    return module.run_checks


def resolve_checkers(registry: dict) -> dict[str, Checker]:
    """One run_checks callable per distinct `checker` name declared by any
    artifact kind in the registry, regardless of that kind's current
    instance count -- see module docstring."""
    needed = set()
    for kind_name, spec in registry.get("artifacts", {}).items():
        if "checker" not in spec:
            raise SystemExit(f"artifact-lint: kind {kind_name!r} has no checker field")
        needed.add(spec["checker"])
    return {name: _import_checker(name) for name in sorted(needed)}


def discover_instances(repo_root: Path, kind_name: str, spec: dict) -> list[Path]:
    exclude = set(spec.get("exclude", []))

    def kept(path: Path) -> bool:
        # Directory indexes and _-prefixed templates are never artifact
        # instances, for any kind (the plans/README.md lesson).
        if path.name == "README.md" or path.name.startswith("_"):
            return False
        return repo_relative(repo_root, path) not in exclude

    if "detect_glob" in spec:
        return [
            p
            for p in sorted(repo_root.glob(spec["detect_glob"]))
            if p.is_file() and kept(p)
        ]
    if "detect_dir_glob" in spec:
        return [
            p
            for p in sorted(repo_root.glob(spec["detect_dir_glob"]))
            if p.is_dir() and kept(p)
        ]
    if "detect_dir" in spec:
        path = repo_root / spec["detect_dir"]
        return [path] if path.is_dir() and kept(path) else []
    raise SystemExit(f"artifact-lint: kind {kind_name!r} has no detect_* rule")


def collect_findings(
    repo_root: Path, registry: dict, checkers: dict[str, Checker]
) -> dict[str, list[str]]:
    """{repo-relative artifact path: sorted finding ids}; kinds/instances with
    no findings contribute no entry (sparse, like skill_inventory_baseline)."""
    result: dict[str, list[str]] = {}
    for kind_name, spec in sorted(registry.get("artifacts", {}).items()):
        checker = checkers[spec["checker"]]
        for path in discover_instances(repo_root, kind_name, spec):
            findings = checker(repo_root, path, spec, registry)
            if findings:
                rel = repo_relative(repo_root, path)
                result[rel] = sorted(set(result.get(rel, [])) | set(findings))
    return result


def load_baseline(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(data, dict):
        return {}
    result: dict[str, list[str]] = {}
    for name, ids in data.items():
        if isinstance(name, str) and isinstance(ids, list):
            result[name] = [i for i in ids if isinstance(i, str)]
    return result


def write_baseline(path: Path, findings: dict[str, list[str]]) -> None:
    payload = {name: sorted(ids) for name, ids in sorted(findings.items())}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def ratchet(
    current: dict[str, list[str]], baseline: dict[str, list[str]]
) -> dict[str, list[str]]:
    """Compare `current` findings against the committed `baseline` by exact
    membership. A current id absent from its path's baseline entry is a
    `new_findings` entry (an error); a baseline id no longer produced for
    that path is a `stale_baseline` entry (informational; shrinkage is the
    goal)."""
    new_findings: list[str] = []
    for path in sorted(current):
        baselined = set(baseline.get(path, []))
        for finding_id in current[path]:
            if finding_id not in baselined:
                new_findings.append(f"{path}: {finding_id}")

    stale_baseline: list[str] = []
    for path in sorted(baseline):
        current_ids = set(current.get(path, []))
        for finding_id in baseline[path]:
            if finding_id not in current_ids:
                stale_baseline.append(f"{path}: {finding_id}")

    return {"new_findings": new_findings, "stale_baseline": stale_baseline}


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = repo_root_from_args(args.repo_root)
    registry = load_registry(repo_root)
    checkers = resolve_checkers(registry)
    current = collect_findings(repo_root, registry, checkers)
    baseline_path = repo_root / DEFAULT_BASELINE_RELPATH

    if args.write_baseline:
        write_baseline(baseline_path, current)
        total_ids = sum(len(ids) for ids in current.values())
        print(
            f"artifact-lint: wrote {len(current)} artifact path(s), "
            f"{total_ids} finding id(s) -> {DEFAULT_BASELINE_RELPATH}"
        )
        return 0

    baseline = load_baseline(baseline_path)
    result = ratchet(current, baseline)
    new_findings = result["new_findings"]
    stale_baseline = result["stale_baseline"]

    for line in new_findings:
        print(f"FINDING {line}")
    for line in stale_baseline:
        print(f"stale-baseline: {line}")

    if new_findings:
        print(f"artifact-lint: {len(new_findings)} new finding(s)")
    else:
        baselined_count = sum(len(ids) for ids in baseline.values())
        print(f"artifact-lint: pass ({baselined_count} baselined)")

    return 1 if new_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
