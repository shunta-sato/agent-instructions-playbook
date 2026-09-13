# AI Agent Instructions Playbook — contract-first edition

A breaking redesign for Astra-generation coding agents: a working contract, selectively
installed specialist knowledge, and executable evidence tools. Ordinary small work may
use **zero Skills**. The model chooses implementation methods; the requester and project
define outcome, authority, required quality and completion evidence. Substantial delivery
starts with human alignment and a demonstrated verification path, not blind autonomy.

## Install only what the project needs

Python 3.11+, Git and a POSIX system are required for the installer/tests. No Python
third-party packages are required. Check out a reviewed revision, then run:

```sh
./setup.sh --list
./setup.sh /path/to/project --profile core --profile embedded --dry-run
./setup.sh /path/to/project --profile core --profile embedded
./setup.sh /path/to/project --skill ui-design --skill ui-verification --client both
```

With no selection, only `core` is installed. An explicit profile/skill selection replaces
the managed selection; repeat `--profile core` to include it. `codex` installs native
`.agents/skills` entries (also usable by clients supporting that location), `claude` uses
`.claude/skills`, and `both` uses both. Client discovery must be supported by the installed
runtime; this repository does not choose a model or guarantee other models' behavior.

The installer links current Skills and records ownership in `.playbook-install.json`.
It refuses unmanaged collisions, edited managed paths and legacy whole-directory symlinks;
it does not delete project-owned files, copy contributor instructions, change credentials,
or edit Git configuration/ignore rules. Review/ignore the generated links and ownership
file according to your project's policy. Keep the manifest local with its matching links.
A source checkout update changes linked Skills; pin a revision for reproducibility.

Adapt `templates/AGENTS.md` with real commands, authorized execution boundaries, acceptance
requirements and escalation contacts. Installation alone does not update an existing
project's instructions. Remove retired workflow mandates while preserving local requirements.
Do **not** copy this repository's contributor `AGENTS.md` into a consumer project.

## Profiles

| Profile | Specialists |
| --- | --- |
| core | repo-onboarding, decision-analysis, boundary-migration, workflow-contracts, bug-investigation-and-rca, preflight-engineering, agentic-tdd |
| embedded | target-discovery, embedded-runtime-evidence, runtime-performance, concurrency-verification |
| backend | auth-session, db-migration, runtime-performance |
| research | research-workflow, experiment-loop, research-synthesis |
| mobile | mobile-platform, mobile-verification, mobile-release, concurrency-verification |
| ui | ui-design, ui-verification |
| authoring | playbook-authoring, lessons-learned, japanese-tech-writing |

Profiles make Skills available; they are not execution sequences. Descriptions are selection
boundaries. References and scripts are used only for the decision they address. The UI profile
retains seven style/token families and preview assets. Specialist scripts travel with their
Skill. Bundled research-ledger tools remain optional project-level tools; see their references.

## Entry, human alignment and E2E

Start from the request plus the project working contract. Before substantial dependent work,
align on the user's outcome, acceptance/E2E boundary, NFRs and allowed execution/actions.
Reuse prior answers. Ask only for material unresolved decisions, with the impact and a bounded
recommendation; silence is not consent. Continue independent authorized work without making
up a missing requirement or asking permission for every ordinary command.

`preflight-engineering` is a rewritten human-communication and readiness Skill, not the old
full-repository preparation workflow. Demonstrate start/drive/observe/reset for the necessary
verification path early. A greenfield task can first build a minimal executable slice. Reuse
valid readiness evidence and revisit affected changes. `repo-onboarding` only repairs missing
repository facts; knowing an execution command does not prove the environment works.

`agentic-tdd` puts executable acceptance/E2E outside a focused UT/integration loop for
user-visible runtime delivery and explicit TDD. Environment failure is not feature Red;
UT success, no-tests/all-skipped, screenshots or a healthy process are not E2E Green.
Use the appropriate public boundary for pure library/static work instead of manufacturing an
unnecessary UI/system test. Required performance/physical claims need their own evidence.

Fix environment gaps inside granted authority. Raise missing access, real targets or material
requirements when discovered, not at submission. Do not bypass denial through a different
tool/host/CI/agent, search for credentials, disable security or weaken assertions. A separately
approved alternative is allowed; it cannot silently broaden what the evidence claims.
Partial work may be shared in a Draft PR but is not a completed feature with required E2E missing.
These duties live in the common contract too, so missed Skill selection does not waive them.

## Quality without ceremony

Preserve safety/security/privacy, data integrity, external obligations and required checks.
Derive quality from use, failure impact, workload, expected changes and recovery conditions.
Required-but-unverified is not complete; an optional improvement may remain unmet. Reuse
proof only while candidate, target, workload, configuration and method still support it.
Use `docs/quality-contract.md` when requirements are unresolved, not as a per-edit checklist.

No compulsory generic delivery router, final-gate Skill, role roster, function ledger, report
pack, retry count or universal performance/structure threshold. This does not remove real
sequencing dependencies: unresolved material agreement or unavailable required verification
must not be ignored while dependent implementation accumulates. Informative debugging
continues within authority; uninformative repetition changes approach.

## Breaking migration

Retired Skill names, aggregate links, `--overlay`, indexes and model-routing configs remain
retired without aliases or fallbacks. `bug-investigation-and-rca` and `preflight-engineering`
are intentionally rewritten in place; `test-driven-development` maps to `agentic-tdd`.
Their former fixed workflows and report obligations are not restored. Inspect and explicitly
remove/relocate old playbook-owned links before installing; ownership is never guessed.
`docs/skill-disposition.json` accounts for all 67 old entrypoints. The 24 current entrypoints
are a design choice, not a measured optimal number.

Old plans/reports/experiments and run evidence remain historical, not active guidance.
The research evidence schema stays readable because preserving experiment provenance is
not compatibility with the retired workflow. No downstream product API/data waiver is implied.

## Contributor verification

```sh
make verify
```

CI runs the same catalog/reference/syntax validation, research-ledger integrity check and
unit/integration regressions. New preflight fixtures exercise an actual CLI across processes,
including missing environment, meaningful acceptance failure and persistence. Those fixture
tests do not prove that a model asks questions at the right time or respects authority.

`evals/README.md` describes matched baseline/minimal/selective arms, task oracles and pending
trace/communication review. **Live Astra A/B trials have not been run for this redesign.**
See `docs/astra-redesign.md` for boundaries, evaluation limits and the source rationale.
