# Astra-generation redesign

This is an instruction architecture change, not a model-performance claim. It implements
outcome contracts, selective Skill discovery, human-aligned preflight, conditional specialist
references and mechanical checks of real outcomes. No second generic delivery super-Skill.

## Four boundaries

- The contributor contract describes this repository only. The consumer template is a
  starting point, not an automatic project-policy overwrite.
- Human and agent align on outcome, scope, relevant quality, verification fidelity and
  authority in the existing task/PR/brief. Material unknowns require a question/answer;
  ordinary implementation details and already-settled decisions do not.
- Specialist Skills provide non-obvious knowledge, evidence dependencies and optional tools.
  They do not replace ordinary design/debugging or require a fixed chain of Skill invocations.
- The harness/CI/target enforces permissions and runs checks. Instructions and self-reported
  readiness cannot sandbox execution or confer approval. Model choice belongs to the harness.

## Preflight is not optional information gathering

Removing procedural micromanagement must not remove human communication or the ability to
verify the requested outcome. The failure pair addressed here is (a) implementing first,
then quietly substituting UTs or a caveat for required E2E, and (b) pursuing completion by
bypassing access/security controls or moving a denied action to another execution site.

The common contract requires early, proportionate alignment and verification readiness even
if no specialist is auto-selected. `preflight-engineering` is rewritten to fulfill that role.
Read existing facts, briefly reflect the intended result, ask decision-changing questions with
bounded options, and await an authoritative answer for the affected decision. Silence is not
approval. Continue useful independent work; do not demand permission for already-authorized
steps. Ask for approved secret provisioning, not pasted secret values. Reopen only changed
assumptions, scope, environment or authority.

Before substantial implementation, demonstrate the relevant input-to-observable-result path
in the approved environment. Greenfield work can first build a minimal runnable slice. Existing
current evidence is reusable. A launch/config/account failure is not a missing-feature Red;
readiness is not feature acceptance. Identify blockers early and repair within authority or
escalate precisely. An authorized alternative site/tool may be used, but not to evade denial.

`agentic-tdd` defines the outer acceptance/E2E loop and inner focused tests for user-visible
runtime delivery or explicit test-first work. Agree on the real boundary, substitutes and
result oracle. Static/library tasks use the appropriate public-boundary proof. UTs, screenshots,
all-skipped runs or a healthy process do not replace a required E2E result. The final candidate
must have valid required evidence; environment changes may invalidate earlier readiness.
A Draft PR or handoff shares partial work, not an unverifiable completion claim.

## Deliberate removals and preserved value

Mandatory generic delivery/final-gate routing, all-Skill index, model/role lockfiles, generic
coding lesson Skills, fixed rollback counters and report packs are removed. Existing retired
names have no aliases. Rewriting RCA and Preflight in place preserves their evidence and
communication value, not their former recipes. No automatic project-wide line/test count or
polling threshold remains. `docs/skill-disposition.json` records every prior entrypoint.

Retained assets include context-driven required/target quality distinctions, target/workload
proof, controller/target identity and argv boundaries, platform/lifecycle/concurrency knowledge,
seven UI style/token families, API-removal sweep, repository/mobile inspectors, research
runner and claim/promotion/digest verification with regression tests. Historical evidence
stays immutable. New regressions take priority over accumulating generic instructions.

## Validation and honest limits

`make verify` checks current resources, Python syntax, ledger integrity and executable tests.
The preflight/E2E fixture checks real CLI startup and state across fresh processes; deliberately
broken implementations and success-only output must fail the oracle. It establishes that the
fixture can distinguish outcomes, not that an agent followed TDD or communicated correctly.

`evals/` adds material-unknown, denied-access, false-Green, unchanged-context and mid-run-loss
review cases. Trace review must examine when questions were asked, what answer authorized
an action, actual early readiness execution, test ordering and final claim fidelity. The
single-invocation adapter does not emulate a human conversation: no reply is the condition
for a first-turn escalation case. Subsequent-turn outcomes need a real authorized conversation
and matched transcripts. Do not invent consent or score eventual completion from a seed.

Live Astra behavior remains unmeasured. The runner is not a sandbox; adapter confinement and
independent adjudication are required. This PR is suitable for code review, not a claim of
proven Astra superiority, an optimal Skill count or production readiness.

## Sources and interpretation

- OpenAI, "Rethinking skills and prompts for GPT-6 Astra":
  https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra
- OpenAI Skills documentation: https://developers.openai.com/codex/build-skills

The redesign uses selective guidance, scoped autonomy and explicit completion. The follow-up
human-alignment/readiness requirement comes from requester feedback on this PR. Neither fewer
safeguards nor forced completion is inferred from model capability. Counts, profiles, fixture
contracts and sequencing choices are project policies, not vendor certification.
