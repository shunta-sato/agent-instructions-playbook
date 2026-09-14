# Preflight Console — local dialogue prototype

Discuss the agent's questions before deciding. The conversation sits beside an editable
agreement, with an explicit distinction between proposals, human content confirmation,
execution permission and verification evidence. This app is optional; Skill setup never
installs browser dependencies, starts a server or invokes a model.

**Scope:** one local user, one conversation per state directory, discussion and a JSON
handoff. No project editor, terminal, automatic environment preparation, production access,
CLI approval forwarding, cloud/team service or attachment to an arbitrary running CLI.
Python 3.11+, a POSIX host and a modern browser are required. Runtime Python dependencies
are standard-library only. Do not expose this loopback service publicly.

## Start without credentials or model usage

From the repository root:

```sh
python3 -m apps.preflight_web.server --provider demo --port 8765
```

Open the printed `http://127.0.0.1:8765/#token=...` URL. The fragment is removed immediately
and the token is kept in that tab's sessionStorage, not sent in the HTTP request target.
Treat the URL as a local session key: never post it in issues, logs or screenshots.
Restart creates a new token; open the newly printed URL. `--port 0` selects a free port.
The default state directory is `~/.local/state/playbook-preflight`, outside the repository.
Use `--state-dir /private/path` for a separate conversation.

The **demo is deterministic, not an AI**. It provides labelled why-question and local-only
examples; there are no model calls, fees, credentials or silent live-to-demo fallback.

1. Describe the feature, then ask `なぜこの質問が必要？` instead of selecting a number.
2. Say `ローカルのみ。CI・本番は触らないで` and inspect the proposed change.
3. Take the proposal into the editor, correct it, and save the draft.
4. Review the exact displayed version before confirming it and downloading the JSON handoff.

A confirmed handoff always says `execution_authorized: false` and
`verification_status: not-run`. It records reviewed content, not organizational authority,
a capability, execution readiness or E2E success. A downstream agent must verify applicable
policy, authority and the actual verification environment before acting.

## Stop a response, then continue the discussion

While waiting, use **応答を止めて相談に戻る**. The server binds cancellation to the displayed
revision and exact turn, waits for provider cleanup, and only then permits another message.
A reply or failure arriving from an older turn cannot complete or interrupt a newer one.
The interrupted question stays visible as context, not as work to retry automatically.
No answer, draft or content confirmation becomes an execution grant.

The Codex adapter ends only its own child process group when cancelled. It does not kill an
unrelated CLI, approve a pending tool request or weaken permissions. On the next explicit
message, it starts a new native thread using saved conversation/draft context. This is not
native thread resumption or rollback of model-side usage. A normal uninterrupted dialogue
keeps its existing native thread. Token streaming and mid-turn steering remain unimplemented.

## Keep edits through conflicts and reconnects

Unsent text and unsaved agreement edits are kept in sessionStorage for this tab, keyed by
the persistent database identity, not the access token. A reload on the same origin restores
them without sending or saving. The browser warns before navigating away with draft edits.
This recovery is tab/origin-local: closing the tab, clearing site storage, or changing the
port can lose unsaved work. The server's saved transcript and draft persist independently.
Neither the token nor local recovery storage is multi-user authentication.

When another tab updates the draft, your text is not overwritten. **最新との差分を確認**
shows the starting value, latest saved value and your edited value for changed fields only.
After explicit review, **表示した差分を保存** reapplies those fields against that exact
revision, preserving fields you did not edit. A newer write while the dialog is open causes
another conflict, not a silent overwrite. Discarding local edits requires confirmation.
Human draft changes retire model proposals based on the older draft.

Network errors disable mutations until reconnect and preserve the input; requests are not
automatically retried. When a write's response is lost, inspect the latest transcript/history
before resending: the server may already have accepted it. Content confirmation is invalidated
by new discussion or a changed draft. Refresh alone never approves or invalidates content.

## Experimental Codex connection

An App Server adapter is implemented, but **real Codex binary/login/model compatibility is
not yet verified**. Wire fixtures test this client's protocol handling, not model behavior
or the runtime's enforcement. No real Codex executable is available in the development
container used for this follow-up. Model trials require explicit operator authorization.

Use a separately provisioned dedicated Codex login home and a reviewed binary/model:

