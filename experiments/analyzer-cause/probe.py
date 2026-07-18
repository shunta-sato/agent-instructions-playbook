"""Probe: which single change to analyzer.py recovers the most wall-clock
time on the 300k-line app.log fixture?

Disposable research probe code (experiments/ is a research-mode path;
code-quality gates are waived here per research-workflow). Evidence
discipline is not waived: this script is invoked only through
scripts/research_run.py register/execute, which stamps outcome and timing.

Target under study (read-only, never modified):
/private/tmp/claude-501/-Users-shuntasato-workspace-agent-instructions-playbook/
3ef6bea6-2f2e-4dff-b2ae-392b4019d6ac/scratchpad/fixture-a-research/analyzer.py

analyze() in that file has four independent suspects, all exercised by the
same loop over app.log:
  1. `pattern = re.compile(...)` is recompiled every line (re's internal
     cache means this is a dict lookup, not a full recompile, on repeat
     calls -- plausible but not obviously dominant).
  2. `if req not in seen_requests: seen_requests.append(req)` -- a Python
     list used as a membership set. `req` is unique per line (request=i is
     the loop index), so the membership check always scans the *entire*
     accumulated list before returning False. This is O(k^2) in the number
     of ERROR lines (k), pure Python-level comparisons.
  3. `stats["report"] = stats["report"] + (...)` grows a string via
     dict-item concatenation for every ERROR line. CPython's in-place
     string-concat fast path only applies to simple `x = x + y` on a bound
     variable with refcount 1, not to `d[k] = d[k] + y`, so this is
     plausibly O(k^2) in bytes copied.
  4. `stats["slowest"] = sorted(stats["slowest"] + [int(latency)],
     reverse=True)[:10]` runs on *every* line (not just errors) but the
     list is always length <=11, so this is O(1) per line / O(n) total --
     included as a control suspect expected to be minor.

Method: ablation. Each variant below is a structural copy of analyze()
with exactly ONE suspect fixed, all others left exactly as in the
original. Wall-clock time is measured per variant (median of 3 repeats on
the real 300k-line fixture, file cache warmed first). The variant whose
single fix recovers the most time relative to the baseline replica is the
dominant cause. `all_fixed` (all four suspects fixed at once) is a sanity
check, not part of the ranking. Every variant's output (error counts,
top-10 latencies, report length) is checked against the baseline replica's
output so a "fix" that is merely fast-and-wrong cannot masquerade as
evidence.
"""

from __future__ import annotations

import heapq
import json
import os
import re
import statistics
import sys
import time
from pathlib import Path

LOG_PATH = (
    "/private/tmp/claude-501/-Users-shuntasato-workspace-agent-instructions-playbook/"
    "3ef6bea6-2f2e-4dff-b2ae-392b4019d6ac/scratchpad/fixture-a-research/app.log"
)

PATTERN_SRC = r"^(\S+) (INFO|WARN|ERROR) (\w+) request=(\d+) latency_ms=(\d+)$"
COMPILED_PATTERN = re.compile(PATTERN_SRC)

REPEATS = 3


def run_baseline(path: str):
    """Exact structural replica of the original analyze(): all four
    suspects present."""
    stats = {"report": "", "slowest": []}
    counts: dict[str, int] = {}
    seen_requests: list[str] = []
    with open(path) as f:
        for line in f:
            pattern = re.compile(PATTERN_SRC)
            m = pattern.match(line.strip())
            if not m:
                continue
            ts, level, module, req, latency = m.groups()
            if level == "ERROR":
                if req not in seen_requests:
                    seen_requests.append(req)
                counts[module] = counts.get(module, 0) + 1
                stats["report"] = stats["report"] + (
                    f"[{ts}] {module} req={req} latency={latency}ms\n"
                )
            stats["slowest"] = sorted(stats["slowest"] + [int(latency)], reverse=True)[:10]
    return counts, stats["report"], stats["slowest"]


