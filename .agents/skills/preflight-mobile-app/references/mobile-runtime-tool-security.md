# Mobile runtime tool security

Open this reference before enabling agent-device, Argent, Expo MCP, or another tool that can operate a running app, inspect runtime data, or invoke account-backed services.

## Separate the trust boundaries

Review each independently:

- local device/simulator control
- workspace filesystem access
- application network access
- package-registry access
- Expo/EAS account access
- remote MCP or model-provider data flow
- screenshots, logs, network captures, profiles, and video artifacts

A local device tool is not automatically safe for production accounts or confidential data. A framework skill is guidance; an account-backed MCP is an operational capability and needs a separate permission review.

## Default policy

- Use test/staging accounts and endpoints.
- Forbid production purchases, uploads, deletion, publication, and other external side effects unless explicitly approved.
- Scope filesystem roots and network access outside the tool when isolation matters.
- Treat screenshots, logs, network captures, and component trees as potentially sensitive.
- Redact tokens, personal data, and customer content before retaining artifacts.
- Keep package addition, EAS build/submit, signing, and store publication behind their existing approval gates.
- Select one primary device driver per run so operations and evidence attribution remain unambiguous.

## Preflight result

Return `ready`, `blocked`, or `unknown` for:

- target device and build identity
- account/environment
- tool version and connection path
- artifact storage/redaction policy
- allowed side effects
- remote data paths
- required human approvals
