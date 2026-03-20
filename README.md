# AI Agent Instructions Playbook

このリポジトリは、ソフトウェア開発エージェント向けの「薄い常設ルール + 必要時だけ読む詳細プレイブック」を提供するテンプレートです。

## Core files

- `AGENTS.md` — 常時読み込まれる中核ルールと skill index
- `COMMANDS.md` — build / lint / test の正規コマンド
- `PLANS.md` — ExecPlan 運用のガイド
- `README.md` — リポジトリ概要と最小導入
- `REFERENCES.md` — 参照ドキュメントの入口

## Core runtime skills（short list）

- `dev-workflow` — 変更リスクをルーティングし、必要分岐だけ実行
- `quality-gate` — 提出前の最終判定
- `execution-plans` — 複雑・長期タスクの実行計画管理
- `requirements-to-design` — 要件を実装可能な設計入力へ変換
- `project-initialization` — コマンド体系の初期化

詳細な skill 一覧と運用手順は `AGENTS.md` と各 `SKILL.md` を参照してください。

## Minimal bootstrap

1. `AGENTS.md` を開き、`dev-workflow` と `quality-gate` の流れを確認する。
2. `COMMANDS.md` が未初期化（`<fill>`）なら `project-initialization` を実行する。
3. 変更の前後で、`COMMANDS.md` に定義された正規コマンドで検証する。
