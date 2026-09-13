---
name: ui-verification
description: "Check changed appearance, responsive states, accessibility or user transitions against visual and runtime evidence."
---

# UI evidence

Choose evidence for the actual claim: screenshot comparison for rendered appearance,
interaction/state assertions for behavior, semantic checks for accessibility, and
real device/browser evidence for platform-specific boundaries. None proves all others.

Bind captures to candidate/build, viewport/device, theme, locale, data/initial state
and environment. Inspect the relevant rendered states rather than declaring visual
success from source review alone. Missing browser/device access leaves that claim
unverified, while independent implementation or component checks may continue.

Compare against accepted baselines or explicit design criteria, not arbitrary pixel
or aesthetic scores. Distinguish intentional visual changes from regressions. Cover
affected loading, empty, error, disabled, overflow and focus states when applicable;
do not fill a universal matrix for every edit.

Preserve accessibility semantics and supported journeys. Report concrete violations
and actual evidence. Optional polish is not blocking unless it violates a required
condition. Stop when required criteria pass, without a compulsory extra polish pass.
