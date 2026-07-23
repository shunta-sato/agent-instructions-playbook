#!/usr/bin/env python3
"""Runner-agnostic routing-eval harness: build, grade, report.

Turns the static trigger-eval corpus (evals/skill-triggers/*.json) into a
model-executable routing measurement. Never calls a model itself: it builds
self-contained prompt packs any runner (Claude Code subagent, Codex CLI, API
script) can answer, then grades the raw JSON answers mechanically. See
``--help`` per subcommand and ``evals/routing-runs/README.md`` for the full
build/run/grade/report protocol. Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path

try:
    from scripts.update_skill_requires import parse_tier_lists, split_frontmatter
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from update_skill_requires import parse_tier_lists, split_frontmatter

DEFAULT_BATCH_SIZE = 18
REQUIRES_MANY_THRESHOLD = 2  # mirrors check_context_budget.REQUIRES_MAX_ENTRIES
CORE_SKILLS = ("dev-workflow", "quality-gate")
SKILLS_DIR = ".agents/skills"
EVALS_DIR = "evals/skill-triggers"
HIDDEN_VISIBILITY = ("explicit-only", "template")

RESPONSE_INSTRUCTION = (
    "## RESPONSE INSTRUCTION\n\n"
    "For each case above, decide - as the repository bootstrap above directs - "
    "which skills you would load before or while executing it. Report the "
    "final co-fire set (every skill you would load), not just the first "
    "router skill.\n\n"
    "Reply with ONLY a JSON array in this exact shape, no prose, no markdown "
    "fences:\n\n"
    '[{"id": "<case id>", "skills": ["skill-a", "skill-b"]}, ...]\n'
)

# ---- discovery surface (build) --------------------------------------------

def parse_skill_meta(frontmatter: list[str]) -> dict[str, str]:
    """Extract top-level ``name``/``description`` and ``metadata.visibility``."""
    meta: dict[str, str] = {}
    for line in frontmatter:
        if line.startswith("name:"):
            meta["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("description:"):
            meta["description"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("  ") and line.strip().startswith("visibility:"):
            meta["visibility"] = line.split(":", 1)[1].strip()
    return meta


def discover_skills(repo_root: Path) -> list[dict]:
    """Every skill's name/description/visibility, sorted by name."""
    skills = []
    for skill_md in sorted((repo_root / SKILLS_DIR).glob("*/SKILL.md")):
        text = skill_md.read_text(encoding="utf-8")
        frontmatter, _body = split_frontmatter(text, skill_md)
        meta = parse_skill_meta(frontmatter)
        name = meta.get("name", skill_md.parent.name)
        skills.append({"name": name, "description": meta.get("description", ""), "visibility": meta.get("visibility")})
    return sorted(skills, key=lambda s: s["name"])


def render_available_skills(skills: list[dict]) -> str:
    visible = [s for s in skills if s["visibility"] not in HIDDEN_VISIBILITY]
    hidden = [s for s in skills if s["visibility"] in HIDDEN_VISIBILITY]
    lines = ["## Available skills", ""]
    lines += [f"- {s['name']}: {s['description']}" for s in visible]
    if hidden:
        lines += ["", "### explicit-only (name only)", ""]
        lines += [f"- {s['name']}" for s in hidden]
    return "\n".join(lines)


def _core_requires(skill_dir: Path, frontmatter: list[str]) -> list[str]:
    # Unmigrated (pre four-tier) skills regenerate `requires` from every file
    # under references/templates/scripts, which can balloon past a couple of
    # entries. Fall back to the skill's own references/<name>.md then.
    requires = parse_tier_lists(frontmatter).get("requires", [])
    if len(requires) > REQUIRES_MANY_THRESHOLD:
        fallback = f"references/{skill_dir.name}.md"
        if (skill_dir / fallback).is_file():
            return [fallback]
    return requires


def core_router_section(repo_root: Path) -> str:
    parts = []
    for name in CORE_SKILLS:
        skill_dir = repo_root / SKILLS_DIR / name
        skill_md = skill_dir / "SKILL.md"
        text = skill_md.read_text(encoding="utf-8")
        parts.append(f"## {name}/SKILL.md\n\n{text}")
        frontmatter, _body = split_frontmatter(text, skill_md)
        for rel in _core_requires(skill_dir, frontmatter):
            req_path = skill_dir / rel
            if req_path.is_file():
                parts.append(f"## {name}/{rel}\n\n{req_path.read_text(encoding='utf-8')}")
    return "\n\n".join(parts)


def build_discovery_surface(repo_root: Path) -> str:
    agents_md = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    skills = discover_skills(repo_root)
    return "\n\n".join(
        [
            "# DISCOVERY SURFACE",
            "## AGENTS.md\n\n" + agents_md,
            render_available_skills(skills),
            "## Core router files",
            core_router_section(repo_root),
        ]
    )


