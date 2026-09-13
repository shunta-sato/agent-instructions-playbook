# Evidence that matches the claim

Select the least elaborate method that resolves the uncertainty: inspection for bounded
known behavior, focused measurement for uncertain scaling, or target/workload evidence for
physical and strict timing claims. Functional tests cannot alone prove energy or endurance.

Record candidate/build, target, workload, configuration, method, observation interval,
sample limitations and raw artifact identity. For percentile claims retain sample count,
warmup/steady-state treatment and tail visibility. Do not call a noisy one-off change a
causal improvement. Reuse a result only while all relevant conditions remain valid.

Use existing target tooling before building a harness. Synthetic load proves only its
tested envelope. A host fallback cannot masquerade as a target run. Unavailable hardware,
tools or sensors must remain visible. Continue useful authorized work without claiming
the unavailable evidence. Run affected proof again after a material change, not merely
because the reviewer or agent changed.

The optional `scripts/verify_evidence.py` checks manifest linkage and artifact digests;
it cannot determine that measurements are genuine or that a chosen method is sufficient.
See the script's `--help` and its schema in `references/evidence-format.md`.
