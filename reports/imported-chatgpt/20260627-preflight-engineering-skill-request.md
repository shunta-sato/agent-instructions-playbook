以下を、そのままCodexへの依頼文として使える形でまとめます。設計根拠は、Codexが `AGENTS.md` を作業前に読み、ルートから作業ディレクトリへ向かって結合すること、Skillsがprogressive disclosureで読み込まれること、Subagentが明示依頼時だけ起動され各自トークンを消費すること、Prompt Cachingが先頭からの完全一致prefixに依存することです。 [OpenAI Developers + 3 OpenAI Developers + 3 OpenAI Developers + 3](https://developers.openai.com/codex/guides/agents-md)

# Codex依頼書: `preflight-engineering` Skill を開発する

## GOAL

`preflight-engineering` というCodex Skillを作成してください。

このSkillの目的は、長時間のAgentic Developmentを始める前に、リポジトリ内の `AGENTS.md` 、Agent向け短縮ドキュメント、Skill逆引き、テスト経路、禁止事項、Subagent分業方針、開発総指揮Agentへのhandoff promptを整備することです。

このSkillは、実装作業そのものを行うためのものではありません。実装Agentが迷わず、安全に、少ない再探索で、Prompt Cachingが効きやすい形で作業を始められるように、作業環境を整えるためのSkillです。

## 背景

Codexは、作業開始時に `AGENTS.md` などのinstruction filesを読み込みます。リポジトリルートから現在の作業ディレクトリまで順に探索し、近いディレクトリの指示ほど後ろに置かれます。合計サイズは `project_doc_max_bytes` で制限され、デフォルトは32 KiBです。したがって、 `AGENTS.md` には長大な説明ではなく、短く安定した作業契約と参照先を置くべきです。 [OpenAI Developers](https://developers.openai.com/codex/guides/agents-md)

Codex Skillsは、最初から全文がすべてcontextに入る設計ではありません。CodexはまずSkillの `name` 、 `description` 、file pathを読み、必要だと判断したときに `SKILL.md` 全文を読みます。初期Skill一覧にはcontext windowの2%または8,000文字の予算があるため、Skillのdescriptionは短く、trigger語を前方に置く必要があります。 [OpenAI Developers](https://developers.openai.com/codex/skills)

Subagentは複雑な調査や並列レビューに有効ですが、各Subagentが独自にmodelとtoolを使うため、同等のsingle-agent runより多くのtokenを消費します。したがって、Subagentを使う前に、共通文脈、参照先、禁止事項、出力形式を固定しておく必要があります。 [OpenAI Developers](https://developers.openai.com/codex/subagents)

Prompt Cachingは、promptの先頭から続く完全一致prefixに対して働きます。静的な指示、例、tools、schemaなどを前方へ置き、ユーザー固有情報、ログ、検索結果、今回だけの観測結果を後方へ置く必要があります。OpenAIのCookbookでは、Prompt Cachingは1024 tokens以上のpromptで自動的に働き、cache hitは128 tokens単位で発生し、入力tokenコストを最大90%、time-to-first-tokenを最大80%下げ得ると説明されています。ただし、実際の削減率はワークロードとcache hit率に依存します。 [OpenAI Developers + 1](https://developers.openai.com/api/docs/guides/prompt-caching)

## Skill名

`preflight-engineering`

## Skillの保存先

リポジトリ内Skillとして作成してください。

```
.agents/skills/preflight-engineering/SKILL.md
```

Codexはリポジトリ内では、現在の作業ディレクトリからリポジトリルートまでの `.agents/skills` を探索します。Skill directoryには `SKILL.md` が必要で、 `SKILL.md` には `name` と `description` を含める必要があります。 [OpenAI Developers](https://developers.openai.com/codex/skills)

## Skill descriptionの要件

`description` は、implicit invocationで選ばれやすいように、trigger語を先頭に置いてください。

推奨description:

```
description: Preflight, AGENTS.md, agent context, skill routing, test routing, subagent handoff, prompt caching readiness. Use before long-running, multi-agent, unfamiliar, high-risk, or cross-service coding tasks. Do not use for small one-file edits.
```

## Non-goals

このSkillは、プロダクト実装を直接行わないでください。

このSkillは、以下を行いません。

- バグ修正そのもの
- feature実装そのもの
- 破壊的変更
- 本番設定変更
- secret、credential、tokenの表示
- 依存関係追加
- migration実行
- deploy実行
- 長い人間向けドキュメントの全文生成
- すべてのSkill本文を `AGENTS.md` へ貼ること
- lintやformatterで検出できるstyle ruleの列挙

このSkillは、調査、整理、提案、短縮ドキュメント作成、handoff prompt作成に集中します。

## 成果物

初回実装では、少なくとも以下を作成してください。

```
.agents/skills/preflight-engineering/
  SKILL.md
  references/
    agents-template.md
    agent-ctx-template.md
    skill-map-template.md
    handoff-prompt-template.md
    cache-readiness-checklist.md
```

可能なら、後続改善として以下も追加できる構成にしてください。

```
.agents/skills/preflight-engineering/
  scripts/
    inspect_repo.py
    estimate_context_size.py
    check_agent_docs.py
```

ただし、初回版ではscriptsを必須にしないでください。まずはinstruction-only Skillとして成立させてください。

## Preflight Engineeringの定義

Preflight Engineeringとは、開発Agentを走らせる前に、リポジトリの作業地図を作る工程です。

この工程では、以下を明確にします。

- 何を守るべきか
- 何を見ればよいか
- どのSkillを使えばよいか
- どのテストを走らせればよいか
- どの変更は人間承認が必要か
- Subagentを使うなら、誰が何を調査するか
- 開発総指揮Agentへ何を渡せばよいか
- Prompt Cachingを壊しにくい文脈配置になっているか

## 対象タスク

このSkillは、次のような作業前に使います。

- 初めて触るリポジトリでの開発
- 複数ファイルにまたがる変更
- 複数サービスにまたがる変更
- auth、billing、security、public API、DB migration、infra、production configを触る作業
- Subagentを使う作業
- 長時間のAgentic Development
- 既存ドキュメントや `AGENTS.md` が未整備なリポジトリ
- 同じリポジトリを今後何度もAgentに触らせる予定がある場合

このSkillは、次の作業では原則として使いません。

- 1ファイルのtypo修正
- formatterだけの変更
- 明白な1行修正
- すでに整った `AGENTS.md` とAgent contextがある小変更

## 中心設計思想

### 1. `AGENTS.md` には「何を守るか」と「何を見ればよいか」を置く

`AGENTS.md` は、長い説明を書く場所ではありません。

`AGENTS.md` には、以下を置きます。

- 絶対に守るべきリポジトリ固有の不変条件
- generated file、public API、secret、dependency、migration、deployに関する制約
- 作業領域ごとの最初に読むdoc
- 作業領域ごとの最初に見るfile
- 作業領域ごとの使うべきSkill
- 作業領域ごとのtargeted test command
- broad searchの前に見るべき短縮map

`AGENTS.md` には、以下を置きません。

- 長い設計背景
- 過去の議論全文
- API仕様全文
- すべてのSkill本文
- lintで検出できるstyle rule
- timestamp
- issue番号
- 現在のログ
- 一時的なplan
- ユーザー固有情報

### 2. Agent向け短縮ドキュメントを作る

人間向けdocsとAgent向けdocsを分けます。

推奨構成:

```
.agent/
  ctx/
    index.md
    auth.md
    api.md
    db.md
    test.md
  maps/
    paths.md
    skills.md
  prompts/
    dev-commander.md
```

`.agent/ctx/*.md` は、長い説明ではなく、作業索引です。

`.agent/ctx/auth.md` のような短いpathは、Agent prompt、Subagent prompt、レビュー結果、handoff promptで繰り返し出やすいため、token削減にも効きます。ただし、意味が分からない略語は使わないでください。短く、人間も監査できるpathにしてください。

### 3. 人間向けdocsは長くてよい

人間向けdocsは、読みやすく、背景を含めて構いません。

例:

```
docs/auth/refresh-token-expiration-and-login-redirect.md
docs/auth/oauth-session-lifecycle.md
docs/api/public-error-compatibility.md
```

Agent向けdocは、これらへの入口を持つ短いmapにします。

### 4. Skill本文は `AGENTS.md` に貼らない

`AGENTS.md` にはSkill逆引きだけを置きます。

良い例:

```
## Skill routing

- `$auth-debugging`: OAuth, refresh token, session expiry, JWT, CSRF.
- `$api-compat-review`: public API errors, OpenAPI, GraphQL, generated clients.
- `$test-regression`: regression tests and targeted test commands.
```

悪い例:

```
## Skill routing

ここに全Skillの本文を貼る。
...
```

Codex Skillsはprogressive disclosureで読み込まれるため、Skill本文は必要時だけ読ませる設計にしてください。 [OpenAI Developers](https://developers.openai.com/codex/skills)

### 5. Prompt Cachingを前提に、固定prefixを安定させる

Preflight成果物は、Prompt Cachingが効きやすいように設計します。

固定prefixに向くもの:

- `AGENTS.md`
- nested `AGENTS.md`
- `.agent/ctx/*.md` への短い入口
- Skill metadata
- 共通の作業契約
- Subagent共通のacceptance criteria
- 出力schema
- 安定したtest routing

固定prefixに入れてはいけないもの:

- timestamp
- request ID
- CI log
- grep結果
- test output
- RAG結果
- file snippet
- issue固有の一時情報
- Subagent固有のroleやfocus

Subagent promptでは、共通文脈を前に置き、worker固有文脈を後ろに置いてください。

### 6. Subagentは調査とレビューに使う

Subagentは、並列に独立調査できる場合だけ使います。

良い使い方:

- backend explorer
- frontend explorer
- test explorer
- API compatibility reviewer
- security reviewer
- performance reviewer

悪い使い方:

- 全Subagentに同じ探索をさせる
- 複数Subagentに同じファイルを編集させる
- Subagentに実装を分散させる
- ログ全文を全Subagentに渡す
- Subagentごとのprompt冒頭を毎回変える

Preflight Skillは、Subagentを使う場合、原則として「read-only investigation first, main-thread implementation, read-only post-patch review」という構成を推奨してください。

## Workflow

### Phase 0: 使用可否判定

最初に、このタスクがpreflight対象かを判定してください。

軽量preflightでよい場合:

- 対象領域が1つ
- 変更規模が小さい
- `AGENTS.md` がある
- テスト経路が明確

full preflightが必要な場合:

- 複数サービス
- Subagentを使う
- auth、billing、security、DB、public API、infraを触る
- docsが未整備
- `AGENTS.md` がない
- リポジトリが大きい
- 今後もAgentで繰り返し触る予定がある

小変更でpreflight不要なら、その理由を短く返してください。

### Phase 1: Inventory

リポジトリを調査してください。

見る対象:

```
AGENTS.md
AGENTS.override.md
nested AGENTS.md
README.md
CONTRIBUTING.md
package manager files
lockfiles
CI config
test config
docs/
.agent/
.agents/skills/
OpenAPI / GraphQL / schema files
generated code directories
migration directories
deployment config
secret or credential filename patterns
```

secretやcredentialの中身は読まないでください。pathやpatternだけを扱ってください。

出力:

```
## Inventory

| Path | Role | Use in AGENTS.md? | Use in .agent/ctx? | Notes |
|---|---|---:|---:|---|
```

### Phase 2: Risk classification

対象タスクのリスクを分類してください。

分類軸:

```
auth/session/token
billing/payment
public API
database migration
security-sensitive code
production configuration
generated client
multi-service change
external side effect
dependency change
```

出力:

```
## Risk classification

- Risk level: low / medium / high
- Sensitive areas:
- Required approvals:
- Required reviewers:
- Required tests:
```

### Phase 3: Invariant extraction

Agentが作業前に知るべき不変条件を抽出してください。

不変条件の例:

```
- Do not edit generated clients.
- Do not log tokens, cookies, authorization headers, or credentials.
- Do not change public API response shapes without explicit approval.
- Do not add production dependencies without approval.
- Refresh-token expiry must map to an auth-domain error, not generic 500.
- Login redirects must go through `apps/web/src/auth/redirect.ts`.
```

lintやformatterで検出できるものは除外してください。

### Phase 4: Routing map作成

「あれをやるなら何を見るか」を短く作ってください。

出力形式:

```
## Work routing

| Task phrase | First doc | First files | Skills | Targeted tests |
|---|---|---|---|---|
| OAuth / refresh token / session expiry | `.agent/ctx/auth.md` | `services/auth/src/token-exchange.ts`, `apps/web/src/auth/redirect.ts` | `$auth-debugging`, `$frontend-auth-redirect` | `pnpm --filter @acme/auth test`, `pnpm --filter @acme/web test -- auth` |
```

### Phase 5: `AGENTS.md` 設計

既存 `AGENTS.md` がなければ作成案を出してください。

既存 `AGENTS.md` があれば、短縮、分割、移動のpatch案を出してください。

root `AGENTS.md` の推奨構造:

```
# AGENTS.md

## Agent context

Use these compact maps before broad search:

- General index: `.agent/ctx/index.md`
- Path map: `.agent/maps/paths.md`
- Skill map: `.agent/maps/skills.md`
- Test routing: `.agent/ctx/test.md`

## Hard rules

- Do not edit generated clients.
- Do not log tokens, cookies, authorization headers, or credentials.
- Do not add production dependencies without approval.
- Do not change public API shapes without explicit approval.
- Use targeted tests before broad test suites.

## Work routing

| Task | First map | Skills | Tests |
|---|---|---|---|

## Common commands

- Lint:
- Typecheck:
- Targeted tests:
```

領域固有の細かいルールはnested `AGENTS.md` へ分けてください。

例:

```
services/auth/AGENTS.md
apps/web/AGENTS.md
packages/api-client/AGENTS.md
```

### Phase 6: Agent context docs作成

`.agent/ctx/*.md` を提案してください。

例:

```
.agent/ctx/index.md
.agent/ctx/auth.md
.agent/ctx/api.md
.agent/ctx/test.md
.agent/maps/skills.md
.agent/maps/paths.md
```

`.agent/ctx/auth.md` の例:

```
# Auth context

## Read first

- Human overview: `docs/auth/oauth-session-lifecycle.md`
- Refresh-token behavior: `docs/auth/refresh-token-expiration-and-login-redirect.md`
- API compatibility: `docs/api/public-error-compatibility.md`

## Entry points

- Backend token exchange: `services/auth/src/token-exchange.ts`
- Error mapping: `services/auth/src/errors.ts`
- Session middleware: `services/auth/src/middleware/session.ts`
- Frontend redirect: `apps/web/src/auth/redirect.ts`

## Invariants

- Expired refresh tokens map to auth-domain errors, not generic 500.
- Login redirects go through `apps/web/src/auth/redirect.ts`.
- Do not edit generated clients.
- Do not log tokens, cookies, authorization headers, or credentials.

## Tests

- Backend auth: `pnpm --filter @acme/auth test`
- Web auth: `pnpm --filter @acme/web test -- auth`
- API compatibility: `pnpm api:compat`
```

### Phase 7: Skill routing整理

既存Skillを調査し、足りないSkillを提案してください。

出力:

```
## Skill routing

| Skill | Trigger terms | Use when | Do not use when | First docs |
|---|---|---|---|---|
```

Skillが未整備なら、将来作るべきSkillを提案してください。

例:

```
auth-debugging
frontend-auth-redirect
api-compat-review
test-regression
security-token-review
db-migration-review
```

ただし、preflight-engineering Skillの初回実装では、これらのSkillをすべて実装しなくてよいです。まずは「必要なSkillを発見・提案する」能力を作ってください。

### Phase 8: Cache readiness check

Prompt Cachingを壊しにくい構成か検査してください。

チェック項目:

```
## Cache readiness

- [ ] root `AGENTS.md` contains stable guidance only.
- [ ] No timestamp, issue-specific log, request ID, or temporary plan in `AGENTS.md`.
- [ ] Long human docs are referenced, not pasted.
- [ ] Skill bodies are not pasted into `AGENTS.md`.
- [ ] `.agent/ctx` paths are short and stable.
- [ ] Subagent shared prompt context is placed before worker-specific context.
- [ ] Tool/schema/order-sensitive lists are described as deterministic where relevant.
- [ ] User-specific or run-specific data is suffix-only.
- [ ] Nested `AGENTS.md` is used for specialized areas.
```

### Phase 9: Subagent plan作成

Subagentを使う場合、read-only調査から始めるplanを作ってください。

出力形式:

```
## Subagent plan

### Phase 1: read-only investigation

1. Backend explorer
   - Scope:
   - Skills:
   - Outputs:

2. Frontend explorer
   - Scope:
   - Skills:
   - Outputs:

3. Test explorer
   - Scope:
   - Skills:
   - Outputs:

4. Security/API reviewer
   - Scope:
   - Skills:
   - Outputs:

### Phase 2: main-thread implementation

- Main agent synthesizes findings.
- Main agent implements minimal patch.
- Main agent runs targeted tests.

### Phase 3: read-only post-patch review

- Security/API reviewer
- Test coverage reviewer
```

Subagentに編集させる設計は、明示的にユーザーが求めた場合を除いて避けてください。

### Phase 10: Handoff prompt生成

preflightの最後に、開発総指揮Agentへ渡すpromptを生成してください。

handoff promptには必ず以下を含めてください。

- GOAL
- 対象リポジトリのreadiness summary
- 参照すべき `AGENTS.md`
- 参照すべき `.agent/ctx`
- 使うべきSkills
- hard constraints
- Subagent plan
- 実装方針
- targeted test plan
- post-patch review plan
- final response format

handoff promptの例:

```
You are the development commander for <TASK_ID>.

Goal:
<clear goal>

Repository readiness:
- Follow root `AGENTS.md`.
- Follow nested `AGENTS.md` in relevant directories.
- Use `.agent/ctx/index.md` before broad search.
- Use relevant `.agent/ctx/*.md` maps.
- Use `.agent/maps/skills.md` for skill routing.

Hard constraints:
- Preserve public API compatibility unless explicitly approved.
- Do not edit generated files.
- Do not log secrets, credentials, tokens, cookies, or authorization headers.
- Do not add production dependencies without approval.
- Keep the diff minimal.

Subagent phase 1:
Spawn read-only subagents and wait for all results.

1. <subagent name>
   - Scope:
   - Skills:
   - Output:

Main implementation phase:
- Synthesize subagent findings in the main thread.
- Implement the minimal fix in the main thread.
- Run targeted tests first.

Subagent phase 2:
Spawn read-only reviewers for:
- API/security
- test coverage

Final response:
- root cause
- changed files
- tests run
- remaining risks
```

## OAuth refresh token事例での期待動作

このSkillを、次の依頼に対して使えるようにしてください。

```
Issue AUTH-1841を修正したい。

症状:
OAuth refresh tokenが期限切れになったとき、frontendは再ログイン画面へ遷移すべきだが、現在は500エラー画面になる。

条件:
- public API互換性を壊さない
- auth middleware設計に従う
- 回帰テストを追加する
- 差分は最小にする
- Subagentを使って原因調査、テスト観点、安全性観点を並列に確認したい
```

期待するpreflight出力:

```
AGENTS.md更新案
services/auth/AGENTS.md更新案
apps/web/AGENTS.md更新案
.agent/ctx/auth.md作成案
.agent/ctx/api.md作成案
.agent/ctx/test.md作成案
.agent/maps/skills.md作成案
Subagent plan
Cache readiness check
Development commander handoff prompt
```

OAuth事例で `AGENTS.md` に入れるべき情報の例:

```
## Auth work quick map

Use this map before broad search.

- OAuth / refresh token / session expiry:
  - First map: `.agent/ctx/auth.md`
  - Backend entry: `services/auth/src/token-exchange.ts`
  - Error mapping: `services/auth/src/errors.ts`
  - Middleware: `services/auth/src/middleware/session.ts`
  - Frontend redirect: `apps/web/src/auth/redirect.ts`
  - Frontend guards: `apps/web/src/auth/guards/`
  - API compatibility: `.agent/ctx/api.md`

## Auth invariants

- Expired refresh tokens must become an auth-domain error, not a generic 500.
- Login redirects must go through `apps/web/src/auth/redirect.ts`.
- Do not edit generated API clients directly.
- Do not log tokens, cookies, authorization headers, refresh tokens, or credentials.
- Do not change public API error shapes without explicit approval.

## Auth skill routing

- `$auth-debugging`: OAuth, refresh token, session expiry, JWT, CSRF.
- `$frontend-auth-redirect`: login redirect, route guard, auth error UI.
- `$api-compat-review`: public API errors, OpenAPI, GraphQL, generated clients.
- `$test-regression`: regression tests and targeted test commands.
- `$security-token-review`: token exposure, redirect safety, credential leakage.
```

## 情報圧縮方針

短くする対象は、自然文の冗長な説明です。

短くしてよいもの:

- 長いpathをAgent向けmapで短いaliasにする
- 同じ説明の重複
- README的な背景説明
- lintで検出できるstyle rule
- 過去の議論

短くしてはいけないもの:

- security invariant
- public API compatibility rule
- destructive operation policy
- secret handling rule
- generated file boundary
- approval requirement
- test command
- file path

悪い圧縮:

```
AUTH:R1=RTEXP->AERR; R2=REDIR@web/auth; R3=NO-GEN; R4=NO-TOKLOG
```

良い圧縮:

```
## Auth invariants

- AUTH-ERR: Refresh-token expiry maps to an auth-domain error, not generic 500.
- AUTH-REDIRECT: Login redirects go through `apps/web/src/auth/redirect.ts`.
- AUTH-GEN: Do not edit generated clients.
- AUTH-LOG: Never log tokens, cookies, authorization headers, or credentials.
```

人間が監査できないほどの圧縮は禁止してください。

## Symlink方針

Skill folderのsymlinkは、Codexがscan時にsymlink targetをたどるため、複数ツールでSkillを共有する用途では検討してよいです。 [OpenAI Developers](https://developers.openai.com/codex/skills)

ただし、Agent向け短縮docはsymlinkより実体ファイルを推奨します。

推奨:

```
.agent/ctx/auth.md       # Agent向け短縮mapの実体
docs/auth/*.md           # 人間向け詳細docs
```

非推奨:

```
.agent/ctx/auth.md -> docs/auth/very-long-human-document-name.md
```

理由は、人間向けdocが長くなりやすく、Agent向け短縮mapとしての役割を失いやすいためです。

## Human interaction policy

Preflight Skillは、人間と対話して不足情報を埋めてください。

ただし、毎回細かい質問をしすぎないでください。まずリポジトリを調査し、仮説を作り、不明点だけを質問してください。

質問すべきもの:

- このリポジトリで最も危険な変更領域
- public API互換性の扱い
- generated fileの境界
- secretやcredentialの扱い
- deployやmigrationの承認条件
- 既存Skillの正本
- human docsとAgent docsの置き場所
- Subagentを使うかどうか

質問せず推定してよいもの:

- package manager
- test command候補
- docs候補
- service boundary候補
- generated directory候補

推定した内容は、必ず「confirmed / inferred / unknown」で区別してください。

## Output format

Skill実行時の最終出力は、必ずこの構造にしてください。

```
# Preflight result

## Summary

## Repository readiness score

- AGENTS.md:
- Agent context docs:
- Skill routing:
- Test routing:
- Safety invariants:
- Prompt caching readiness:
- Subagent readiness:

## Proposed file changes

| File | Action | Purpose |
|---|---|---|

## Key invariants

## Work routing map

## Skill routing map

## Test routing

## Cache readiness check

## Subagent plan

## Human decisions required

## Development commander handoff prompt

## Remaining gaps
```

## Acceptance criteria

このSkillの初回実装は、以下を満たしたら完了です。

- `.agents/skills/preflight-engineering/SKILL.md` が存在する。
- `SKILL.md` に `name` と `description` がある。
- descriptionの先頭に `Preflight`, `AGENTS.md`, `agent context`, `skill routing`, `subagent handoff` などのtrigger語がある。
- Skill本文に、Inventory、Risk classification、Invariant extraction、Routing map、AGENTS.md設計、Agent context docs設計、Skill routing、Cache readiness、Subagent plan、Handoff promptの各Phaseがある。
- 実装作業をしないことが明示されている。
- secretやcredentialの中身を読まないことが明示されている。
- `AGENTS.md` に長文docsやSkill本文を貼らない方針が明示されている。
- `.agent/ctx` と `.agent/maps` の推奨構成がある。
- OAuth refresh token事例のサンプルが含まれている。
- final output formatが定義されている。
- `references/` にテンプレートがある。
- 小変更ではpreflightを省略する判断基準がある。
- Subagentは原則read-only調査とpost-patch reviewに使う方針がある。
- Prompt Cachingを壊す要因、つまり可変情報をprefixに入れない、共通文脈を先頭へ置く、toolsやschema順序を安定させる、という注意が含まれている。

## 実装順序

まず、 `SKILL.md` を作成してください。

次に、 `references/` 配下にテンプレートを作成してください。

最後に、OAuth refresh token事例を使って、このSkillがどのようなpreflight resultを出すか、短いdry-run例を `references/oauth-refresh-token-example.md` として追加してください。

初回実装では、scriptは任意です。scriptを追加する場合も、Skillの本質がscript依存にならないようにしてください。

## 期待する最終ファイル構成

```
.agents/skills/preflight-engineering/
  SKILL.md
  references/
    agents-template.md
    agent-ctx-template.md
    skill-map-template.md
    handoff-prompt-template.md
    cache-readiness-checklist.md
    oauth-refresh-token-example.md
```

## 最後に確認すること

実装後、次の観点で自己レビューしてください。

```
## Self-review

- [ ] This skill prepares the environment and does not implement product changes.
- [ ] The skill can be triggered implicitly by its description.
- [ ] The skill keeps AGENTS.md compact and stable.
- [ ] The skill separates human docs from Agent context docs.
- [ ] The skill encourages Skill routing, not Skill body pasting.
- [ ] The skill produces a development commander handoff prompt.
- [ ] The skill includes a cache-readiness check.
- [ ] The skill treats Subagents as useful but token-expensive.
- [ ] The skill avoids unreadable over-compression.
- [ ] The skill includes the OAuth refresh token example.
```

## 補足設計メモ

Preflight Engineeringの価値は、最初に「正しい地図」を作ることです。

開発Agentは、GOALを受け取れば段取りを作れます。しかし、リポジトリ固有の不変条件、見るべきファイル、テスト経路、Skill逆引き、generated file境界、public API互換性、secret handlingは、リポジトリ側に置かれていなければ毎回探索することになります。

このSkillは、その探索を構造化し、次回以降のAgent loopで再利用できる形にします。

`AGENTS.md` は「AI用README」ではありません。 `AGENTS.md` は、Agentが作業開始前に読む、短く安定した作業契約です。

`.agent/ctx/*.md` は「人間向け設計書」ではありません。Agentが最初にどこを見るかを決めるための、短い作業mapです。

`handoff prompt` は「ユーザー依頼の再掲」ではありません。preflightで得たリポジトリ地図を使って、開発総指揮Agentを安全に起動するための実行指示です。
