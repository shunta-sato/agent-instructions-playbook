#!/usr/bin/env python3
"""Runner-agnostic behavior-eval harness: build, grade, report.

Routing evals (``run_routing_eval.py``) measure skill SELECTION. This
harness measures skill EXECUTION BEHAVIOR: it turns
``evals/skill-behavior/*.json`` grader-shaped cases (``prompt``, ``given``,
``expected_decision``, ``expected_findings``, ``expected_output_contains``)
into one self-contained prompt pack per case, any runner can answer, then
grades the raw plain-text answers mechanically. Never calls a model itself.
Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path

try:
    from scripts.run_routing_eval import git_commit
    from scripts.update_skill_requires import parse_tier_lists, split_frontmatter
except ImportError:  # pragma: no cover - direct execution puts scripts/ on sys.path
    from run_routing_eval import git_commit
    from update_skill_requires import parse_tier_lists, split_frontmatter

EVALS_DIR = "evals/skill-behavior"
SKILLS_DIR = ".agents/skills"

# A skill's Output expectation may document a fixed decision-line prefix,
# e.g. quality-gate's "Start with: `Gate decision: submit` or ...". When a
# skill documents no such line (e.g. unit-test-design), grading falls back
# to the response's first line.
DECISION_MARKER_RE = re.compile(r"Start with:\s*`([^`\n]+)`")


# ---- pack building (build) -------------------------------------------

def iter_case_files(repo_root: Path) -> list[Path]:
    return sorted((repo_root / EVALS_DIR).glob("*.json"))


def extract_decision_marker(skill_text: str) -> str | None:
    match = DECISION_MARKER_RE.search(skill_text)
    if not match:
        return None
    prefix = match.group(1).split(":", 1)[0]
    return f"{prefix}:"


NUMBERED_ITEM_RE = re.compile(r"^\d+\)\s")


def resource_condition(body_text: str, resource_path: str) -> str:
    """The load condition SKILL.md's body states for one resource, as one
    joined line. Searches the body only (never the frontmatter), so the
    resource's own `metadata.resources:` list entry is never mistaken for its
    condition. "How to use" steps wrap their condition sentence across
    several indented lines under a numbered item (``0) Open X. Open Y only
    when ...``); this joins the whole numbered item, not just the physical
    line the path happens to sit on."""
    lines = body_text.splitlines()
    item_starts = [i for i, l in enumerate(lines) if NUMBERED_ITEM_RE.match(l)]
    for i, line in enumerate(lines):
        if resource_path not in line:
            continue
        if not item_starts:
            return line.strip()
        block_start = max((s for s in item_starts if s <= i), default=i)
        block_end = min((s for s in item_starts if s > i), default=i + 1)
        return " ".join(l.strip() for l in lines[block_start:block_end] if l.strip())
    return "condition not stated inline; see the skill's How-to-use section above."


def render_response_instruction(skill_name: str, marker: str | None) -> str:
    lines = [
        "## RESPONSE INSTRUCTION",
        "",
        f'Execute the "{skill_name}" skill on this scenario exactly as its '
        "SKILL.md above specifies, and produce its normal output (see "
        '"Output expectation" above).',
    ]
    if marker:
        lines.append(
            f"Start your response with the documented `{marker}` line, "
            "exactly as SKILL.md specifies, then the rest of the normal output."
        )
    lines += [
        "",
        "Reply with plain text only: this IS the skill's output for this "
        "scenario, not a report about the skill and not JSON.",
    ]
    return "\n".join(lines)


def render_pack(
    skill_name: str,
    skill_text: str,
    requires_texts: list[tuple[str, str]],
    resource_conditions: dict[str, str],
    marker: str | None,
    case: dict,
) -> str:
    parts = [
        "# BEHAVIOR EVAL PACK",
        f"skill: {skill_name}",
        f"case: {case['id']}",
        "",
        f"## {skill_name}/SKILL.md",
        "",
        skill_text,
    ]
    for rel, text in requires_texts:
        parts += ["", f"## {skill_name}/{rel} (required)", "", text]
    if resource_conditions:
        parts += [
            "",
            "## Resources (not included; open only if the stated condition applies)",
            "",
        ]
        parts += [f"- {rel}: {cond}" for rel, cond in resource_conditions.items()]
    parts += ["", "## Scenario", "", case["prompt"], "", "## Given", ""]
    parts += [f"- {fact}" for fact in case["given"]]
    parts += ["", render_response_instruction(skill_name, marker)]
    return "\n".join(parts)


def cmd_build(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    commit = git_commit(repo_root)
    manifest_cases = []
    for eval_file in iter_case_files(repo_root):
        data = json.loads(eval_file.read_text(encoding="utf-8"))
        skill_name = data["skill"]
        skill_dir = repo_root / SKILLS_DIR / skill_name
        skill_md_path = skill_dir / "SKILL.md"
        skill_text = skill_md_path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(skill_text, skill_md_path)
        tiers = parse_tier_lists(frontmatter)
        requires = tiers.get("requires", [])
        resources = tiers.get("resources", [])
        requires_texts = [
            (rel, (skill_dir / rel).read_text(encoding="utf-8")) for rel in requires
        ]
        resource_conditions = {rel: resource_condition(body, rel) for rel in resources}
        marker = extract_decision_marker(skill_text)
        for case in data.get("cases", []):
            pack_text = render_pack(
                skill_name, skill_text, requires_texts, resource_conditions, marker, case
            )
            pack_path = out / f"{case['id']}.md"
            pack_path.write_text(pack_text, encoding="utf-8")
            manifest_cases.append(
                {
                    "id": case["id"],
                    "skill": skill_name,
                    "pack": pack_path.name,
                    "lines": len(pack_text.splitlines()),
                    "chars": len(pack_text),
                }
            )
    manifest = {
        "variant": repo_root.name,
        "commit": commit,
        "case_count": len(manifest_cases),
        "cases": manifest_cases,
    }
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    total_lines = sum(c["lines"] for c in manifest_cases)
    print(f"build: {len(manifest_cases)} pack(s) -> {out} (total {total_lines} lines)")
    return 0


# ---- grading ------------------------------------------------------------

def load_case_index(repo_root: Path) -> dict[str, dict]:
    """Every case from evals/skill-behavior/*.json, keyed by id, skill attached."""
    index: dict[str, dict] = {}
    for eval_file in iter_case_files(repo_root):
        data = json.loads(eval_file.read_text(encoding="utf-8"))
        skill = data.get("skill")
        for case in data.get("cases", []):
            entry = dict(case)
            entry["skill"] = skill
            index[case["id"]] = entry
    return index


def grade_decision(response_text: str, expected_decision: str, marker: str | None) -> bool:
    if marker:
        for line in response_text.splitlines():
            stripped = line.strip()
            if stripped.startswith(marker):
                return stripped[len(marker):].strip() == expected_decision
        return False
    first_line = next((l.strip() for l in response_text.splitlines() if l.strip()), "")
    return expected_decision in first_line


def grade_output_contains(response_text: str, expected: list[str]) -> dict:
    missing = [s for s in expected if s not in response_text]
    return {"total": len(expected), "matched": len(expected) - len(missing), "missing": missing}


def grade_findings(response_text: str, expected_findings: list[str]) -> dict:
    matched = [f for f in expected_findings if f in response_text]
    return {"total": len(expected_findings), "matched": len(matched)}


def grade_case_record(case: dict, response_text: str, marker: str | None) -> dict:
    return {
        "id": case["id"],
        "skill": case.get("skill"),
        "decision_match": (
            grade_decision(response_text, case["expected_decision"], marker)
            if case.get("expected_decision")
            else None
        ),
        "output_contains": grade_output_contains(
            response_text, case.get("expected_output_contains", [])
        ),
        "findings": grade_findings(response_text, case.get("expected_findings", [])),
    }


def _rate(matched: int, total: int) -> float:
    return round(matched / total, 4) if total else 1.0


def aggregate_results(records: list[dict], ungraded: list[dict], manifest: dict) -> dict:
    decision_records = [r for r in records if r["decision_match"] is not None]
    decided = sum(1 for r in decision_records if r["decision_match"])
    output_matched = sum(r["output_contains"]["matched"] for r in records)
    output_total = sum(r["output_contains"]["total"] for r in records)
    findings_ratios = [
        r["findings"]["matched"] / r["findings"]["total"]
        for r in records
        if r["findings"]["total"] > 0
    ]
    return {
        "variant": manifest.get("variant"),
        "commit": manifest.get("commit"),
        "cases_total": len(manifest.get("cases", [])),
        "cases_graded": len(records),
        "ungraded": ungraded,
        "decision_accuracy": _rate(decided, len(decision_records)),
        "output_contains_rate": _rate(output_matched, output_total),
        "findings_ratio_mean": round(statistics.fmean(findings_ratios), 4)
        if findings_ratios
        else 1.0,
        "cases": records,
    }


def cmd_grade(args: argparse.Namespace) -> int:
    packs_dir = Path(args.packs)
    responses_dir = Path(args.responses)
    manifest = json.loads((packs_dir / "manifest.json").read_text(encoding="utf-8"))
    repo_root = Path(args.repo_root).resolve()
    corpus = load_case_index(repo_root)
    marker_cache: dict[str, str | None] = {}
    records: list[dict] = []
    ungraded: list[dict] = []
    for entry in manifest.get("cases", []):
        cid, skill = entry["id"], entry["skill"]
        resp_path = responses_dir / f"{cid}.txt"
        if not resp_path.is_file():
            ungraded.append({"id": cid, "reason": "response_missing"})
            continue
        response_text = resp_path.read_text(encoding="utf-8")
        if not response_text.strip():
            ungraded.append({"id": cid, "reason": "response_empty"})
            continue
        case = corpus.get(cid)
        if case is None:
            ungraded.append({"id": cid, "reason": "case_missing_from_corpus"})
            continue
        if skill not in marker_cache:
            skill_md = repo_root / SKILLS_DIR / skill / "SKILL.md"
            marker_cache[skill] = (
                extract_decision_marker(skill_md.read_text(encoding="utf-8"))
                if skill_md.is_file()
                else None
            )
        records.append(grade_case_record(case, response_text, marker_cache[skill]))
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
        ("Decision accuracy", [_fmt_pct(g.get("decision_accuracy", 0.0)) for g in graded]),
        ("Output-contains rate", [_fmt_pct(g.get("output_contains_rate", 0.0)) for g in graded]),
        ("Findings ratio (mean)", [_fmt_pct(g.get("findings_ratio_mean", 0.0)) for g in graded]),
    ]
    out = [
        "| Metric | " + " | ".join(variants) + " |",
        "| --- | " + " | ".join(["---"] * len(variants)) + " |",
    ]
    out += [f"| {name} | " + " | ".join(values) + " |" for name, values in rows]
    return out


def _case_badness(record: dict) -> int:
    badness = 0 if record["decision_match"] else 1
    badness += len(record["output_contains"].get("missing", []))
    return badness


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
        oc, fnd = r["output_contains"], r["findings"]
        parts = [
            f"decision={'ok' if r['decision_match'] else 'mismatch'}",
            f"output_contains={oc['matched']}/{oc['total']}",
        ]
        if oc.get("missing"):
            parts.append(f"missing={oc['missing']}")
        if fnd["total"]:
            parts.append(f"findings={fnd['matched']}/{fnd['total']}")
        lines.append(f"- {cid}: " + "; ".join(parts))
    return lines


def cmd_report(args: argparse.Namespace) -> int:
    graded = [json.loads(Path(p).read_text(encoding="utf-8")) for p in args.graded]
    lines = ["# Behavior Eval Report", ""] + _summary_table(graded)
    for g in graded:
        lines += _worst_cases_section(g)
    print("\n".join(lines))
    return 0


# ---- CLI ------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Behavior-eval harness: build / grade / report.")
    sub = parser.add_subparsers(dest="command", required=True)
    build_p = sub.add_parser("build", help="Build one self-contained pack per case.")
    build_p.add_argument("--repo-root", required=True)
    build_p.add_argument("--out", required=True)
    grade_p = sub.add_parser("grade", help="Grade raw plain-text responses against the corpus.")
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
