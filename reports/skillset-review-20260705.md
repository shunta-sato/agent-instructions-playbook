# Skillset Strategic Review — 2026-07-05

対象: agent-instructions-playbook 全体(スキル50件、約3,428行 + ルーティング/eval/スクリプト基盤)
目的: Codex運用で発生した「巨大main.rs + テストコード混在」インシデントの根本原因究明と、
Claude Code上での Opus 4.8(司令塔)+ Sonnet 5(ワーカー)混成チーム運用に向けた改善戦略の策定。
手法: 4系統の並列調査(根本原因分析 / 中位モデル理解容易性監査 / プラットフォーム基盤調査 / ポートフォリオ健全性評価)を統合。

---

## 1. エグゼクティブサマリー

**main.rs肥大化はバグではなく、現行スキル体系の原則群の論理的帰結である。**
スキルは発火していた(dev-workflow 83回/日、quality-gate 76回/日)が、以下の4つの構造的欠陥により
「モノリス化を止める者が誰もいない」状態だった:

1. 全トリガーが**イベント駆動**(構造変更の提案時のみ発火)であり、**状態駆動**(構造の劣化を検知)が存在しない。
   main.rsへの追記は「レイアウト変更イベント」を発生させないため、design-balance等は原理的に発火し得ない。
2. 常時原則「最小の安全な変更」+ implementation-economy の抽象化抑制が、
   局所最適として**常に「既存ファイルへの追記」を選好**させる。スキルはモノリス方向に押していた。
3. quality-gate は**プロセス成果物の存在確認のみ**を行い、構造的出口基準
   (ファイルサイズ、モジュール数、テスト配置)を一切持たない。モノリスはゲートを素通りする。
4. **言語別プロジェクトレイアウト規約が全スキルに不在**(Rustの lib.rs/main.rs 分割、
   `#[cfg(test)]`/`tests/` 配置)。さらに dev-workflow の low-risk ルート
   「1ファイル・抽象化なしならレーンをスキップ」が、main.rs追記を毎回素通しにした。

加えて、スキル群は Opus級の推論を前提とした曖昧述語・入れ子条件・深い参照連鎖を多用しており、
**Sonnet 5 での誤実行リスクが高い**。Claude Code へのネイティブ配線はゼロである。

---

## 2. 目指すべき姿(To-Be)

### 2.1 品質保証モデル
- スキルは**プロセス遵守ではなく構造的結果を保証**する。quality-gate は成果物の存在に加え、
  検証可能な構造基準(ファイル行数、モジュール数、テスト配置、公開API面)で submit/no-submit を判定する。
- トリガーは**イベント駆動 + 状態駆動のハイブリッド**。「変更を提案した時」だけでなく
  「触れたファイルが閾値を超えた時」「テストコード比率が偏った時」に必ず設計スキルへ回送される。
- **生成的ガイダンス**(書く前に構造を形成する: プロジェクトレイアウト、命名、分割基準)が
  レビュー系スキルと同格の第一級市民である。

### 2.2 モデル可搬性
- 全スキルは**Sonnet 5 が決定木・チェックリスト・数値閾値で迷わず実行できる**水準で記述される。
  曖昧述語(「measurable」「primary」「large」)は数値または検査可能な述語に置換される。
- 出力契約は機械検証可能(固定見出し、固定enum)。参照ファイルの必読マニフェストがあり、
  部分読み込みが検出可能。
- 語彙は用語集で統一(route/branch/lane → 1語、artifact/evidence/record → 定義済み使い分け)。

### 2.3 プラットフォームと混成チーム運用
- `.agents/skills/` を単一ソースとし、Claude Code(`.claude/`)・Copilot(`.github/prompts/`)向けは
  **生成物**。手動ミラーは廃止。
- Opus 4.8 = オーケストレーター/アーキテクト/最終判定(judge)、Sonnet 5 = スコープ限定ワーカー、
  という役割が model catalog + route lockfile + `.claude/agents/` 定義で再現可能に結線される。
- 委譲は既存のタスクブリーフ契約(allowed files / commands / stop conditions)に従い、
  run ledger が Claude Code 実行も捕捉する。

### 2.4 継続校正ループ
- テレメトリの「その他」が解消され、スキル別の発火実態が可視化される。
- 高トラフィックスキルは十分な positive eval を持ち、**Sonnet 5 を対象モデルとした実行eval**で
  スキル改訂ごとに回帰検証される。レビュー勧告は closure まで追跡される。

---

## 3. 現在の姿(As-Is)

### 3.1 品質保証モデルの実態(根本原因分析より)
| # | 事実 | 根拠 |
|---|------|------|
| A1 | 全50スキルのトリガーがイベント駆動。状態駆動(メトリクス監視)ゼロ | design-balance「adds two or more classes/modules」等、追記では発火不能 |
| A2 | AGENTS.md「最小の安全な変更」「広範なクリーンアップ禁止」+ implementation-economy「抽象化より再利用/インライン優先」がモノリス方向の力学を形成 | AGENTS.md L86-88, implementation-economy L40 |
| A3 | quality-gate は Complexity Budget / Responsibility Map 等の**存在**のみ確認。構造メトリクスの出口基準なし | quality-gate SKILL.md L25-30 |
| A4 | テスト配置・言語レイアウト規約が皆無。working-with-legacy-code に cpp/py/ts 変種はあるが **Rust変種なし** | TDDスキルは Red/Green/Refactor のみ |
| A5 | dev-workflow low-risk ルート「1ファイル・抽象化なし→レーンスキップ」が増分追記を毎回素通し | dev-workflow SKILL.md L26, references L10 |
| A6 | implementation-economy の監査は**事後**であり、ブロッキングな構造ゲートではない | SKILL.md L29/L47 |

### 3.2 Sonnet 5 適合性の実態(理解容易性監査より)
- **曖昧述語**: スキルの約48%が判断依存トリガーを持つ(「measurable quality drivers」「primary question」
  「when needed」「not understood」)。中位モデルは不確実時に low-risk 分類 + ブランチスキップへ流れる。
- **入れ子条件**: dev-workflow は15超、quality-gate は20超の条件分岐を散文で保持。
  三重否定(「Do NOT require X UNLESS Y」)を含む。最初の finding で監査を打ち切るリスク。
- **コンテキスト負荷**: 必須パス最小 ~2.6Kトークン、high-risk 最悪 ~15Kトークン/19ファイル/最大4ホップ。
  部分読み込みを検出するガードなし(preflight-engineering は8ファイル必読)。
- **語彙断片化**: trigger/branch/route/lane/required-branch、artifact/evidence/record/ledger が混在。
  `$skill` 記法は Codex 専用で Claude Code では機能しない。
- **出力契約**: 7スキルが曖昧(「make the route obvious」等)。function-boundary-governor の
  スコアリング(0-2×12基準)に閾値・重みが未定義。
- **誤実行リスク上位**: embedded-system-familiarization(9/10)、dev-workflow(8.5)、quality-gate(8)、
  preflight-engineering(7.5)、requirements-engineering(7.5)。

### 3.3 プラットフォーム基盤の実態(基盤調査より)
- **Claude Code ネイティブ配線ゼロ**: `.claude/` ディレクトリ・CLAUDE.md・skills 配置なし。
  ただし SKILL.md frontmatter 自体は Claude Code 互換であり移行障壁は低い。
- **モデルルーティング土台は既存**: task-classes.yml / capability-profiles.yml / resolver ポリシー /
  prompt-detail-levels(compact/normal/strict)/ resolve_model_route.py。
  **欠落は結線のみ**: model catalog、route lockfile、`.claude/agents/` バインディング。
- **委譲契約は設計済み**: preflight-engineering → execution-plans(subagent-task-brief / report /
  supervisor-review テンプレート)→ agent-workflow-contract-review の3段。Claude Code の
  Agent tool / custom agents へのマッピングは自然に可能。
- **重複負債**: `.github/prompts/` 19ファイルが手動ミラー。第3クライアント追加で drift 点が3倍化。
- **run ledger は Codex 専用**(parse_codex_jsonl.py)。judge_agent_run.py は未接続。
- **未コミット作業**: function-design 検証一式(fixtures 6シナリオ + oracle ハーネス +
  validate_function_design_protocol.py)が実質完成済みだが未コミット・Makefile未結線。
  `function-design-eval-content/` は重複ステージング。

### 3.4 ポートフォリオの実態(健全性評価より)
- **構成の偏り**: embedded 10skills(20%)> code-quality 6(12%)。生成的ガイダンスは3スキルのみ
  (design-balance / implementation-economy / architecture-decision-analysis)。
  命名・関数複雑度・言語イディオム・新規構造の指針が欠落。
- **embedded co-firing**: nfr-design / hot-path / observer-effect / nfr-gate が
  「logger, recorder, polling, always-on, daemon」の同一キーワードを共有し、クラスタ発火
  (計~112回/日、トラフィックの8-13%)。CLIプロジェクトに対する恒常的コンテキスト税。
- **設計品質の5スキル重複ゾーン**: design-balance / code-smells / function-boundary-governor /
  implementation-economy / architecture-decision-analysis が同一領域で競合。優先順位・排他規則が不完全。
- **eval の薄さ**: implementation-economy(65回/日発火、positive eval 2件)、execution-plans(40回/日、1件)。
  25スキルが positive ≤2。LLM実行型のevalランナーは不在(JSONスキーマ検証のみ)。
- **テレメトリ**: 「その他」239件/日(76%が未分類)— 発火実態が不可視。
- **前回レビュー(2026-04-24)勧告のうち2件が未消化**(uidesign-orchestrator の去就、eval運用強化)。

---

## 4. GAP分析

| # | GAP | To-Be | As-Is | 深刻度 |
|---|-----|-------|-------|--------|
| G1 | **プロセス保証 ≠ 構造保証** | 構造的出口基準で submit 判定 | 成果物存在確認のみ。モノリスがゲート通過 | ★★★ 直近インシデントの直接原因 |
| G2 | **インセンティブの矛盾** | 「最小の変更」と「健全な分解」が両立する原則体系 | 最小変更原則+経済性スキルがモノリスを選好 | ★★★ 同上 |
| G3 | **状態駆動トリガーの不在** | 構造劣化(サイズ/比率超過)で設計スキルが強制発火 | イベント駆動のみ。追記は永遠に素通し | ★★★ 同上 |
| G4 | **生成的構造ガイダンス欠落** | 言語別レイアウト/テスト配置/分割基準を書く前に適用 | Rust規約ゼロ、テスト配置規約ゼロ | ★★★ |
| G5 | **Sonnet 5 実行可能性** | 決定木+数値閾値+固定出力契約 | 曖昧述語48%、入れ子15-20、参照4ホップ | ★★★ 混成チーム移行の前提条件 |
| G6 | **Claude Code 配線** | `.claude/` 一式 + 単一ソース生成 | 配線ゼロ、手動ミラー重複 | ★★☆ 移行の物理的前提 |
| G7 | **モデルルーティング結線** | catalog + lockfile + agents バインド + run捕捉 | 土台のみ。Opus/Sonnet未結線、ledgerはCodex専用 | ★★☆ |
| G8 | **ポートフォリオ均衡** | 汎用code-quality中心、embeddedはアンチトリガーで抑制 | embedded過重・co-firing、5スキル重複ゾーン | ★★☆ |
| G9 | **校正ループ** | テレメトリ可視化+高トラフィックskillの実行eval | 「その他」76%、positive eval薄、勧告未追跡 | ★★☆ 再発防止の持続性 |

---

## 5. GAP解消課題(ワークストリーム)

改善実行は本レビューの次フェーズ。以下は優先度・依存関係・担当モデル案を含む課題定義である。

### Phase 0 — 足場固め(依存なし、即時)
| WS | 課題 | 内容 | 担当案 |
|----|------|------|--------|
| WS0a | 未コミット作業の着地 | function-design eval一式を commit、`validate_function_design_protocol.py` を `make lint` へ結線、`function-design-eval-content/` 重複を解消 | Sonnet 5(機械的) |
| WS0b | 用語集の制定 | route/branch/lane、artifact/evidence/record/ledger の正規語を定義し `.agents/bootstrap/glossary.md` 化。以後の全改訂の基準 | Opus 4.8 起草 → Sonnet 5 適用 |

### Phase 1 — 構造ゲートの導入(G1〜G4: main.rs再発防止。最優先)
| WS | 課題 | 内容 | 担当案 |
|----|------|------|--------|
| WS1 | quality-gate への構造的出口基準 | 検査可能な基準を追加: 触れたファイルの行数閾値(例: ソース400行/超過は分割記録必須)、バイナリクレートの main.rs ロジック行数、テスト配置(Rust: unit=`#[cfg(test)]` mod、integration=`tests/`)、1ファイル内テスト比率。スクリプト化(`scripts/check_structure.py`)して gate から呼ぶ | Opus 設計 → Sonnet 実装 |
| WS2 | 状態駆動トリガーの新設 | dev-workflow に「structure watch」ステップを追加: 編集後に触れたファイルが閾値超過なら design-balance / function-boundary-governor を**必須発火**。low-risk スキップ条件に「かつ触れたファイルが閾値内」を追加 | Opus 設計 |
| WS3 | 生成的 project-structure スキル新設 | 言語別レイアウト規約(まず Rust: main.rs/lib.rs 分割基準、モジュール分割、テスト配置、可視性)。新規ファイル/クレート作成時と structure watch 超過時に発火。working-with-legacy-code に rs 変種追加 | Opus 起草 → Sonnet 展開 |
| WS4 | 原則の矛盾解消 | AGENTS.md を改訂: 「最小の安全な変更」に「ただし構造予算(ファイル/モジュール閾値)内で。超過時は分割が“最小の正しい変更”」と明記。implementation-economy に「モジュール分割は複雑性追加ではなく複雑性の配置である」旨のアンチ誤読条項 | Opus(原則設計は司令塔専管) |

### Phase 2 — Sonnet 5 実行可能化(G5)
| WS | 課題 | 内容 | 担当案 |
|----|------|------|--------|
| WS5 | dev-workflow / quality-gate の決定木化 | 散文条件を番号付きチェックリスト+明示的優先順位表に再構成。三重否定排除。embedded NFR 表に precedence を明記 | Opus 設計 → Sonnet 書換 → Opus 判定 |
| WS6 | 曖昧述語の閾値化 | 「large class」「too complex」「measurable」等16箇所に数値または例示ベースの判定規則を付与。function-boundary-governor のスコア閾値を定義 | Opus 閾値決定 → Sonnet 適用 |
| WS7 | 出力契約の機械検証化 | 全スキルの Output expectation を固定見出し+enumに統一。validate_skills.py に契約lint追加 | Sonnet 実装 |
| WS8 | 必読マニフェスト | 各SKILL.md frontmatter に `requires:`(必読 references/templates 列挙)を追加し、部分読み込みを構造的に防止 | Sonnet 実装 |

### Phase 3 — Claude Code + 混成チーム結線(G6, G7)
| WS | 課題 | 内容 | 担当案 |
|----|------|------|--------|
| WS9 | `.claude/` スキャフォールド | CLAUDE.md(AGENTS.md相当のClaude Code入口)、`.claude/skills/` を `.agents/skills/` から**生成**(generate_agent_index.py 拡張)。`$skill` 記法をクライアント中立表現へ | Sonnet 実装 |
| WS10 | ミラー一本化 | `.github/prompts/` を生成物化または廃止。単一ソース原則を CI で強制 | Sonnet 実装 |
| WS11 | モデルカタログ+ロックファイル | Opus 4.8 / Sonnet 5 を capability-profiles へマップ(coding_supervisor/high_reasoning_review→Opus、focused_code_edit/codebase_explorer→Sonnet)。route lockfile 生成、`.claude/agents/*.md` に model フィールドで結線 | Opus 設計 → Sonnet 実装 |
| WS12 | run ledger の Claude Code 対応 | agent_run.py を拡張し Claude Code 実行を捕捉。judge_agent_run.py をポストラン結線。エスカレーション規約(Sonnet が stop_condition 到達→Opus へ返す)を明文化 | Sonnet 実装 |

### Phase 4 — ポートフォリオ再均衡と校正ループ(G8, G9)
| WS | 課題 | 内容 | 担当案 |
|----|------|------|--------|
| WS13 | embedded アンチトリガー | 全 embedded スキルに「電力/熱/リアルタイム制約のない通常のCLI/デーモンには適用しない」を追加。共有キーワードの排他規則 | Sonnet 実装 |
| WS14 | 設計品質ゾーンの序列化 | 5スキルの優先順位・排他規則を dev-workflow の routing priority に一本化(architecture→design-balance→function-boundary→economy→smells) | Opus 設計 |
| WS15 | eval 拡充 | 高トラフィックスキル(top10)に positive eval 各3-5件。**Sonnet 5 を対象とした実行スモークeval**(改訂スキルを Sonnet に実行させ oracle 判定)を新設 | Sonnet 作成 → Opus 判定 |
| WS16 | テレメトリ分類是正+勧告追跡 | 「その他」76%の分類、前回勧告(uidesign-orchestrator 去就等)の closure 追跡を CHANGELOG/plan で運用 | Sonnet |

### 受け入れ基準(プロジェクト全体)
1. **再現テスト**: 「Rust CLIを新規実装せよ」相当の fixture シナリオで、改訂後スキル群に従うエージェントが
   main.rs 肥大化・テスト混在を起こさない(oracle で機械判定)— WS1-4 の合格条件。
2. **Sonnet 実行eval**: dev-workflow / quality-gate / project-structure を Sonnet 5 単独で実行し、
   ルーティング判断と gate 判定が Opus 実行と一致する — WS5-8 の合格条件。
3. `make verify` 全green + Claude Code 上で `/dev-workflow` 等が自動発見・発火する — WS9-12 の合格条件。

### 実行体制(混成チーム運用モデル)
- **Opus 4.8(司令塔/アーキテクト/ジャッジ)**: 原則改訂(WS4)、決定木設計(WS5)、閾値決定(WS6)、
  ルーティング設計(WS11, WS14)、全WSの最終レビュー判定。
- **Sonnet 5(ワーカー)**: タスクブリーフ(既存 subagent-task-brief テンプレート)に基づく
  スコープ限定実装 — スキル書換の機械的展開、スクリプト実装、eval作成、生成パイプライン。
- 委譲は既存3段契約(preflight → task brief → contract review)をそのまま使用し、
  本改善プロジェクト自体を新運用モデルのパイロットとする。

---

## 6. 付記
- 本レビューの詳細な生データ(引用箇所、file:line)は調査エージェントの出力に基づく。
  主要な引用は本文に記載済み。
- 前回レビュー: reports/skillset-review-20260424.md(勧告2件未消化 → WS16 で追跡)。
