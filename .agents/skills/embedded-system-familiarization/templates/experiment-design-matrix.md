# Experiment Design Matrix: <target>/<feature>

Purpose: plan controlled operating point experiments so factor control, ordering, repetition, noise, thermal state, and restore behavior are explicit before measurements are trusted.

## 1. Experiment Question

- Decision or claim under test:
- Claimed operating range:
- Primary response metrics:
- Safety limits:
- Stop / abort owner:

## 2. Factor Classification

| Factor | Role | Levels / range | Control source | Observation source | Safety limit | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| CPU governor | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  |  |
| CPU frequency | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  |  |
| CPU core affinity | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  |  |
| Online CPU cores | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  |  |
| Thermal state | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  |  |
| Power mode / supply | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  |  |
| Workload level | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  |  |

## 3. Matrix

| Run ID | Operating point ID | CPU governor | CPU frequency | Core affinity | Online cores | Thermal precondition | Power mode | Workload level | repetitions | warmup_seconds | cooldown_seconds | order | randomization | thermal_soak_state | ambient_condition | Measurements | Evidence path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- |
| R-001 | OP-001 |  |  |  |  |  |  |  |  |  |  | fixed|randomized|blocked | none|seed=<value>|not_applicable | cold|warm|steady|unknown |  |  |  |

## 4. Repetition, Noise, And Soak Plan

- Repetitions per operating point:
- Warmup seconds:
- Cooldown seconds:
- Run ordering:
- Randomization method / seed:
- Thermal precondition:
- Thermal soak state:
- Ambient condition:
- Noise sources to record:
- Noise sources to block:
- Residual confounders:

## 5. Setup / Restore Sequence

| Step | Action | Verification | Abort condition | Restore action | Restore verification |
| --- | --- | --- | --- | --- | --- |
| 1 |  |  |  |  |  |

## 6. Confidence Plan

| Evidence pattern | Confidence | Allowed claim strength |
| --- | --- | --- |
| No run or host-only fallback | none|low | blocked or host-only provisional |
| Observed natural variation only | low | observed under current policy; no sweep claim |
| Controlled subset with verified setup and restore | medium | limited to tested operating points |
| Repeated controlled sweep with thermal/power/workload conditions recorded | high | range claim only within swept range and recorded conditions |

## 7. Data Quality Checks

- Missing samples:
- Clock/source consistency:
- Observer-on vs observer-off comparison:
- Thermal throttling or mitigation detection:
- Power mode drift:
- Workload saturation / backpressure:
- Outlier policy:
- Report path:
