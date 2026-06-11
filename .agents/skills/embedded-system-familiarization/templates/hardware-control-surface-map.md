# Hardware Control Surface Map: <target>

Purpose: identify which hardware and workload factors can be controlled safely, which are only observable, and which must remain claim-limiting confounders.

## 1. Control Vocabulary

Control status:

- `controllable`: documented control method exists, can be verified, and restore is known.
- `not_controllable`: no practical control path exists for this target or environment.
- `read_only_observable`: value can be observed but not set by the test operator.
- `control_requires_privilege`: control exists but requires root, capability, service access, lab equipment, or operator approval.
- `control_unsafe`: control could damage the target, corrupt data, violate policy, or exceed safe operating limits.
- `control_not_supported`: hardware, OS, driver, firmware, or lab setup does not expose the control.

Evidence role:

- `controlled_factor`: intentionally set as part of the experiment.
- `observed_covariate`: measured and recorded but not set.
- `uncontrolled_confounder`: neither controlled nor sufficiently observed; limits claims.

## 2. Control Surface Inventory

| Factor | Evidence role | Control status | Read / observation command | Control command or method | Verification command | Requires privilege? | Reversible? | Operator approval required? | Safety precondition | Abort condition | Restore command or method | Restore verification | Claim boundary |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CPU governor | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |
| CPU frequency | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |
| CPU core affinity | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |
| Online CPU cores | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |
| Thermal state | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |
| Power mode / supply | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |
| Workload level | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |
| GPU / accelerator availability | controlled_factor|observed_covariate|uncontrolled_confounder | controllable|not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  | yes|no|unknown | yes|no|unknown | yes|no|unknown |  |  |  |  |  |

## 3. Safe Control / Restore Protocols

Use one entry per control action that will be used in a controlled operating point.

### Protocol: <factor>/<operation>

- Precondition:
- Control command or method:
- Verification command:
- Abort condition:
- Restore command or method:
- Restore verification:
- Requires privilege: yes|no|unknown
- Reversible: yes|no|unknown
- Operator approval required: yes|no|unknown
- Evidence path:

## 4. Not-Controllable Factors

| Factor | Classification | Reason | Observable proxy | Claim limitation | Follow-up |
| --- | --- | --- | --- | --- | --- |
|  | not_controllable|read_only_observable|control_requires_privilege|control_unsafe|control_not_supported |  |  |  |  |

## 5. Control Surface Risks

- Unsafe controls excluded:
- Privileged controls requiring approval:
- Controls not supported by this OS/kernel/firmware:
- Controls with restore risk:
- Controls that can perturb the workload:

## 6. Architecture / NFR Implications

| Claim or decision | Depends on factor | Control status | Evidence role | Allowed wording | Blocked wording |
| --- | --- | --- | --- | --- | --- |
|  |  |  | controlled_factor|observed_covariate|uncontrolled_confounder |  |  |
