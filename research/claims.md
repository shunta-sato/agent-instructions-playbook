# Research claims

ledger-head: 662e1462a7151b493c106f4378d4490f8979f2d2a2530daae210e03173242d5d

## C-0001
ratio improves — observed in a single configuration.
configurations: wt-research-os canonical ledger
evidence: E-0002

## C-0002
dominant_is_seen_requests degrades — observed in a single configuration.
configurations: CPython 3.13.13; analyzer.py analyze() replica; fixture-a-research/app.log, 300000 lines, seed=7 (72% INFO/13% WARN/15% ERROR, unique request id per line); ablation: one suspect fixed at a time, all others left as in the original; wall-clock median of 3 repeats per variant, file cache warmed before timing; every variant's output (error counts, top-10 latencies, report text) checked byte-identical to the baseline replica's output; fixing seen_requests alone recovered ~76-79% of baseline runtime vs ~5-23% for the other three suspects individually
evidence: E-0004
outcome-basis: E-0004=supported
sources: experiments/analyzer-cause/probe.py
