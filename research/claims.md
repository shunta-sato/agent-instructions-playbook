# Research claims

ledger-head: 662e1462a7151b493c106f4378d4490f8979f2d2a2530daae210e03173242d5d

## C-0001
ratio stayed on the non-disconfirming side of <= 1 — observed in a single configuration.
configurations: single configuration
evidence: E-0002

## C-0002
dominant_is_seen_requests stayed on the non-disconfirming side of == 0 — observed in a single configuration.
configurations: log_path=fixture-a-research/app.log(300000 lines, seed=7); repeats=3,median; corrected-predicate-of-E-0003
evidence: E-0004
outcome-basis: E-0004=supported
sources: experiments/analyzer-cause/probe.py
