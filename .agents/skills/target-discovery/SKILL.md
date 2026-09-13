---
name: target-discovery
description: "Resolve unknown hardware capabilities, workloads, operating states, or control surfaces that affect a target-specific decision."
---

# Target discovery

Learn only the target facts needed to choose an implementation or trustworthy
measurement. Reuse current characterization. A daemon, logger, Android, or ROS label
alone does not justify a full hardware investigation.

`references/operating-envelope.md` covers missing workload, baseline, resource,
capability and degradation facts. `references/hardware-controls.md` applies when an
experiment changes governor, affinity, power mode, accelerator settings, or another
physical operating point. Read neither solely to satisfy an inventory.

Keep observed natural variation separate from controlled factors, given conditions,
observed covariates and uncontrolled confounders. Unknown power state is not AC.
Do not infer target performance from host-only results or a vendor's theoretical peak.

Prefer safe read-only discovery, replay or simulation before an action with physical
risk. A privileged control operation requires actual authority, an abort condition,
and verified restoration. Continue independent discovery when that operation is
blocked. Return decision-changing observations and limits, not ten mandatory maps.