def run_fix_regex_recompile(path: str):
    """Only suspect 1 fixed: compile the pattern once, outside the loop."""
    stats = {"report": "", "slowest": []}
    counts: dict[str, int] = {}
    seen_requests: list[str] = []
    with open(path) as f:
        for line in f:
            m = COMPILED_PATTERN.match(line.strip())
            if not m:
                continue
            ts, level, module, req, latency = m.groups()
            if level == "ERROR":
                if req not in seen_requests:
                    seen_requests.append(req)
                counts[module] = counts.get(module, 0) + 1
                stats["report"] = stats["report"] + (
                    f"[{ts}] {module} req={req} latency={latency}ms\n"
                )
            stats["slowest"] = sorted(stats["slowest"] + [int(latency)], reverse=True)[:10]
    return counts, stats["report"], stats["slowest"]


def run_fix_seen_requests(path: str):
    """Only suspect 2 fixed: seen_requests is a set instead of a list."""
    stats = {"report": "", "slowest": []}
    counts: dict[str, int] = {}
    seen_requests: set[str] = set()
    with open(path) as f:
        for line in f:
            pattern = re.compile(PATTERN_SRC)
            m = pattern.match(line.strip())
            if not m:
                continue
            ts, level, module, req, latency = m.groups()
            if level == "ERROR":
                if req not in seen_requests:
                    seen_requests.add(req)
                counts[module] = counts.get(module, 0) + 1
                stats["report"] = stats["report"] + (
                    f"[{ts}] {module} req={req} latency={latency}ms\n"
                )
            stats["slowest"] = sorted(stats["slowest"] + [int(latency)], reverse=True)[:10]
    return counts, stats["report"], stats["slowest"]


def run_fix_string_concat(path: str):
    """Only suspect 3 fixed: report built as a list of parts, joined once
    at the end, instead of repeated dict-item concatenation."""
    report_parts: list[str] = []
    stats = {"slowest": []}
    counts: dict[str, int] = {}
    seen_requests: list[str] = []
    with open(path) as f:
        for line in f:
            pattern = re.compile(PATTERN_SRC)
            m = pattern.match(line.strip())
            if not m:
                continue
            ts, level, module, req, latency = m.groups()
            if level == "ERROR":
                if req not in seen_requests:
                    seen_requests.append(req)
                counts[module] = counts.get(module, 0) + 1
                report_parts.append(f"[{ts}] {module} req={req} latency={latency}ms\n")
            stats["slowest"] = sorted(stats["slowest"] + [int(latency)], reverse=True)[:10]
    return counts, "".join(report_parts), stats["slowest"]


def run_fix_slowest_resort(path: str):
    """Only suspect 4 fixed: maintain the top-10 latencies with a bounded
    min-heap instead of re-sorting an (up to 11-element) list every line."""
    stats = {"report": ""}
    counts: dict[str, int] = {}
    seen_requests: list[str] = []
    heap: list[int] = []
    with open(path) as f:
        for line in f:
            pattern = re.compile(PATTERN_SRC)
            m = pattern.match(line.strip())
            if not m:
                continue
            ts, level, module, req, latency = m.groups()
            lat = int(latency)
            if level == "ERROR":
                if req not in seen_requests:
                    seen_requests.append(req)
                counts[module] = counts.get(module, 0) + 1
                stats["report"] = stats["report"] + (
                    f"[{ts}] {module} req={req} latency={latency}ms\n"
                )
            if len(heap) < 10:
                heapq.heappush(heap, lat)
            elif lat > heap[0]:
                heapq.heapreplace(heap, lat)
    return counts, stats["report"], sorted(heap, reverse=True)


