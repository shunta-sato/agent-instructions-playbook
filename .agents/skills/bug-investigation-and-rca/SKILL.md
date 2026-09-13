---
name: bug-investigation-and-rca
description: "Use for non-trivial or unclear bugs, regressions, crashes, hangs, flakes, incidents, or explicit root-cause/RCA work where the cause must be established from evidence."
---

# Evidence-backed bug investigation

Use this skill when the defect is not already explained by a direct, verified local cause, or when the request asks for root cause. An obvious typo or small defect with a clear cause can stay on the ordinary working contract.

Establish the observed failure and relevant environment first. Prefer a reproducible signal, failing test, trace, log, dump, or other discriminating observation. If reproduction is unavailable, say so and use the strongest available evidence without turning inference into fact.

Keep observations, live hypotheses, and confirmed cause distinct. A final patch passing is evidence that behavior changed; by itself it does not prove why the original failure occurred. Choose the cheapest next observation that can distinguish plausible explanations. Change an uninformative approach instead of repeating it. There is no required hypothesis count, Five Whys sequence, or retry limit.

When a fix is requested, address the supported cause rather than only hiding the symptom. Verify the original failure path and relevant neighboring boundaries at the lowest useful level, plus higher-level behavior when the contract crosses a real integration boundary. A regression check should fail on the defective behavior and pass with the fix when that comparison is practical.

Distinguish a root-cause fix from a mitigation or workaround. A retained workaround needs its risk and removal/revisit condition when those matter to the supported use. Do not invent a prevention project for every bug.

Use other specialists only when the evidence reaches their concrete boundary, for example concurrency, performance, auth/session, database migration, target runtime, or generated cross-host workflow semantics. Escalate to `lessons-learned` when the useful output is durable learning from a recurring or consequential process/tool/instruction failure, not for every single bug.

Report the symptom, the confirmed cause or remaining hypothesis, decisive evidence, the fix when requested, verification, and material limits. Create a standalone RCA document only when the requester, incident process, compliance rule, or downstream consumer actually needs one.
