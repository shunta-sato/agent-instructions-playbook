---
name: execution-plans
description: "MANDATORY for complex/long-running work: create and maintain an ExecPlan in plans/<slug>.md (WBS/progress, design notes, decisions, surprises, and handoff). Always open PLANS.md and references/execution-plans.md."
metadata:
  short-description: "ExecPlan: plan/WBS/progress + handoff"
---

## Purpose

Use this skill to create (or update) an **ExecPlan**: a living, self-contained plan that makes long work measurable, reviewable, and handoff-ready.

This addresses three recurring failure modes in agentic coding:

- work starts without a shared plan, so scope drifts
- progress is not tracked, so “where are we?” is unclear
- context handoff is weak, so long tasks regress or stall

## When to use

This skill is **mandatory** when any ExecPlan trigger is true (see `PLANS.md`), including:

- multi-step / multi-session tasks
- cross-boundary refactors or new modules
- tasks with meaningful unknowns (API choices, rollout, concurrency, performance)

It is also a good default when you are unsure.

## How to use

1) Open `PLANS.md` and `references/execution-plans.md`.

2) Create or update a plan file under `plans/` using `plans/_template_execplan.md`.
   - Quick start helper: `python scripts/init_artifact.py --kind execplan --slug <ticket-or-topic>`

3) Keep the plan up to date while you work:
- update **Progress (WBS)** as items complete
- record **Surprises & discoveries** as you learn new constraints
- record **Decision log** entries for trade-offs
- update **Handoff** whenever you pause or finish a milestone

4) If a human is present and the change is risky/irreversible, ask for approval after drafting the plan and before large edits.

## Gotchas

- **ありがち:** 最初に plan を作るだけで Progress (WBS) を更新しない。  
  **代わりに:** タスク完了ごとに status を更新し、未着手/進行中/完了を常に最新化する。
- **ありがち:** 大きな方針変更を口頭で済ませ、Decision log を残さない。  
  **代わりに:** 変更理由・代替案・採用判断を plan の Decision log に追記する。
- **ありがち:** セッション終了時に handoff が古く、次担当が再調査から始める。  
  **代わりに:** 停止時点で「現在地 / 次の1手 / ブロッカー / 実行コマンド」を Handoff に必ず更新する。
- **ありがち:** 複雑作業なのに ExecPlan を作らず ad-hoc に進める。  
  **代わりに:** PLANS.md の trigger に1つでも該当したら `plans/<slug>.md` を作成してから着手する。

## Output expectation

When this skill is used, produce:

- An updated ExecPlan file in `plans/…`
- A short status update in the standard format (see the reference)
- Clear “what’s next” items if work is not finished
