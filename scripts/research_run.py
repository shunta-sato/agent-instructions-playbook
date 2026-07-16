#!/usr/bin/env python3
"""Research OS runner — the only writer of research records. Appends
preregister/exploration/result/claim records to the shared JSONL ledger;
every timestamp, id, digest, predicate, outcome, and ``n`` is computed here or
in ``research_ledger`` (never from the caller) so the gate re-derives them.
Subcommands: register, execute, explore, claim, render-claims. Stdlib only."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

try:  # direct execution: scripts/ is on sys.path[0]
    import research_ledger as rl
except ModuleNotFoundError:  # imported as scripts.research_run (tests, -m)
    from scripts import research_ledger as rl

def repo_root_from_args(explicit: str) -> Path:
    if explicit:
        return Path(explicit).resolve()
    return Path(__file__).resolve().parent.parent

def ledger_path_from_args(repo_root: Path, explicit: str) -> Path:
    if explicit:
        path = Path(explicit)
        return path.resolve() if path.is_absolute() else (repo_root / path).resolve()
    return (repo_root / rl.LEDGER_REL).resolve()

def parse_number(text: str) -> float | int:
    try:
        return int(text)
    except ValueError:
        return float(text)

def make_run_dir(repo_root: Path, identifier: str) -> tuple[Path, str]:
    """Create an empty run directory; return (absolute path, repo-relative)."""
    from datetime import datetime, timezone

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    rel = f"research/runs/{identifier}/{stamp}"
    absolute = repo_root / rel
    absolute.mkdir(parents=True, exist_ok=True)
    return absolute, rel

def run_command(command: str, repo_root: Path, run_dir: Path, use_argv: bool = False) -> int:
    """Execute the registered/explored command. B(c): the ``shlex.split`` + ``shell=False`` argv path
    is used ONLY when ``use_argv`` (an axis-bearing execute, where the parsed argv the axis binds to
    must BE the process argv); axis-less register/execute and explore always use the shell path, so
    env-var prefixes, globs, and shell builtins (``cd``) keep working."""
    env = dict(os.environ)
    env["RESEARCH_RUN_DIR"] = str(run_dir)
    if use_argv:
        completed = subprocess.run(shlex.split(command), shell=False, cwd=str(repo_root), env=env)
    else:
        completed = subprocess.run(command, shell=True, cwd=str(repo_root), env=env)
    return completed.returncode

def read_metrics(run_dir: Path) -> Any:
    result_file = run_dir / "result.json"
    if not result_file.is_file():
        return None
    payload = json.loads(result_file.read_text(encoding="utf-8"))
    if payload is not None and not isinstance(payload, dict):
        raise ValueError("result.json must contain a JSON object or null")
    return payload

# --- working-tree fingerprinting (runner-only; the gate re-derives outcomes,
# never the working-tree digest, so these live with their sole caller) --------

def _git(repo_root: Path, args: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *args], check=True, capture_output=True, text=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return completed.stdout

def git_head(repo_root: Path) -> str:
    out = _git(repo_root, ["rev-parse", "HEAD"])
    return out.strip() if out else "no-git"

def _excluded_from_digest(rel_path: str, ledger_rel: str | None) -> bool:
    """A dirty path that is the recorder's own output, not an experiment input:
    the ledger being written (incl. default ``LEDGER_REL`` that ``register``
    appends to) and runner artifacts under ``RUNNER_OUTPUT_REL``."""
    if rel_path == rl.LEDGER_REL or rel_path == ledger_rel:
        return True
    return rel_path == rl.RUNNER_OUTPUT_REL or rel_path.startswith(rl.RUNNER_OUTPUT_REL + "/")

def dirty_input_files(repo_root: Path, ledger_path: Path | None = None) -> list[dict[str, str]]:
    """Dirty ``command_digest`` inputs: tracked files modified vs ``HEAD`` plus
    untracked, non-ignored files — the untracked set is load-bearing, since a
    probe run WITHOUT ``git add`` would otherwise be editable between calls."""
    tracked = _git(repo_root, ["diff", "--name-only", "HEAD", "--"]) or ""
    untracked = _git(repo_root, ["ls-files", "--others", "--exclude-standard"]) or ""
    ledger_rel: str | None = None
    if ledger_path is not None:
        try:
            ledger_rel = ledger_path.resolve().relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            ledger_rel = None
    names = {ln.strip() for ln in tracked.splitlines() if ln.strip()}
    names |= {ln.strip() for ln in untracked.splitlines() if ln.strip()}
    entries: list[dict[str, str]] = []
    for name in sorted(names):
        if _excluded_from_digest(name, ledger_rel):
            continue
        path = repo_root / name
        if path.is_file():
            entries.append({"path": name, "sha256": rl.sha256_file(path)})
    return entries

# --- subcommands -------------------------------------------------------------

# B(b): a shell/interpreter invoked with an inline script consumes later argv as its own
# ($0/-c script), not the wrapped program's argv, so a token bound there is not a real knob.
_SHELL_WRAPPERS = {"sh", "bash", "zsh", "dash", "ksh"}
_SCRIPT_WRAPPERS = {"python", "python3", "perl", "ruby"}

def _wrapper_denies_axis(tokens: list[str]) -> bool:
    if not tokens:
        return False
    name = Path(tokens[0]).name
    flags = {"-c"} if name in _SHELL_WRAPPERS else {"-c", "-e"} if name in _SCRIPT_WRAPPERS else set()
    return bool(flags) and any(tok in flags for tok in tokens[1:])

def _bound_after_terminator(tokens: list[str], positions: list[int]) -> bool:
    """The only key-bound occurrence(s) sit after a bare ``--`` terminator (positional, not the option)."""
    return "--" in tokens and bool(positions) and all(p > tokens.index("--") for p in positions)

def validate_variation_axis(axis: str, command: str) -> list[str]:
    """F3/R3/B(b): a declared axis must be ``key=value`` (non-empty parts) whose value is BOUND to
    option ``key`` in the command's real argv — not a shell/interpreter wrapper's own -c/-e args and
    not stranded after a bare ``--`` terminator — so ``n`` is a mechanically checkable knob."""
    parsed = rl._axis_key_value(axis)
    if parsed is None:
        return ["variation_axis must be key=value with non-empty key and value"]
    key, value = parsed
    if not rl.command_is_simple(command):  # B2: no flat-argv binding over a shell pipeline
        return ["axis-bearing experiments require a simple command (no shell metacharacters); "
                "register without an axis or split the command"]
    tokens = rl._tokenize(command)
    if _wrapper_denies_axis(tokens):
        return [f"variation_axis cannot bind through wrapper {tokens[0]!r} (-c/-e consumes argv); "
                "run the probe directly instead of via a shell/interpreter wrapper"]
    positions = rl._bound_value_positions(tokens, key, value)
    if not positions:
        return [f"variation_axis value {value!r} must be bound to option {key!r} in the command"]
    if _bound_after_terminator(tokens, positions):
        return [f"variation_axis value {value!r} is bound to {key!r} only after a bare '--' "
                "terminator; run the probe directly instead of passing it through '--'"]
    return []

def build_disconfirm(args: argparse.Namespace) -> dict[str, Any]:
    """The runner constructs the disconfirm predicate — threshold (comparator +
    threshold) or the structured equivalence bounds (R2b) — so a claim's
    predicate shape is derived from flags, never asserted free-text."""
    if args.equivalence_bounds is not None:
        if args.comparator or args.threshold is not None:
            raise ValueError("--equivalence-bounds cannot be combined with --comparator/--threshold")
        lower, upper = args.equivalence_bounds
        return {"type": rl.PREDICATE_EQUIVALENCE, "metric": args.metric,
                "lower": parse_number(lower), "upper": parse_number(upper)}
    if not args.comparator or args.threshold is None:
        raise ValueError("register requires either --comparator with --threshold, or --equivalence-bounds LOWER UPPER")
    return {"type": rl.PREDICATE_THRESHOLD, "metric": args.metric,
            "comparator": args.comparator, "threshold": parse_number(args.threshold)}

def cmd_register(args: argparse.Namespace, repo_root: Path, ledger_path: Path) -> int:
    disconfirm = build_disconfirm(args)
    errors = rl.validate_predicate(disconfirm)
    if args.variation_axis:
        errors += validate_variation_axis(args.variation_axis, args.command)
    if errors:
        raise ValueError("; ".join(errors))

    head = git_head(repo_root)
    dirty = dirty_input_files(repo_root, ledger_path)
    records = rl.load_research_records(ledger_path)
    experiment_id = rl.next_counter(records, rl.PREREGISTER, "E")
    record: dict[str, Any] = {
        "schema_version": rl.SCHEMA_VERSION,
        "record_type": rl.PREREGISTER,
        "experiment_id": experiment_id,
        "registered_at": rl.stamp_utc(),
        "mode": "research",
        "hypothesis": args.hypothesis,
        "disconfirm": disconfirm,
        "command": args.command,
        "command_digest": rl.command_digest(head, dirty, args.command),
        "git_head": head,
        "dirty_files": dirty,
    }
    if args.variation_axis:
        record["variation_axis"] = args.variation_axis
    rl.chain_and_append(ledger_path, record)
    print(experiment_id)
    return 0

def cmd_execute(args: argparse.Namespace, repo_root: Path, ledger_path: Path) -> int:
    records = rl.load_research_records(ledger_path)
    prereg = rl.find_preregister(records, args.experiment_id)
    if prereg is None:
        raise ValueError(
            f"no registration for {args.experiment_id}; unregistered execution must use 'explore'"
        )

    command = prereg["command"]
    head = git_head(repo_root)
    dirty = dirty_input_files(repo_root, ledger_path)
    digest = rl.command_digest(head, dirty, command)
    if digest != prereg["command_digest"]:
        raise ValueError(
            f"command_digest for {args.experiment_id} changed since registration; "
            "register a revision instead of executing"
        )

    run_dir_abs, run_dir_rel = make_run_dir(repo_root, args.experiment_id)
    started_at = rl.stamp_utc()
    axis = rl._axis_key_value(prereg.get("variation_axis"))
    use_argv = axis is not None and rl.command_is_simple(command)  # B(c): only axis-bearing executes
    exit_code = run_command(command, repo_root, run_dir_abs, use_argv=use_argv)
    finished_at = rl.stamp_utc()
    metrics = read_metrics(run_dir_abs)
    outcome = rl.final_outcome(prereg, metrics)  # B4 parity: axis_effective override shared with the checker
    mult = rl.multiplicity(records, digest)

    record = {
        "schema_version": rl.SCHEMA_VERSION,
        "record_type": rl.RESULT,
        "experiment_id": args.experiment_id,
        "started_at": started_at,
        "finished_at": finished_at,
        "command_digest": digest,
        "exit_code": exit_code,
        "metrics": metrics,
        "outcome": outcome,
        "run_dir": run_dir_rel,
        "exploration_multiplicity": mult,
        "derived_from_exploration": mult > 0,
    }
    rl.chain_and_append(ledger_path, record)
    print(f"{args.experiment_id} {outcome} {run_dir_rel}")
    return 0

def cmd_explore(args: argparse.Namespace, repo_root: Path, ledger_path: Path) -> int:
    head = git_head(repo_root)
    dirty = dirty_input_files(repo_root, ledger_path)
    digest = rl.command_digest(head, dirty, args.command)
    records = rl.load_research_records(ledger_path)
    exploration_id = rl.next_counter(records, rl.EXPLORATION, "X")

    run_dir_abs, run_dir_rel = make_run_dir(repo_root, exploration_id)
    executed_at = rl.stamp_utc()
    exit_code = run_command(args.command, repo_root, run_dir_abs)
    metrics = read_metrics(run_dir_abs)

    record = {
        "schema_version": rl.SCHEMA_VERSION,
        "record_type": rl.EXPLORATION,
        "exploration_id": exploration_id,
        "executed_at": executed_at,
        "command": args.command,
        "command_digest": digest,
        "exit_code": exit_code,
        "metrics": metrics,
        "run_dir": run_dir_rel,
    }
    rl.chain_and_append(ledger_path, record)
    print(f"{exploration_id} {run_dir_rel}")
    return 0

def cmd_claim(args: argparse.Namespace, repo_root: Path, ledger_path: Path) -> int:
    records = rl.load_research_records(ledger_path)
    for eid in args.evidence:
        prereg = rl.find_preregister(records, eid)
        result = rl.find_result(records, eid)
        if prereg is None or result is None:
            raise ValueError(f"evidence {eid} has no completed experiment result")
        if not (prereg["registered_at"] < result["started_at"]):
            raise ValueError(f"evidence {eid}: registered_at is not before started_at")

    # Semantic binding (S3): metric/evidence consistency, with outcome_basis
    # persisted so the gate re-derives it from the ledger. B1: the claim's
    # category is machine-derived below, never a caller-supplied direction.
    binding_errors, outcome_basis = rl.evaluate_claim_binding(records, args.metric, args.evidence)
    binding_errors += rl.predicate_identity_errors(records, args.evidence)  # S5
    if binding_errors:
        raise ValueError("; ".join(binding_errors))

    n, n_basis = rl.claim_n_and_note(records, args.evidence)
    claim_id = rl.next_counter(records, rl.CLAIM, "C")
    record = {
        # S6: no caller-supplied "configurations" free text — the rendered view derives
        # configuration identity from evidence (rl.claim_configuration_labels).
        "schema_version": rl.SCHEMA_VERSION,
        "record_type": rl.CLAIM,
        "claim_id": claim_id,
        "created_at": rl.stamp_utc(),
        "metric": args.metric,
        "evidence": args.evidence,
        "outcome_basis": outcome_basis,
        "derived_category": rl.derive_claim_category(records, args.evidence),
        "n_basis": n_basis,
        "sources": args.source or [],
        "n": n,
    }
    rl.chain_and_append(ledger_path, record)
    print(claim_id)
    return 0

def cmd_render_claims(args: argparse.Namespace, repo_root: Path, ledger_path: Path) -> int:
    records = rl.load_research_records(ledger_path)
    content = rl.render_claims(records)
    if args.output:
        output = Path(args.output)
        if not output.is_absolute():
            output = repo_root / output
    else:
        # Default output tracks the ledger, mirroring the gate's freshness
        # check: research/claims.md for the canonical ledger, an adjacent
        # claims.md for any other --ledger.
        output = rl.claims_view_path(repo_root, ledger_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(output.as_posix())
    return 0

# --- CLI ---------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Research OS runner.")
    parser.add_argument("--repo-root", default="", help="Repository root override.")
    parser.add_argument("--ledger", default="", help="Ledger path override.")
    sub = parser.add_subparsers(dest="command", required=True)

    register = sub.add_parser("register", help="Preregister an experiment.")
    register.add_argument("--hypothesis", required=True)
    register.add_argument("--metric", required=True)
    # A threshold predicate (--comparator + --threshold) OR the structured
    # equivalence predicate (--equivalence-bounds LOWER UPPER, R2b); exactly one.
    register.add_argument("--comparator", choices=rl.COMPARATORS, default="")
    register.add_argument("--threshold", default=None)
    register.add_argument("--equivalence-bounds", nargs=2, metavar=("LOWER", "UPPER"), default=None,
                          help="Equivalence bounds: disconfirmed OUTSIDE [LOWER, UPPER]; "
                          "supported = within bounds (B1: claim category 'within-bounds').")
    register.add_argument("--command", required=True)
    register.add_argument("--variation-axis", default="")
    register.set_defaults(func=cmd_register)

    execute = sub.add_parser("execute", help="Execute a registered experiment.")
    execute.add_argument("--experiment-id", required=True)
    execute.set_defaults(func=cmd_execute)

    explore = sub.add_parser("explore", help="Run an unregistered probe.")
    explore.add_argument("--command", required=True)
    explore.set_defaults(func=cmd_explore)

    claim = sub.add_parser("claim", help="Record a research claim.")
    # R2a/B1/S6: a claim carries no free-text effect, no caller-supplied direction, and no
    # caller-supplied configuration text; its sentence + configuration identity are rendered
    # purely from structured fields (metric/derived-category/n/axis-key/axis-values).
    claim.add_argument("--metric", required=True)
    claim.add_argument("--evidence", action="append", required=True, default=[])
    claim.add_argument("--source", action="append", default=[])
    claim.set_defaults(func=cmd_claim)

    render = sub.add_parser("render-claims", help="Render the claims view.")
    render.add_argument(
        "--output",
        default="",
        help="Output path; default tracks the ledger (research/claims.md for "
        "the canonical ledger, an adjacent claims.md otherwise).",
    )
    render.set_defaults(func=cmd_render_claims)
    return parser

def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = repo_root_from_args(args.repo_root)
    ledger_path = ledger_path_from_args(repo_root, args.ledger)
    try:
        return args.func(args, repo_root, ledger_path)
    except (ValueError, rl.LedgerError) as exc:
        print(f"research-run: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
