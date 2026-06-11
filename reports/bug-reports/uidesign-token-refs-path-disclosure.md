## Bug Report (RCA)
- Title: UIDesign token_refs allowed arbitrary local path snapshotting
- Symptom (actual behavior): The UIDesign workflow accepted `meta.tone_and_manner.token_refs.*` values from a UIUX Pack and instructed agents to copy those referenced files into `tokens/resolved.tokens.*` without path allowlisting or traversal checks.
- Expected behavior: The workflow snapshots only intended Tone & Manner catalog token files, and rejects absolute paths, `..` traversal, non-catalog locations, and mismatched token file suffixes before reading or copying.
- Severity/Impact: High confidentiality impact; a malicious or compromised UIUX Pack could cause a trusted agent to copy sensitive local or workspace files into review artifacts.
- Environment (versions, platform, config): Documentation/template repository at HEAD `fc992d8d73cb3b8eee8c876b7eec523b0905a398`; markdown/yaml/json template workflow, no compiled runtime involved.
- Detection (how it was found): Aardvark vulnerability report for unvalidated UIDesign `token_refs` snapshot paths.

### Reproduction
- Steps to reproduce:
  1. Inspect `.agents/skills/uidesign-flow/SKILL.md` workflow steps for `token_refs` validation and snapshotting.
  2. Inspect `.agents/skills/uidesign-flow/templates/uidesign_contract.yaml` and token snapshot templates.
  3. Observe that the pre-fix workflow required `token_refs.json` / `token_refs.css` to exist in `ui_spec.json`, then copied from those paths without constraining the path source.
- Minimal repro (if available): A malicious UIUX Pack can set `meta.tone_and_manner.token_refs.css` to an absolute or traversal path such as `/home/user/.ssh/id_rsa` or `../../.env`; the pre-fix instruction would direct an agent to snapshot that content into `uidesign/.../tokens/resolved.tokens.css`.
- Frequency: Deterministic whenever an agent follows the pre-fix instructions with attacker-controlled token refs.

### Evidence
- Logs / stack trace / metrics / traces: Not applicable; this is an instruction-level file disclosure flaw, not a runtime crash. Evidence was gathered by reading the workflow and templates.
- What changed recently (if known): The UIDesign flow introduced token snapshot instructions and templates that copied from UIUX Pack-controlled token refs.

### Root Cause Analysis (Five Whys)
1) Why #1: Sensitive files could be copied because the workflow told agents to snapshot files from paths supplied by `ui_spec.json`. Evidence: pre-fix workflow copied from `meta.tone_and_manner.token_refs.*`.
2) Why #2: Attacker-controlled paths were trusted because the workflow only checked that token refs were present, not whether they were safe. Evidence: pre-fix required fields listed `token_refs.json` and `token_refs.css` but no path constraints.
3) Why #3: The contract template normalized direct path recording without a validation contract. Evidence: pre-fix `uidesign_contract.yaml` placeholders described paths from `ui_spec.json` directly.
4) Why #4: Snapshot templates reinforced copying from the raw UIUX metadata path. Evidence: pre-fix `resolved.tokens.*` templates said to copy from `ui_spec.json meta.tone_and_manner.token_refs.*`.
5) Why #5 (root cause): The trusted agent workflow lacked an explicit allowlist and content-type validation step for untrusted UIUX Pack references before file reads. Evidence: no pre-fix instructions rejected absolute paths, traversal, non-catalog locations, or non-token suffixes.

> Rule: each “Why” must be backed by evidence or a clearly labeled assumption.

### Fix
- What changed (summary): Added a required validation step before any token read/copy; constrained token refs to relative `tonemana/catalog/tokens/` paths without `..`, with `.tokens.json` / `.tokens.css` suffixes, existing files, and JSON-object parsing for JSON tokens. Updated reference docs, contract placeholders, token snapshot templates, and the GitHub Copilot prompt to carry the same safety rule.
- Why this fix addresses the root cause: The workflow now treats UIUX Pack token refs as untrusted input and prevents reads from arbitrary absolute, traversal, or non-catalog paths before snapshot artifacts can be created.

### Verification
- Tests run:
  - `rg -n "Copy from ui_spec|Snapshot token_refs into|path from ui_spec" .agents/skills/uidesign-flow .github/prompts/uidesign-flow.prompt.md`
  - `make build-debug`
  - `make lint`
  - `make analysis`
  - `make test-unit`
  - `make test-integration`
  - `make verify`
- Repro re-run result: Static repro condition removed; the workflow now instructs agents to stop before reading or copying invalid token refs.
- Tooling run (if relevant): Canonical repository checks passed.

### Prevention (must include at least one, measurable)
- Prevent: Keep token snapshot source constraints in the UIDesign skill, reference, contract, and prompt so every entry point requires catalog path validation before file reads.
- Detect: Use `rg` checks for unsafe legacy phrases such as `Copy from ui_spec`, `Snapshot token_refs into`, and `path from ui_spec` in UIDesign docs/templates.
- Mitigate: If validation fails during a UIDesign run, stop and rerun `$tonemana-apply` or request corrected catalog token refs; do not snapshot partial artifacts.
- Follow-up tasks (with owners / tracking IDs if available): None; this patch updates the currently known UIDesign entry points.

### Workaround (only if unavoidable)
- Workaround description: Before this fix, reviewers could manually inspect `token_refs` and reject absolute, traversal, or non-catalog paths.
- Risk: Manual inspection is error-prone and can be skipped by agents following the workflow literally.
- Removal plan / tracking: The workaround is superseded by the explicit validation requirements added in this patch.
