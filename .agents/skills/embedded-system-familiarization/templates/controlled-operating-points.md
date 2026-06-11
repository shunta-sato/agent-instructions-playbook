# Controlled Operating Points: <target>/<feature>

Purpose: record which operating points were intentionally controlled, which were merely observed, and which claims are allowed from the resulting evidence.

## 1. Coverage Vocabulary

Operating point coverage status:

- `not_started`: no observation or control evidence exists yet.
- `observational_only`: values varied naturally or were observed under an uncontrolled policy; this is not a sweep.
- `partially_controlled`: some factors were controlled, but important factors remain uncontrolled or weakly observed.
- `controlled_subset`: a defined subset of factor values was controlled and verified.
- `controlled_full`: the full claimed range was controlled, verified, and restored safely.
- `blocked_unsafe`: control was intentionally not attempted because it is unsafe.
- `not_controllable`: the factor cannot be controlled on this target or in this environment.

Experimental confidence:

- `none`: no usable evidence.
- `low`: observation only, single run, unknown confounders, or host-only fallback.
- `medium`: controlled subset with verified setup/restore and known residual confounders.
- `high`: repeated controlled sweep with thermal, power, workload, and noise conditions recorded.

Rule: observed natural variation such as `scaling_cur_freq` moving between values under an `ondemand` governor is `observational_only` and at most `low` confidence for frequency-range claims.

## 2. Factor Coverage

| Factor | Coverage status | Evidence role | Values observed | Values controlled | Residual covariates | Uncontrolled confounders | Confidence | Evidence path |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU governor | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  | none|low|medium|high |  |
| CPU frequency | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  | none|low|medium|high |  |
| CPU core affinity | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  | none|low|medium|high |  |
| Online CPU cores | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  | none|low|medium|high |  |
| Thermal state | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  | none|low|medium|high |  |
| Power mode | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  | none|low|medium|high |  |
| Workload level | not_started|observational_only|partially_controlled|controlled_subset|controlled_full|blocked_unsafe|not_controllable | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |  |  | none|low|medium|high |  |

## 3. Operating Point Records

| Operating point ID | Factor values | Given conditions | Controlled factors | Observed covariates | Uncontrolled confounders | Safety precondition | Control method | Verification method | Abort condition | Restore method | Restore verification | Requires privilege? | Reversible? | Operator approval required? | Evidence path | Confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OP-001 |  |  |  |  |  |  |  |  |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  | none|low|medium|high |

## 4. Claim-To-Evidence Trace

| Claim | Depends on operating points / factors | Required coverage | Actual coverage | Evidence path | Confidence | Allowed wording | Blocked wording / status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| works at all CPU clocks | CPU frequency, governor, thermal state, workload level | controlled_full across claimed range |  |  | none|low|medium|high |  | blocked|provisional|target-specific |
| low overhead across frequency range | CPU frequency, workload level, observer effect | controlled_subset or controlled_full matching the wording |  |  | none|low|medium|high |  | blocked|provisional|target-specific |
| battery safe | power mode, workload level, thermal state, duration | repeated controlled runs under claimed power conditions |  |  | none|low|medium|high |  | blocked|provisional|target-specific |
| GPU offload is better | GPU control surface, cost model, workload fit, thermal/power cost | controlled benchmark and cost model |  |  | none|low|medium|high |  | blocked|provisional|target-specific |

## 5. Coverage Gaps

| Gap | Affected claim | Why gap remains | Safe next experiment | Current allowed wording |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |
