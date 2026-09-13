# Preflight Console — local prototype

Ask questions about the agent's questions, correct premises and inspect the agreement
next to the conversation. This app is optional: installing Skills never starts it.
Python 3.11+, a POSIX host and a modern browser are required. The server uses only the
standard library; browser tests additionally need Playwright and Chromium.

**Scope:** one local user, one conversation per state directory, discussion and explicit
content confirmation, then a downloadable handoff. No shell/terminal, project editor,
production connection, automatic environment setup or forwarding of execution approvals.
It does not attach to an arbitrary running CLI. Do not expose it as a public/team service.

## Try the offline walkthrough

From the repository root:

```sh
python3 -m apps.preflight_web.server --provider demo --port 8765
```

Open the `http://127.0.0.1:8765/#token=...` URL printed by the server. The access token
stays in the URL fragment (not in an HTTP request target), is then removed from the URL,
and lives in that tab's sessionStorage. Treat the printed URL as a local session key.
Do not put it in issues/screenshots. A server restart creates a new token; use its new URL.
Use `--port 0` for an OS-assigned port. Use a separate `--state-dir /private/path` for a
new conversation. The default is `~/.local/state/playbook-preflight` (outside the repo).

The **demo is deterministic, not an AI**. It demonstrates a why-question and a proposal
containing "ローカル". All other input receives a clearly labelled walkthrough reply.
There is no network/model use in demo mode and no silent fallback from live mode to demo.

Try this flow:

1. Describe a feature, then ask `なぜこの質問が必要？` instead of choosing a number.
2. Say `ローカルのみ。CI・本番は触らないで` and inspect the proposed environment change.
3. Bring the proposal into the editor, correct the fields, and save the draft.
4. Review the exact version in the confirmation dialog, confirm it, and export a handoff.

Chat, proposed changes and saved drafts never confirm an agreement. Confirmation records
only that the local user reviewed the displayed content. The handoff explicitly says
`execution_authorized: false` and `verification_status: not-run`. It is not a capability,
release proof or permission token. The downstream agent must check project policy,
identity/authority, material unknowns and actual verification readiness before acting.

## Experimental Codex connection

The adapter is implemented against the official App Server JSONL protocol but **has not
been tested with a real Codex binary/login/model**. Its protocol fixture tests are not
compatibility or safety evidence. Keep this mode in an operator-controlled sandbox until
its effective policy and wire schema are verified against a pinned installed version.

Provision a dedicated Codex login home yourself using your organization's approved login
process; pass it explicitly. The app does not copy credentials from other profiles or
accept secret values through the browser. It refuses a dedicated home containing config,
AGENTS, Skills, plugins or rules, rather than guessing how to neutralize inherited tools.
Do not remove your normal profile configuration to make this check pass.

```sh
python3 -m apps.preflight_web.server \
  --provider codex \
  --codex /absolute/path/to/reviewed/codex \
  --codex-home /absolute/path/to/dedicated-login-home \
  --model YOUR_EXPLICIT_MODEL_ID \
  --live-sandbox-confirmed
```

`--live-sandbox-confirmed` is an operator acknowledgement, **not a sandbox**. Confine the
runtime independently, keep the console's database outside its readable roots, expose no
production credentials, and limit network to the approved model transport. The supplied
chat/draft is sent to the chosen model and may incur usage charges or plan consumption.
Neither this task nor the demo command authorizes a live model trial automatically.

The adapter uses initialize/initialized, thread/start, turn/start with outputSchema, and
item/turn completion events. It requests read-only/restricted-read sandboxing, disables
shell/unified-exec/apps/plugins/multi-agent/search, and rejects unexpected server requests
for tool approval/input rather than auto-answering them. A runtime rejection of settings/protocol,
transport failure, model substitution reported by thread/start, and deadline expiry fail
closed without retrying under a weaker policy. These requests are defense in depth; silently ignored configuration is not detectable
by these fixture tests. Actual enforcement belongs to the reviewed runtime and the
operator's sandbox.

A running server keeps one native Codex thread. Browser reload preserves it. After server
restart or transport failure, a new native thread is created and receives the saved local
transcript/draft; it does not claim native thread resumption or replay unfinished work.
Token streaming and mid-turn steering are not implemented; each discussion turn has a
180-second deadline. A blocked tool/input request fails that turn instead of becoming a
numeric modal. No arbitrary executable/model/working-directory is accepted from HTTP.

