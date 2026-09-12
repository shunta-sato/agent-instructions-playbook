---
name: mobile-runtime-evidence
description: "Use when a mobile behavior or cross-platform parity claim requires simulator/emulator or device evidence."
---

# Mobile runtime evidence

Identify the changed journey, platform, source/build, device/OS, app configuration,
backend/fixture and independent oracle. Use [runtime boundaries](references/runtime-boundaries.md)
when host, simulator, framework or agent-driven evidence may be confused.

Check parity by capability and supported failure behavior, not equal file counts.
Record intentional platform differences. Host unit tests can support logic but do
not prove installation, permissions, lifecycle or device integration.

Reuse valid build/device evidence. Run focused scenarios instead of restarting an
entire release gate after each worker. If required device evidence is unavailable,
complete independent work and report the exact missing claim; do not call it a
pass or silently turn a requested release into a demo.