```sh
python3 -m apps.preflight_web.server \
  --provider codex \
  --codex /absolute/path/to/reviewed/codex \
  --codex-home /absolute/path/to/dedicated-login-home \
  --model YOUR_EXPLICIT_MODEL_ID \
  --live-sandbox-confirmed
```

Provision credentials using the approved login process, never through this UI. The app does
not copy credentials. It refuses a home containing config, instructions, Skills, plugins or
rules; do not strip your normal development profile to satisfy that check. The explicit
model must match the identity returned by `thread/start`; missing identity also fails closed.

`--live-sandbox-confirmed` is an acknowledgement, **not a sandbox**. Independently confine
the runtime, keep the SQLite database outside its readable roots, expose no production
credentials, and limit network access to approved model transport. The conversation/draft
is sent to the chosen provider and may consume a subscription allowance or incur charges.

The adapter requests read-only/restricted-read operation, disables shell/unified exec,
apps/plugins/multi-agent/search, and rejects unexpected approval/input requests. Runtime
rejections, substitution, unsupported messages and deadline expiry fail without weakening
policy or switching providers. Ignored runtime settings cannot be detected by a fake server;
validate effective enforcement with the reviewed runtime and external isolation.

Protocol references consulted 2026-09-13:
- https://developers.openai.com/codex/app-server/
- https://developers.openai.com/codex/config-reference/

## State and local security

SQLite owns revisions, turn identities, proposals and content-confirmation snapshots.
All six agreement fields must be nonempty to confirm; unresolved facts may be explicit text.
This is structural validation, not proof of truth, completeness, identity or authority.
A pending turn found at startup is interrupted, never automatically replayed.

The server binds only to loopback, checks Host/Origin, uses bearer-authenticated JSON state
APIs, a static-asset allowlist and CSP, and renders model/user content as text rather than
HTML. It has no arbitrary file/command endpoint. Same-port restart is supported without
allowing multiple listeners. There are request/turn limits and a single-server state-dir lock.
Local state is plaintext SQLite (0600, state directory 0700), not encrypted. It is not isolated
from other processes with the same OS account or token. Never enter production secrets.
The local owner manages retention/deletion after stopping the server.

## Verification

The repository's `make verify` runs the standard-library HTTP, SQLite and wire fixtures,
including cancellation races, rejected stale actions and persistence. These are not live AI
or browser HTTP E2E. Focused checks from the repository root:

```sh
python3 -m unittest discover -s tests -p 'test_preflight_*.py' -v
```

Browser checks have optional, pinned dependencies. Use a dedicated environment:

```sh
python3 -m venv /tmp/preflight-browser-venv
/tmp/preflight-browser-venv/bin/pip install -r apps/preflight_web/requirements-test.txt
/tmp/preflight-browser-venv/bin/python -m playwright install chromium
/tmp/preflight-browser-venv/bin/python apps/preflight_web/tests/browser_e2e.py \
  --screenshots /tmp/preflight-browser-evidence
```

Run only in an explicitly approved browser verification environment. The browser's required
system libraries must already be available or installed through an authorized setup process.
By default the E2E uses the matching Playwright browser; `CHROMIUM_PATH` selects an explicitly
reviewed installed Chromium. Neither missing dependencies nor denied navigation is a pass.
The E2E exercises actual HTTP/SQLite, two-tab conflicts, stale confirmations, JSON download,
text rendering, native sessionStorage restoration, server restart and cancelled discussion.
The cancellation stage uses a **test-only deterministic slow provider**, not a real model.

In this development container, loopback navigation was denied with
`ERR_BLOCKED_BY_ADMINISTRATOR`; policy was not changed or bypassed. **Browser HTTP E2E remains
blocked/unpassed here.** Its code is supplied for an approved environment; there is no new CI
job that relocates the denied operation. A distinct component check runs without that route:

```sh
python3 apps/preflight_web/tests/offline_ui.py --screenshot /tmp/preflight-component.png
```

It uses the shipped HTML/CSS/JS and shared UI journeys, with an in-process transport and
simulated sessionStorage. Its success does not validate real HTTP from the browser, native
storage persistence, CSP/Origin enforcement or a live model. Real HTTP tests cover the server
separately; no combination of partial results is labelled full E2E.

Before treating the Console as a working replacement for CLI preflight, exercise both the
real browser E2E and a separately authorized live Codex dialogue. Execution-readiness actions,
trusted-executor integration, CLI resumption, Claude/Copilot adapters and multi-user hosting
remain outside this local discussion prototype.