def run_all_fixed(path: str):
    """All four suspects fixed at once. Sanity check, not part of the
    ranking: confirms the fixes are independent/compatible and shows how
    much of the baseline is explained by these four suspects combined."""
    report_parts: list[str] = []
    counts: dict[str, int] = {}
    seen_requests: set[str] = set()
    heap: list[int] = []
    with open(path) as f:
        for line in f:
            m = COMPILED_PATTERN.match(line.strip())
            if not m:
                continue
            ts, level, module, req, latency = m.groups()
            lat = int(latency)
            if level == "ERROR":
                if req not in seen_requests:
                    seen_requests.add(req)
                counts[module] = counts.get(module, 0) + 1
                report_parts.append(f"[{ts}] {module} req={req} latency={latency}ms\n")
            if len(heap) < 10:
                heapq.heappush(heap, lat)
            elif lat > heap[0]:
                heapq.heapreplace(heap, lat)
    return counts, "".join(report_parts), sorted(heap, reverse=True)


VARIANTS = {
    "baseline": run_baseline,
    "fix_regex_recompile": run_fix_regex_recompile,
    "fix_seen_requests": run_fix_seen_requests,
    "fix_string_concat": run_fix_string_concat,
    "fix_slowest_resort": run_fix_slowest_resort,
    "all_fixed": run_all_fixed,
}

SINGLE_FIX_VARIANTS = [
    "fix_regex_recompile",
    "fix_seen_requests",
    "fix_string_concat",
    "fix_slowest_resort",
]


def time_variant(fn, path: str, repeats: int):
    times = []
    last_result = None
    for _ in range(repeats):
        t0 = time.perf_counter()
        last_result = fn(path)
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return statistics.median(times), times, last_result


def main() -> int:
    if not os.path.isfile(LOG_PATH):
        raise SystemExit(f"fixture not found (read-only input): {LOG_PATH}")

    # Warm the OS file cache once, untimed, so the first-timed variant
    # isn't penalized by cold disk I/O relative to the others.
    with open(LOG_PATH, "rb") as f:
        f.read()

    medians: dict[str, float] = {}
    all_times: dict[str, list[float]] = {}
    results: dict[str, tuple] = {}

    for name, fn in VARIANTS.items():
        median, times, last_result = time_variant(fn, LOG_PATH, REPEATS)
        medians[name] = median
        all_times[name] = times
        results[name] = last_result

    baseline_counts, baseline_report, baseline_slowest = results["baseline"]

    correctness: dict[str, dict[str, bool]] = {}
    for name in VARIANTS:
        if name == "baseline":
            continue
        counts, report, slowest = results[name]
        correctness[name] = {
            "counts_match": counts == baseline_counts,
            "slowest_match": slowest == baseline_slowest,
            "report_len_match": len(report) == len(baseline_report),
            "report_text_match": report == baseline_report,
        }
    correctness_ok = all(
        all(flags.values()) for flags in correctness.values()
    )

    baseline_median = medians["baseline"]
    recovered_seconds = {
        name: baseline_median - medians[name] for name in SINGLE_FIX_VARIANTS
    }
    recovered_fraction = {
        name: (recovered_seconds[name] / baseline_median if baseline_median > 0 else 0.0)
        for name in SINGLE_FIX_VARIANTS
    }
    dominant = max(recovered_seconds, key=recovered_seconds.get)

    metrics = {
        "log_path": LOG_PATH,
        "log_lines": sum(1 for _ in open(LOG_PATH)),
        "repeats": REPEATS,
        "python_version": sys.version,
        "medians_seconds": medians,
        "all_times_seconds": all_times,
        "recovered_seconds": recovered_seconds,
        "recovered_fraction": recovered_fraction,
        "dominant_suspect": dominant,
        "dominant_is_seen_requests": 1 if dominant == "fix_seen_requests" else 0,
        "correctness": correctness,
        "correctness_ok": correctness_ok,
        "baseline_median_seconds": baseline_median,
        "all_fixed_median_seconds": medians["all_fixed"],
    }

    run_dir = Path(os.environ["RESEARCH_RUN_DIR"])
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "result.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