def git_commit(repo_root: Path) -> str:
    cmd = ["git", "-C", str(repo_root), "rev-parse", "HEAD"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return "unknown"


def load_cases(repo_root: Path) -> list[dict]:
    """Every case from evals/skill-triggers/*.json, in deterministic file order."""
    cases: list[dict] = []
    for eval_file in sorted((repo_root / EVALS_DIR).glob("*.json")):
        data = json.loads(eval_file.read_text(encoding="utf-8"))
        cases.extend(data.get("cases", []))
    return cases


def make_batches(cases: list[dict], batch_size: int) -> list[list[dict]]:
    return [cases[i : i + batch_size] for i in range(0, len(cases), batch_size)]


def render_batch(surface: str, label: str, batch_cases: list[dict]) -> str:
    lines = [surface, "", f"## {label} cases ({len(batch_cases)})", ""]
    for case in batch_cases:
        lines += [f"### case: {case['id']}", "", case["prompt"], ""]
    lines.append(RESPONSE_INSTRUCTION)
    return "\n".join(lines)


def cmd_build(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    surface = build_discovery_surface(repo_root)
    cases = load_cases(repo_root)
    groups = make_batches(cases, args.batch_size)
    case_map = []
    for i, group in enumerate(groups, start=1):
        label = f"batch-{i:02d}"
        (out / f"{label}.md").write_text(render_batch(surface, label, group), encoding="utf-8")
        case_map += [{"id": c["id"], "batch": label} for c in group]
    manifest = {
        "variant": repo_root.name,
        "commit": git_commit(repo_root),
        "batch_size": args.batch_size,
        "case_count": len(cases),
        "batch_count": len(groups),
        "discovery_surface": {"lines": len(surface.splitlines()), "chars": len(surface)},
        "cases": case_map,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    surf = manifest["discovery_surface"]
    print(
        f"build: {len(groups)} batch(es), {len(cases)} case(s), "
        f"surface {surf['lines']} lines / {surf['chars']} chars -> {out}"
    )
    return 0


# ---- grading ----------------------------------------------------------

def _load_response_batch(responses_dir: Path, batch: str) -> tuple[dict | None, str]:
    path = responses_dir / f"{batch}.json"
    if not path.is_file():
        return None, "batch_missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None, "batch_corrupt"
    if not isinstance(data, list):
        return None, "batch_corrupt"
    mapping = {
        item["id"]: item.get("skills", [])
        for item in data
        if isinstance(item, dict) and "id" in item
    }
    return mapping, ""


def grade_case(case: dict, selected: object, valid_skills: set[str]) -> dict:
    selected_list = list(selected) if isinstance(selected, list) else []
    should_trigger = case.get("should_trigger", [])
    should_not = case.get("should_not_trigger", [])
    return {
        "id": case.get("id"),
        "selected": selected_list,
        "misses": [s for s in should_trigger if s not in selected_list],
        "violations": [s for s in should_not if s in selected_list],
        "unknown": [s for s in selected_list if s not in valid_skills],
        "co_fire_count": len(selected_list),
        "trigger_total": len(should_trigger),
        "not_trigger_total": len(should_not),
    }


def _rate(matched: int, total: int) -> float:
    return round(matched / total, 4) if total else 1.0


def _percentile(values: list[int], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    k = (len(ordered) - 1) * (pct / 100)
    lo, hi = int(k), min(int(k) + 1, len(ordered) - 1)
    if lo == hi:
        return float(ordered[lo])
    return round(ordered[lo] + (ordered[hi] - ordered[lo]) * (k - lo), 3)


def aggregate_results(records: list[dict], ungraded: list[dict], manifest: dict) -> dict:
    trigger_total = sum(r["trigger_total"] for r in records)
    trigger_miss = sum(len(r["misses"]) for r in records)
    not_total = sum(r["not_trigger_total"] for r in records)
    not_violations = sum(len(r["violations"]) for r in records)
    co_fires = [r["co_fire_count"] for r in records]
    confusion: dict[str, int] = {}
    unknown_counts: dict[str, int] = {}
    for r in records:
        for s in r["violations"]:
            confusion[s] = confusion.get(s, 0) + 1
        for s in r["unknown"]:
            unknown_counts[s] = unknown_counts.get(s, 0) + 1
    return {
        "variant": manifest.get("variant"),
        "commit": manifest.get("commit"),
        "surface": manifest.get("discovery_surface"),
        "cases_total": len(manifest.get("cases", [])),
        "cases_graded": len(records),
        "ungraded": ungraded,
        "recall": _rate(trigger_total - trigger_miss, trigger_total),
        "compliance": _rate(not_total - not_violations, not_total),
        "co_fire_mean": round(statistics.fmean(co_fires), 3) if co_fires else 0.0,
        "co_fire_p90": _percentile(co_fires, 90),
        "confusion": confusion,
        "unknown_skills": unknown_counts,
        "cases": records,
    }


def cmd_grade(args: argparse.Namespace) -> int:
    packs_dir = Path(args.packs)
    responses_dir = Path(args.responses)
    manifest = json.loads((packs_dir / "manifest.json").read_text(encoding="utf-8"))
    repo_root = Path(args.repo_root).resolve()
    corpus = {c["id"]: c for c in load_cases(repo_root)}
    valid_skills = {s["name"] for s in discover_skills(repo_root)}
    batch_cache: dict[str, tuple[dict | None, str]] = {}
    records: list[dict] = []
    ungraded: list[dict] = []
    for entry in manifest.get("cases", []):
        cid, batch = entry["id"], entry["batch"]
        if batch not in batch_cache:
            batch_cache[batch] = _load_response_batch(responses_dir, batch)
        mapping, reason = batch_cache[batch]
        if mapping is None:
            ungraded.append({"id": cid, "batch": batch, "reason": reason})
            continue
        if cid not in mapping:
            ungraded.append({"id": cid, "batch": batch, "reason": "case_missing_from_response"})
            continue
        case = corpus.get(cid, {"id": cid})
        records.append(grade_case(case, mapping[cid], valid_skills))
    aggregate = aggregate_results(records, ungraded, manifest)
    Path(args.out).write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"grade: {len(records)}/{len(manifest.get('cases', []))} case(s) graded -> {args.out}")
    return 0


# ---- report -------------------------------------------------------------

def _fmt_pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _summary_table(graded: list[dict]) -> list[str]:
    variants = [str(g.get("variant", "?")) for g in graded]
    rows = [
        ("Commit", [str(g.get("commit", "?")) for g in graded]),
        ("Cases graded", [f"{g.get('cases_graded', 0)}/{g.get('cases_total', 0)}" for g in graded]),
        ("Should-trigger recall", [_fmt_pct(g.get("recall", 0.0)) for g in graded]),
        ("Should-not-trigger compliance", [_fmt_pct(g.get("compliance", 0.0)) for g in graded]),
        ("Mean co-fire", [str(g.get("co_fire_mean", 0)) for g in graded]),
        ("p90 co-fire", [str(g.get("co_fire_p90", 0)) for g in graded]),
        ("Surface lines", [str((g.get("surface") or {}).get("lines", "?")) for g in graded]),
        ("Surface chars", [str((g.get("surface") or {}).get("chars", "?")) for g in graded]),
    ]
    out = [
        "| Metric | " + " | ".join(variants) + " |",
        "| --- | " + " | ".join(["---"] * len(variants)) + " |",
    ]
    out += [f"| {name} | " + " | ".join(values) + " |" for name, values in rows]
    return out


def _case_badness(record: dict) -> int:
    return len(record["misses"]) + len(record["violations"]) + len(record["unknown"])


def _worst_cases_section(g: dict) -> list[str]:
    scored = [(_case_badness(r), r["id"], r) for r in g.get("cases", [])]
    scored += [
        (10**6, u["id"], {"reason": u.get("reason", "ungraded")}) for u in g.get("ungraded", [])
    ]
    scored.sort(key=lambda t: (-t[0], t[1]))
    lines = ["", f"## Worst cases ({g.get('variant', '?')})", ""]
    for _badness, cid, r in scored[:10]:
        if "reason" in r:
            lines.append(f"- {cid}: ungraded ({r['reason']})")
            continue
        parts = []
        if r["misses"]:
            parts.append(f"missed={r['misses']}")
        if r["violations"]:
            parts.append(f"violated={r['violations']}")
        if r["unknown"]:
            parts.append(f"unknown={r['unknown']}")
        lines.append(f"- {cid}: " + ("; ".join(parts) if parts else "ok"))
    return lines


def cmd_report(args: argparse.Namespace) -> int:
    graded = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.graded]
    lines = ["# Routing Eval Report", ""] + _summary_table(graded)
    for g in graded:
        lines += _worst_cases_section(g)
    print("\n".join(lines))
    return 0


# ---- CLI ------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Routing-eval harness: build / grade / report.")
    sub = parser.add_subparsers(dest="command", required=True)
    build_p = sub.add_parser("build", help="Build discovery-surface prompt packs.")
    build_p.add_argument("--repo-root", required=True)
    build_p.add_argument("--out", required=True)
    build_p.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    grade_p = sub.add_parser("grade", help="Grade model responses against the corpus.")
    grade_p.add_argument("--packs", required=True)
    grade_p.add_argument("--responses", required=True)
    grade_p.add_argument("--out", required=True)
    grade_p.add_argument("--repo-root", default=".", help="Checkout to read expectations from.")
    report_p = sub.add_parser("report", help="Render a markdown comparison report.")
    report_p.add_argument("--graded", nargs="+", required=True)
    report_p.add_argument("--format", choices=["md"], default="md")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    commands = {"build": cmd_build, "grade": cmd_grade, "report": cmd_report}
    return commands[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
