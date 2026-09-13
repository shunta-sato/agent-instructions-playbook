# ISO/IEC 25010 quality scenarios

This is a selective Playbook discovery aid, not the standard text, a compliance
assessment, or a requirement to implement every quality mechanism.
ISO/IEC 25010:2023 defines a product quality model with nine characteristics.
The earlier 2011 outline had eight: usability and portability are replaced by
interaction capability and flexibility; safety is a separate characteristic.
The prompts below are practical examples, not a reproduction of subcharacteristics.

First apply `quality-context.md`: select applicable requirements from current use,
classify obligations independently of evidence, and inherit existing policy.
Do not generate a filled matrix, numeric goal, or benchmark for every category.

## Scenario shape

Describe **context → stimulus → expected response → verifiable condition**.
Include affected component/user, workload, source and obligation (`required` or
`target`), agreed verification, evidence status, and revisit trigger in the existing
Quality Targets. Record material exclusions with reason; unknown is not exclusion.
Numeric limits need a source. Qualitative requirements can use a concrete change,
inspection, or recovery scenario. Baseline measurements are not requirements.

## Functional suitability

Which supported input/operation must produce what result, including errors?
Verify completeness and correctness against acceptance and realistic regressions.
A successful demonstration is not proof of unrelated qualities.

## Performance efficiency

What normal/peak input, cadence, concurrency, runtime duration, and deployment
scale matter? Which time/resource/capacity limit affects the user or system?
Inspect bounds and cost routinely; measure when a decision or required criterion
needs it. Consider tails/deadlines, allocation, memory growth, query counts, and
saturation when applicable. Cache or parallelize only with justified trade-offs.

## Compatibility

Which callers, data formats, platforms, and co-resident components must continue
to work? Test semantic contracts and resource interference where relevant.
Use the recorded preserve/staged/break-allowed mode, not universal compatibility
shims or unilateral removal of existing obligations.

## Interaction capability

Can intended users operate the supported journey and recover from mistakes?
Consider accessibility, assistance, input constraints, and platform conventions.
Use applicable accessibility/usability criteria and appropriate automated/manual
proof; do not invent a universal WCAG target for every kind of software.

## Reliability

What happens after dependency loss, overload, interruption, or partial completion?
Set applicable recovery/data-loss limits and verify restart/restore/retry behavior.
Short product lifetime does not remove continuous-runtime leak or recovery risks.
A fallback must not conceal an error the caller needs to observe.

## Security

Which actors, trust boundaries, information, permissions, and abuse paths exist?
Verify relevant authentication/authorization, confidentiality, integrity, privacy,
and audit obligations. Do not add unneeded logging or weaken real boundaries in
pursuit of a shorter patch. Logs must not expose secrets.

## Maintainability

Who performs expected changes, upgrades, diagnosis, and handoff, and how often?
Use a representative operation to evaluate understanding, change locality, and
reverification. Short-lived frequently edited code differs from stable long-lived
code. Neither implies a plugin system, coverage percentage, or file-count goal.
Preserve rationale that a future maintainer needs; omit redundant narration.

## Flexibility

Which environments, installation/update paths, scale changes, and replacements
are actually supported? Verify those paths and bounded adaptation costs.
Do not add configuration or abstraction for platforms that are not required.

## Safety

Can incorrect, late, or absent behavior cause harm directly or through another
component? Identify applicable constraints, safe states, isolation, and assurance
ownership. Industry names alone do not classify the affected component. Use the
actual safety process/standard when applicable; this model is not certification
and does not authorize substituting ad hoc tests for required assurance.

## Cross-cutting use and limits

Operating cost, energy, data retention/deletion, deployability, and observability
may span attributes; select them when the actual use requires them. Trace required
criteria to the final gate. Optional goals can remain unmet, but a `not-measured`
label cannot discharge a mandatory condition. Revisit when the use/envelope changes.

## References (reviewed 2026-09-06)

- [ISO/IEC 25010:2023 product quality model](https://www.iso.org/standard/78176.html)
- [ISO/IEC 25010:2011, superseded edition](https://www.iso.org/standard/35733.html)
- [ISO Online Browsing Platform](https://www.iso.org/obp/ui/): edition change summary.
- [SEI Quality Attribute Workshop](https://www.sei.cmu.edu/library/quality-attribute-workshop-collection/)
- [Google SRE: Implementing SLOs](https://sre.google/workbook/implementing-slos/)
