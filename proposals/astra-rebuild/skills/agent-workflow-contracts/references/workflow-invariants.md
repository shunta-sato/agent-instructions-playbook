# Workflow invariants

A producer's exact artifact must be the consumer's input. Preserve run set, plan
reference, workflow ID, target ID/class and candidate identity across validation
and reporting. A constraints check must use the intended constraints artifact,
not whichever file was written last. No mtime/latest/sort-tail approval selection.

For each affected generated command check argv boundaries, working directory,
controller/target location, required environment, expected output and continuation
condition. Replay safely; do not execute production effects just to test a recipe.

Installation success does not establish runtime discovery. Check non-interactive
SSH PATH, absolute runner location, explicit environment overrides, helper paths,
version skew and useful missing-binary diagnostics under the actual invocation.

Workflow recommendation, collect-plan generation, validation, synthetic load,
operator handoff, target measurement and release readiness are distinct claims.
Raw primitive artifact co-presence is not proof of lineage or authorization.
A report must not promote a successful earlier stage into a broader later claim.
