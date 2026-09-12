# AI Agent Instructions Playbook — contract-first edition

A breaking redesign for Astra-generation coding agents: a small working contract,
selectively installed specialist knowledge, and executable evidence tools. Ordinary work
may use **zero Skills**. The model chooses the method; the task and product define outcome,
authority, required quality and completion evidence.

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

For a new project, adapt `templates/AGENTS.md` with real commands and authorized execution
boundaries. Do **not** copy this repository's contributor `AGENTS.md`. Existing project
requirements and instructions remain authoritative within their proper scope.

## Profiles

| Profile | Specialists |
| --- | --- |
| core | repo-onboarding, decision-analysis, boundary-migration, workflow-contracts, bug-investigation-and-rca |
| embedded | target-discovery, embedded-runtime-evidence, runtime-performance, concurrency-verification |
| backend | auth-session, db-migration, runtime-performance |
| research | research-workflow, experiment-loop, research-synthesis |
| mobile | mobile-platform, mobile-verification, mobile-release, concurrency-verification |
| ui | ui-design, ui-verification |
| authoring | playbook-authoring, lessons-learned, japanese-tech-writing |

Descriptions are selection boundaries, not an always-on workflow. References and scripts
are used only for the decision they address. The UI profile retains seven style/token
families and executable preview assets. Specialist scripts travel with their Skill.
Bundled research-ledger scripts remain optional project-level tools; see the research
Skills' references before adopting their machine format.

## Quality without ceremony

Preserve safety/security/privacy, data integrity, external obligations and required checks.
Derive quality from use, failure impact, workload, expected changes and recovery conditions.
Required-but-unverified is not complete; an optional improvement may remain unmet. Reuse
proof only while candidate, target, workload, configuration and method still support it.
Use `docs/quality-contract.md` when requirements are unresolved, not as a per-edit checklist.

Ordinary development has no compulsory router, final-gate Skill, role roster, function
ledger, report pack, retry count or universal performance/structure threshold. A concrete
failure still requires correction and appropriate regression proof. Informative debugging
continues within authority; uninformative repetition changes approach.

## Breaking migration

Retired Skill names, aggregate links, `--overlay`, generated indexes and model-routing configs
remain retired without aliases or fallbacks. `bug-investigation-and-rca` is intentionally rewritten in place as a lightweight evidence contract, not restored as the old procedural workflow. Inspect and explicitly remove/relocate old
playbook-owned links before installing; the installer will not guess ownership. Update
project instructions that invoke retired names. `docs/skill-disposition.json` accounts for
all 67 old entrypoints and their replacement or retirement. The 22 current entrypoints
are a design choice, not a measured optimal number.

Old plans/reports/experiments and run evidence remain historical, not active guidance.
The research evidence schema stays readable because preserving experiment provenance is
not compatibility with the retired Skill workflow. No downstream product API/data waiver
is implied by this playbook's breaking release.

## Contributor verification

```sh
make verify
```

This runs catalog/reference validation, Python syntax checks, the preserved research-ledger
integrity check, and real unit/integration regressions. CI runs the same command. There is
no separate generated-index gate or substring rubric for model behavior.

Live model evaluation is separate: `evals/README.md` describes matched baseline/minimal/
selective arms, executable task oracles and pending trace review. **Live Astra A/B trials
have not been run for this redesign.** Tool tests are not model capability evidence.

See `docs/astra-redesign.md` for boundaries, evaluation limits and the source rationale.
