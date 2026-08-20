# Dart and Flutter MCP security

Use this reference when `preflight-mobile-app` detects or proposes Dart/Flutter MCP.

## Data-flow model

Treat these as separate trust boundaries:

```text
AI client <-> Dart/Flutter MCP (stdio)
                  |
                  +-> local Dart/Flutter CLI
                  +-> local analyzer/LSP
                  +-> local DTD / VM service / running app
                  +-> explicit package-network tools when enabled

AI client <-> cloud LLM/provider (client policy and contract dependent)
```

The MCP server is primarily a local tooling bridge. That does not imply an end-to-end local-only workflow: the AI client may send selected source, diagnostics, logs, widget information, screenshots, or tool results to its configured model service.

## Confidential-code defaults

For confidential repositories, prefer all of the following unless project/company policy explicitly says otherwise:

- suppress Dart tooling analytics for the MCP process
- disable package-network/search capabilities unless needed
- mount only the project/workspace and required SDK/cache paths into the agent sandbox
- do not mount SSH keys, cloud credentials, signing keys, keystores, service-account credentials, or unrelated home-directory data
- use test/staging accounts and non-production endpoints for UI automation
- do not enable MCP protocol traffic logging by default
- review screenshots, runtime logs, and widget text as potentially sensitive data
- enforce network egress outside MCP; MCP feature selection alone is not a network sandbox

Candidate invocation for a confidential environment, subject to the installed MCP server's actual `--help` output:

```sh
dart --suppress-analytics mcp-server --disable package_deps
```

Never copy this command into a canonical command file without verifying support in the pinned Dart/Flutter SDK.

## Roots are not access control

MCP roots communicate relevant workspace locations to the server and tools. They are not a filesystem security boundary.

Do not conclude that files outside a configured root are unreachable. If that property is required, enforce it with OS permissions, container/sandbox mounts, namespaces, or equivalent runtime isolation.

## Network-capable surfaces

Classify separately:

- package search against public/private registries
- `pub get`, add, upgrade, or Git dependencies
- the running application's own API/analytics/crash-reporting traffic
- the AI client's model-provider traffic
- any SDK/tool telemetry

A local analyzer operation is materially different from a package search or application API call. Policy should permit them independently.

## UI automation safety

Tap, text input, scroll, screenshots, and runtime inspection can cause application side effects or expose user data. Prefer:

- debug/test builds
- test identities
- seeded test data
- staging/fake backend
- explicit blocks on payment, deletion, publication, or irreversible production operations

Production endpoints or real customer data require explicit project policy and approval.

## Preflight record

Record:

- MCP server/version source: confirmed | inferred | unknown
- transport: stdio | other | unknown
- cloud model data path reviewed: yes | no | unknown
- analytics suppressed/disabled: yes | no | unknown
- package-network tools: enabled | disabled | unknown
- workspace filesystem isolation: enforced | not-enforced | unknown
- production credentials mounted: no | yes-with-approval | unknown
- UI automation environment: local-test | staging | production-with-approval | unknown
- protocol log enabled: no | yes-with-retention-policy | unknown

Do not record secret values.
