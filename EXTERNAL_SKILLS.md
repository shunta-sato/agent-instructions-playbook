# External Agent Skills

This playbook keeps `.agents/skills` as the source of truth for first-party reusable skills. Third-party or upstream-maintained skills remain distinguishable so their triggers, update cadence, commands, policy assumptions, and trust boundary are explicit.

## Overlay installation

Use overlay mode when a target repository also needs local or external skills:

```sh
./setup.sh --overlay /path/to/worktree
```

Overlay mode creates one symlink per playbook skill under `.agents/skills/` and `.claude/skills/`. Non-conflicting target entries remain untouched; name collisions are errors. Switching from a whole-directory symlink is intentionally not automatic.

## Framework-maintained skill sources

Select upstream skills for framework mechanics only when they fit project policy. Current source categories include:

- Flutter/Dart: `flutter/agent-plugins`, `dart-lang/skills`
- React Native/Expo: `expo/skills`
- React Native diagnostics/performance: reviewed skills from `callstackincubator/agent-skills`
- Device runtime operation: reviewed agent-device skills/configuration from its upstream source

Do not install every upstream skill by default. Architecture, routing, data fetching, HTTP, serialization, project structure, dependency, native-module, EAS, and store skills can encode choices or operational capabilities that conflict with the target repository.

Recommended selection classes:

- low-conflict candidates: focused analyzer, test, or deterministic diagnosis workflows
- project-policy-gated: architecture, state/data patterns, routing, HTTP, serialization, project structure
- native-boundary: Expo/native modules, FFI, JSI/TurboModule, platform interop
- dependency-mutating: package add/update/conflict resolution
- account/side-effect capable: EAS build/submit, store operations, remote MCP, device automation against non-test systems

## Skills are not MCP permissions

Framework skill text is guidance. MCP servers, device drivers, Expo/EAS account access, package-network access, screenshots/logs/network captures, signing, and store publication are operational capabilities and require separate preflight and approval.

In particular:

- enabling selected Expo skills does not imply enabling Expo MCP
- enabling agent-device guidance does not authorize production accounts or side effects
- remote services and local runtime tools must document data paths, credentials/account scope, retained artifacts, and approval boundaries

Use `preflight-mobile-app` before enabling account-backed or runtime-operating mobile tools in a confidential or production-adjacent project.

## Pinning and review

Treat external skill content like a dependency:

1. Record source repository and exact revision.
2. Review description, write capabilities, commands, network behavior, account access, and policy assumptions.
3. Re-review on revision updates.
4. Keep project architecture in target `AGENTS.md` or `.agent/ctx/*`, not a casual upstream fork.
5. Add trigger/behavior evals around conflicts that matter.
6. Keep selected skills and operational MCP/tool permissions in separate lock/policy fields.

Example:

```yaml
external_skills:
  - source: expo/skills
    revision: <commit-sha>
    selected:
      - <skill-name>
  - source: callstackincubator/agent-skills
    revision: <commit-sha>
    selected:
      - <skill-name>

runtime_tools:
  agent_device:
    revision: <version-or-commit>
    production_access: false
    allowed_targets: [android-emulator, ios-simulator]
  expo_mcp:
    enabled: false
```

The playbook does not fetch or execute external installers automatically. Network access, package installation, source review, account connection, and permissions remain explicit project setup steps.

## Trust and precedence

Resolve conflicts in this order:

1. user/request constraints
2. target repository `AGENTS.md` and project policy/context
3. first-party playbook routing, preflight, and gates
4. selected external skills
5. model general knowledge

For technical facts, prefer current repository/toolchain evidence and analyzer/test/runtime output over examples embedded in any skill.