Sources consulted on 2026-09-13:
- https://developers.openai.com/codex/app-server/
- https://developers.openai.com/codex/config-reference/
- https://github.com/openai/codex/blob/main/codex-rs/app-server-protocol/schema/json/v2/ThreadStartParams.json

## State and authority boundaries

The browser edits a draft; the provider only returns `reply` and proposed field changes.
The SQLite store owns confirmation records, revision numbers, snapshots and history.
Each change/confirmation is compare-and-swap against the displayed revision. A stale
confirmation, stale editor, busy turn or missing confirmation cannot produce a handoff.
The MVP conservatively invalidates confirmation after any new discussion or draft edit.
Refresh/reconnect alone does not confirm or invalidate anything. A pending turn found at
server startup becomes interrupted; it is never automatically resubmitted.

All six fields must be nonempty to confirm a content snapshot. Unresolved facts can be
written explicitly. This is structural validation, not proof that the statements are
true or that their author has organizational approval authority. AI proposals can be
wrong; the person reviews them. There is no universal mandatory form for ordinary CLI
work and no new requirement to use this UI for every task.

Loopback bind only; exact Host/Origin checks; bearer authentication for all state APIs;
JSON-only writes; no CORS; static asset allowlist; CSP; no HTML/Markdown execution from
messages; request-size/turn-time limits; single-server state-dir lock. Chats, proposals
and changes are stored locally in plaintext SQLite (0600, directory 0700), not encrypted.
No transcripts/tokens are logged by default. The startup URL, browser storage, local
files and live Codex credential home are sensitive. This MVP does not isolate against
another process/user with access to the same OS account or token, and is not multi-user
authentication. Do not put production secrets in the conversation. Retention/deletion
is by the local owner after stopping the server; there is no remote deletion endpoint.

## Verification and what is still blocked

Canonical non-browser checks (also discovered by the repository's `make verify`):

```sh
python3 -m unittest discover -s tests -p 'test_preflight_web.py' -v
python3 -m unittest discover -s tests -p 'test_preflight_codex.py' -v
```

The tests exercise real HTTP requests, SQLite persistence, discussion-to-handoff,
proposal/confirmation separation, stale writes/confirmations/exports, policy checks and
Codex wire-protocol fixtures. They do not call a model or provision an environment.

With a reviewed Playwright installation and Chromium available (set `CHROMIUM_PATH` when
needed), run the **full browser HTTP E2E** in a permitted local verification environment:

```sh
python3 apps/preflight_web/tests/browser_e2e.py --screenshots /tmp/preflight-browser-evidence
```

This starts the real server, drives the shipped UI, asks why, corrects a proposal, tests a
stale approval from another tab, confirms and downloads the handoff, checks HTML-as-text,
and restarts the server to verify persistence. It uses the labelled demo provider only.
Missing browser/runtime or denied navigation fails the command; it is never an E2E pass.

During development here, Chromium launched, but browser navigation to loopback HTTP was
rejected with `ERR_BLOCKED_BY_ADMINISTRATOR`. That policy was not modified or bypassed.
**The full browser HTTP E2E is blocked/unpassed**, not covered by the passing HTTP tests.
A narrower offline UI/component check is provided separately:

```sh
python3 apps/preflight_web/tests/offline_ui.py --screenshot /tmp/preflight-ui.png
```

That check loads the shipped markup/styles/script in a browser and uses an in-process
fixture transport. It verifies UI interactions/layout, but is **not** browser HTTP E2E,
origin/CSP verification or a live-model trial. The PR remains draft until the actual E2E
path and a separately authorized real Codex dialogue have been exercised. Do not move an
administratively denied operation to another host or weaken browser policy to get a pass.

## Next boundary, not hidden scope

Before adding "start verification", specify the trusted executor, allowed target/actions,
revocation/expiry semantics, how it verifies the exact human-approved scope, and evidence
identity. Do not turn this content-confirmation button into a generic execution grant.
Bidirectional CLI handoff/resumption, execution-readiness evidence ingestion, Claude/Copilot
adapters, shared accounts, cloud hosting and multi-user permissions are not implemented.
