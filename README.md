# AI Agent Instructions Playbook

このリポジトリは、ソフトウェア開発エージェント向けの**再利用可能な運用プレイブック集**です。  
目的は、リポジトリ固有の開発ルールを「常時読む薄いルール」と「必要時だけ読むスキル」に分離し、変更の一貫性と検証可能性を高めることです。

## Core files

- `AGENTS.md` — エージェント共通の中核ルール（必読）
- `COMMANDS.md` — build / lint / test の正規コマンド
- `PLANS.md` — ExecPlan の運用ルール
- `plans/README.md` — `plans/` 配下の使い方
- `REFERENCES.md` — 参照ドキュメント索引
- `.agents/skills/` — Codex 用スキル本体
- `.github/skills/` — Agent Skills 互換ミラー
- `.github/prompts/` — VS Code 用 prompt 集
- `.github/instructions/` — パス別ルール

## Core runtime skills (short list)

日常運用で中心になるスキル:

- `dev-workflow` — 変更時の標準フロー（risk routing 起点）
- `quality-gate` — 提出前の最終品質ゲート
- `execution-plans` — 長期/複雑タスクの計画管理
- `requirements-to-design` — 要求→設計への落とし込み
- `observability` — 挙動変更時の診断可能性確保

## Minimal bootstrap

1. `AGENTS.md` を開き、Always-on principles と Mandatory workflow を確認する。  
2. `COMMANDS.md` を開き、このリポジトリの正規 verify コマンドを確認する。  
3. 変更作業は `dev-workflow` で開始し、完了前に `quality-gate` を適用する。
