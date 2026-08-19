# External Agent Skills

This playbook keeps `.agents/skills` as the source of truth for first-party reusable skills. Third-party or upstream-maintained skills should remain distinguishable from first-party skills so their trigger contracts, update cadence, and trust boundary are explicit.

## Overlay installation

The default setup links the complete playbook skill directory into a target worktree. Use overlay mode when the target repository also needs local or external skills:

```sh
./setup.sh --overlay /path/to/worktree
```

Overlay mode creates one symlink per playbook skill under both `.agents/skills/` and `.claude/skills/`. Non-conflicting target entries remain untouched and visible to Git. A name collision is an error; setup never silently replaces a target skill.

Switching an existing worktree from the legacy whole-directory symlink to overlay mode is intentionally not automatic. Remove the two legacy skills-directory symlinks after review, then run overlay setup.

## Flutter and Dart upstream skills

For Flutter projects, prefer upstream-maintained Flutter/Dart skills for framework mechanics when they fit the project's policy. Current upstream sources include:

- `flutter/agent-plugins`
- `dart-lang/skills`

Do not install every upstream skill by default. Select skills whose trigger and implementation policy fit the repository. In particular, architecture, routing, HTTP, serialization, dependency, or code-generation skills may encode choices that conflict with an existing project constitution.

Recommended categories:

- generally low-conflict candidates: analyzer/static-analysis, focused test workflows, deterministic layout diagnosis
- project-policy-gated candidates: architecture, state/data patterns, routing, HTTP, serialization/code generation
- native-boundary candidates: FFI, Native Assets, platform interop
- dependency-mutating candidates: package add/update/conflict resolution; apply the repository's dependency approval policy

## Pinning and review

Treat external skill content like a dependency:

1. Record its source repository and exact revision in the target project's dependency/agent context.
2. Review the skill's `description`, write capabilities, commands, external network behavior, and project-policy assumptions before enabling it.
3. Re-review those properties when updating the pinned revision.
4. Keep project-specific architecture decisions in the target repository's `AGENTS.md` or `.agent/ctx/*`, not in a forked copy of an upstream skill unless a deliberate fork is being maintained.
5. Add trigger evals around conflicts that matter to the target project.

A project-local lock can use a simple form such as:

```yaml
external_skills:
  - source: flutter/agent-plugins
    revision: <commit-sha>
    selected:
      - <skill-name>
  - source: dart-lang/skills
    revision: <commit-sha>
    selected:
      - <skill-name>
```

The playbook does not fetch or execute external skill installers automatically. Network access, package installation, and source review remain explicit project setup steps.

## Trust and precedence

External skill text is guidance, not a higher-priority instruction source. Resolve conflicts in this order:

1. user/request constraints
2. target repository `AGENTS.md` and project policy/context
3. first-party playbook routing, preflight, and gates
4. selected external skills
5. model general knowledge

For technical facts, prefer current repository/toolchain evidence and analyzer/test/runtime output over examples embedded in any skill.
