# Routing eval — first measurement (2026-07-23)

Subjects: 24 isolated Sonnet 5 sessions (Claude Code subagents), one per batch,
each seeing ONLY the variant's self-contained prompt pack (no repo access, no
expectations). Variants: pre98 = commit 5d2b413 (before WS-A), post98 = commit
b908894 (after WS-A). Single run per case per variant — treat point deltas of a
few percent as suggestive, not conclusive; no confidence interval is claimed.
GPT-class runners: not yet executed — the packs are runner-agnostic and this slot
is open (see README).

## Supervisor reading

- WS-A's 15% discovery-surface cut came with a ~3pt should-trigger recall drop
  concentrated in the embedded-NFR family (chain skills such as
  target-characterization / operating-envelope-discovery / nfr-calibration are
  missed more often after the routing table moved into the reference §2a).
  Both variants already struggled on those chains; post is somewhat worse.
- Should-not-trigger compliance is essentially unchanged (98.9% → 98.3%) and mean
  co-fire slightly improved (3.29 → 3.14): the reduction did not cause
  over-selection; the cost is under-selection on deep multi-skill chains.
- WS-C implication: embedded-chain discoverability is the first repair target
  (options: a stronger one-line chain cue in the surface, or revisiting eval
  expectations that demand 4+ co-fired chain skills from a one-line prompt);
  trigger NARROWING proposals must not touch the embedded family until this is
  addressed.

# Routing Eval Report

| Metric | wt-pre98 | wt-wsb |
| --- | --- | --- |
| Commit | 5d2b41378453676e9f791fb0967e36d482dd20c5 | b90889495f1d688411c5cc6f546f244ef431be1a |
| Cases graded | 212/212 | 212/212 |
| Should-trigger recall | 86.0% | 82.9% |
| Should-not-trigger compliance | 98.9% | 98.3% |
| Mean co-fire | 3.288 | 3.142 |
| p90 co-fire | 5.0 | 5.0 |
| Surface lines | 708 | 647 |
| Surface chars | 77511 | 65656 |

## Worst cases (wt-pre98)

- existing-logger-blackout-boundary: missed=['embedded-target-characterization', 'embedded-operating-envelope-discovery', 'embedded-observer-effect-review', 'embedded-nfr-calibration']
- embedded-envelope-unknown: missed=['embedded-target-characterization', 'embedded-nfr-calibration']
- fixed-frequency-benchmark-needed: missed=['embedded-system-familiarization', 'embedded-operating-envelope-discovery']
- gpu-capability-without-cost-model: missed=['architecture-decision-analysis']; violated=['embedded-nfr-harness-design']
- observed-cpufreq-not-controlled-sweep: missed=['embedded-system-familiarization', 'embedded-operating-envelope-discovery']
- architecture-negative-observability-detail: violated=['quality-gate']
- battery-safe-claim-without-measurement: missed=['embedded-nfr-design']
- destructive-refactor-delete-obsolete-positive: missed=['destructive-refactor']
- destructive-refactor-replace-old-abstraction-positive: missed=['function-boundary-governor']
- destructive-refactor-wrong-side-effects: missed=['function-boundary-governor']

## Worst cases (wt-wsb)

- embedded-system-performance-extraction: missed=['embedded-system-familiarization', 'embedded-target-characterization', 'embedded-nfr-calibration', 'architecture-decision-analysis']
- existing-logger-blackout-boundary: missed=['embedded-target-characterization', 'embedded-operating-envelope-discovery', 'embedded-observer-effect-review', 'embedded-nfr-calibration']
- observed-cpufreq-not-controlled-sweep: missed=['embedded-system-familiarization', 'embedded-operating-envelope-discovery', 'embedded-nfr-calibration']
- embedded-daemon-proc-watcher: missed=['embedded-nfr-harness-design', 'embedded-hot-path-review']
- embedded-envelope-unknown: missed=['embedded-target-characterization', 'embedded-nfr-calibration']
- embedded-system-boundary-optimization: missed=['embedded-observer-effect-review', 'embedded-nfr-calibration']
- embedded-system-new-target-optimization: missed=['embedded-operating-envelope-discovery', 'embedded-nfr-calibration']
- fixed-frequency-benchmark-needed: missed=['embedded-system-familiarization', 'embedded-operating-envelope-discovery']
- android-background-work: missed=['concurrency-core']
- architecture-negative-observability-detail: violated=['quality-gate']

## WS-C1 repair result (same day)

The chain-composition cues (6 lines in dev-workflow reference §2a: familiarization
rides with its missing-context stages; measurement adds harness-design;
perturbing measurement adds observer-effect-review; unsupported claims and
uncharacterized malfunctions route to the learning chain) plus the preflight
reachability row were applied and the FULL corpus re-measured with 12 fresh
isolated Sonnet subjects (`20260723-chainfix-sonnet-5.json`):

| Metric | post98 | chainfix |
| --- | --- | --- |
| Should-trigger recall | 82.9% | 87.0% |
| Should-not-trigger compliance | 98.3% | 98.3% |
| Mean co-fire | 3.142 | 3.212 |
| Surface chars | 65,656 | 66,899 |

Recall recovered past the pre-WS-A baseline (86.0%) at a surface cost of +1.2k
chars (net vs pre-WS-A: still −14%). Embedded skill-misses dropped 24 → 17.
Compliance unchanged — the cues did not cause over-selection; the small co-fire
rise is completed chains, which is the intended behavior. No eval expectation was
modified. Largest remaining miss cluster: `destructive-refactor` (6 cases, present
at the same level in every variant) — next repair candidate, same protocol.
Single-run caveat applies to all three variants equally.
