"""Probe: does textbook first-element-pivot recursive quicksort degrade
superlinearly relative to built-in sorted() on nearly-sorted input?

Disposable research probe code (experiments/ is a research-mode path;
code-quality gates are waived here per research-workflow). Evidence
discipline is not waived: this script is invoked only through
scripts/research_run.py register/execute, which stamps outcome and timing.

Input shape: a sorted list of N ints with a fixed fraction of random
index-pair swaps applied ("nearly sorted"). First-element-pivot quicksort
on nearly-sorted data is close to its known worst case (each partition is
maximally unbalanced), so recursion depth approaches N. We raise the
recursion limit and run the recursive sort on a thread with a large C
stack to let it complete rather than crash, and honestly record it as
recursion_error / not-evaluable if it still fails.
"""

from __future__ import annotations

import json
import os
import random
import sys
import threading
import time
from pathlib import Path

N = 20_000
SWAP_FRACTION = 0.01
SEED = 20260712
RECURSION_LIMIT = 200_000
THREAD_STACK_BYTES = 512 * 1024 * 1024  # 512 MiB


def make_nearly_sorted(n: int, swap_fraction: float, seed: int) -> list[int]:
    rng = random.Random(seed)
    data = list(range(n))
    n_swaps = int(n * swap_fraction)
    for _ in range(n_swaps):
        i = rng.randrange(n)
        j = rng.randrange(n)
        data[i], data[j] = data[j], data[i]
    return data, n_swaps


def quicksort(arr: list[int], lo: int, hi: int) -> None:
    """Textbook recursive quicksort, first element as pivot (Hoare-style
    partition, in place)."""
    if lo >= hi:
        return
    pivot = arr[lo]
    i, j = lo + 1, hi
    while True:
        while i <= j and arr[i] <= pivot:
            i += 1
        while i <= j and arr[j] > pivot:
            j -= 1
        if i > j:
            break
        arr[i], arr[j] = arr[j], arr[i]
    arr[lo], arr[j] = arr[j], arr[lo]
    quicksort(arr, lo, j - 1)
    quicksort(arr, j + 1, hi)


def run_quicksort_on_thread(data: list[int]) -> dict:
    """Run the recursive quicksort on a dedicated thread with a large C
    stack and a raised Python recursion limit, so a ~N-deep recursion on
    adversarial (nearly-sorted) input can complete instead of crashing the
    interpreter. Catches RecursionError honestly rather than hiding it."""
    outcome: dict = {}

    def target() -> None:
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(RECURSION_LIMIT)
        try:
            arr = data[:]
            start = time.perf_counter()
            quicksort(arr, 0, len(arr) - 1)
            elapsed = time.perf_counter() - start
            outcome["status"] = "ok"
            outcome["seconds"] = elapsed
            outcome["correct"] = arr == sorted(data)
        except RecursionError as exc:
            outcome["status"] = "recursion_error"
            outcome["error"] = str(exc)
        finally:
            sys.setrecursionlimit(old_limit)

    threading.stack_size(THREAD_STACK_BYTES)
    t = threading.Thread(target=target)
    t.start()
    t.join()
    return outcome


def main() -> int:
    data, n_swaps = make_nearly_sorted(N, SWAP_FRACTION, SEED)

    qs_outcome = run_quicksort_on_thread(data)

    sorted_start = time.perf_counter()
    sorted_result = sorted(data)
    sorted_seconds = time.perf_counter() - sorted_start
    sorted_correct = sorted_result == list(range(N))

    metrics: dict = {
        "n": N,
        "swap_fraction": SWAP_FRACTION,
        "swap_count": n_swaps,
        "seed": SEED,
        "python_version": sys.version,
        "quicksort_status": qs_outcome.get("status"),
        "sorted_seconds": sorted_seconds,
        "sorted_correct": sorted_correct,
    }

    if qs_outcome.get("status") == "ok":
        qs_seconds = qs_outcome["seconds"]
        metrics["quicksort_seconds"] = qs_seconds
        metrics["quicksort_correct"] = qs_outcome["correct"]
        # ratio is the only metric the registered disconfirm predicate reads;
        # omitted entirely (not a sentinel) if it cannot be computed (quicksort
        # did not complete, or the sorted() timer read exactly zero), so the
        # runner honestly derives "not-evaluable" instead of a fabricated
        # number or a crash on None.
        if sorted_seconds > 0:
            metrics["ratio"] = qs_seconds / sorted_seconds
    else:
        metrics["quicksort_error"] = qs_outcome.get("error")

    run_dir = Path(os.environ["RESEARCH_RUN_DIR"])
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "result.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(json.dumps(metrics, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
