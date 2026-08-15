# Workflow Contract Review

## Scope

- PR / branch: current working tree
- Workflow surfaces: `setup.sh`, `README.md`, and `tests/test_setup_sh.py`
- Generated artifacts: two worktree-local skill symlinks and two local Git exclude entries

## Source-of-truth chain

| Stage | Artifact / command | Producer | Consumer | Notes |
| --- | --- | --- | --- | --- |
| Skill source | `.agents/skills` in this repository | Playbook maintainers | All configured worktrees | One directory remains authoritative. |
| Codex / Copilot discovery | `<worktree>/.agents/skills` | `setup.sh` | Codex and GitHub Copilot | Direct symlink to the authoritative source. |
| Claude discovery | `<worktree>/.claude/skills` | `setup.sh` | Claude Code | Direct symlink to the same authoritative source. |
| Git exclusion | `git rev-parse --git-path info/exclude` | `setup.sh` | Git in the selected worktree | Explicit Git-local file; shared `.gitignore` is unchanged. |

## Generated argv replay

| Step | Execution location | argv | Required env | Expected artifact | Stop/continue |
| --- | --- | --- | --- | --- | --- |
| Preflight | playbook checkout | `git -C <worktree> rev-parse --show-toplevel` | POSIX shell and Git | Exact target worktree root | Stop if absent or mismatched. |
| Enable clients | playbook checkout | `./setup.sh <worktree>` | POSIX shell and Git | `.agents/skills` and `.claude/skills` symlinks | Stop before mutation on an existing conflicting path. |
| Verify behavior | playbook checkout | `python3 -m unittest tests.test_setup_sh` | Python 3 stdlib, POSIX shell, and Git | Passing integration-style tests | Stop on failure. |

## Producer/consumer consistency

| Producer | Artifact | Consumer | Required identity match | Result |
| --- | --- | --- | --- | --- |
| Playbook checkout | canonical `.agents/skills` directory | Both generated symlinks | Resolved link target equals the canonical directory | Pass by preflight and tests. |
| Git worktree discovery | worktree root and Git-path result | Link placement and exclude writer | Both belong to the explicitly selected worktree | Pass; nested targets are rejected. |

## Run-set / target / workflow identity consistency

| Identity | Producer value | Consumer value | Result |
| --- | --- | --- | --- |
| run set | Not applicable | Not applicable | Pass. |
| workflow id | `setup-workdir-skills` | README command and setup output | Pass. |
| target id / class | Canonical path of the explicit worktree argument | Link and exclude destinations | Pass. |

## Controller / target-local execution locations

| Step | Expected location | Actual/generated location | Result |
| --- | --- | --- | --- |
| Setup command | Playbook checkout | `setup.sh` resolves its own checkout independently of the current directory | Pass. |
| Skill discovery | Target Git worktree root | Worktree-local `.agents` and `.claude` paths | Pass. |

## Deployment/runtime discovery

| Runtime boundary | Install path | Invocation path | Env/PATH assumption | Preflight | Result |
| --- | --- | --- | --- | --- | --- |
| POSIX shell | Repository `setup.sh` | `./setup.sh <worktree>` | `/bin/sh` | Script shebang | Pass. |
| Git worktree | Target repository metadata | `git -C <worktree>` | `git` is on `PATH` | `rev-parse --show-toplevel` | Pass. |
| Agent clients | `.agents/skills`, `.claude/skills` | Client-native project discovery | No helper binary or modified `PATH` | Resolved symlink tests | Pass. |

## Forbidden fallback checks

- filename-order artifact selection: pass; no artifact search is used.
- mtime/latest/newest artifact inference: pass; both links name the source explicitly.
- stale prompt fallback: pass; configured clients read the source through live links.
- raw co-presence as causal evidence: pass; tests compare resolved link identity.

## Claim boundaries

- Workflow authority artifacts: `setup.sh` controls only skill discovery links and local Git exclusions.
- Validation artifacts: tests establish link, conflict, idempotency, target-root, and Git-status behavior.
- Measurement artifacts: none.
- Blocked claims: setup does not install or configure the clients themselves and does not copy `AGENTS.md` into target repositories.

## Findings

| ID | Severity | Finding | Required fix |
| --- | --- | --- | --- |
| none | none | No workflow contract findings. | None. |

## Decision

submit
