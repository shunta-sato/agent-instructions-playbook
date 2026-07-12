# Research claims

ledger-head: 662e1462a7151b493c106f4378d4490f8979f2d2a2530daae210e03173242d5d

## C-0001
Observed once under configuration wt-research-os canonical ledger: digest fix restores canonical-ledger execution (ratio improves).
evidence: E-0002

## C-0002
Observed once under configuration CPython 3.13.13; analyzer.py analyze() replica; fixture-a-research/app.log, 300000 lines, seed=7 (72% INFO/13% WARN/15% ERROR, unique request id per line); ablation: one suspect fixed at a time, all others left as in the original; wall-clock median of 3 repeats per variant, file cache warmed before timing; every variant's output (error counts, top-10 latencies, report text) checked byte-identical to the baseline replica's output; fixing seen_requests alone recovered ~76-79% of baseline runtime vs ~5-23% for the other three suspects individually: dominant cause of analyzer.py slowness on the 300k-line app.log fixture: seen_requests list-membership scan (O(k^2) in ERROR-line count) vs. three other candidate suspects (regex recompiled per line, dict-item string concatenation for the error report, per-line list re-sort of top-10 latencies) (dominant_is_seen_requests degrades).
evidence: E-0004
outcome-basis: E-0004=supported
sources: experiments/analyzer-cause/probe.py
