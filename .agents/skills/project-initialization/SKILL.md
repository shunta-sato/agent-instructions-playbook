---
name: project-initialization
description: "Interactive initialization workflow: configure Makefile wrapper + COMMANDS.md, run make verify, and only clear the COMMANDS.md <fill> gate after successful verification."
metadata:
  short-description: Initialize canonical verify commands
---

## Purpose

Initialize a copied repository so agents can run canonical verification commands without guessing.

This skill standardizes Makefile targets as the command wrapper and makes `make verify` the completion gate.

## When to use

Use this skill when:
- `COMMANDS.md` still contains `<fill>` in the initialization verification line.
- The project has just been copied from this template.
- Canonical build/lint/analysis/test commands are not yet wired.

## Workflow

1. Check `COMMANDS.md` for `<fill>`.
   - If `<fill>` exists, initialization is required.
2. Infer likely tooling from repository evidence (lockfiles, CI config, package manager, compose files, scripts).
3. Ask at most 5 focused questions for missing decisions.
4. Update `Makefile` wrapper targets and `COMMANDS.md` command entries.
   - Keep `verified by agent: <fill>` unchanged at this step.
5. Run `make verify`.
6. Gate behavior:
   - **Success (exit 0):** replace `verified by agent: <fill>` with `yes (YYYY-MM-DD)`.
   - **Failure (non-zero):** keep `<fill>` and document failure reason + exact next steps to retry (in `INIT_REPORT.md` or appended notes in `COMMANDS.md`).

## Sudo / install policy

- Do not run privileged installs directly.
- If setup requires sudo/system packages, generate a reviewable script (for example `tools/bootstrap/install.sh`) and ask the user to run it.
- Avoid `curl | bash` patterns.

## Gotchas

- **ありがち:** `make verify` 未実行なのに `verified by agent` を yes にする。  
  **代わりに:** verify 成功 (exit 0) を確認した時だけ日付付きで yes に更新する。
- **ありがち:** `<fill>` が残っているのに初期化完了として扱う。  
  **代わりに:** `rg "<fill>" COMMANDS.md` で 0 件になるまで完了宣言しない。
- **ありがち:** コマンドを推測で埋めて実プロジェクトと乖離する。  
  **代わりに:** lockfile/CI/package manager/scripts の証拠を先に確認し、不足点だけ質問する。
- **ありがち:** verify 失敗時の次手順を書かずに作業を終える。  
  **代わりに:** 失敗理由と再実行手順を `INIT_REPORT.md` または `COMMANDS.md` に具体的に残す。

## Completion criteria

Initialization is complete **only when both are true**:
1. `COMMANDS.md` contains no `<fill>`.
2. `make verify` has been executed successfully (exit code 0) by the agent.

If `make verify` fails, initialization is **not complete** and `<fill>` must remain.

## Verify

- Run `make help` (should show wrapper targets and initialization status guidance).
- Run `make verify`.
- If successful, update verification line in `COMMANDS.md` and re-check `rg "<fill>" COMMANDS.md` returns no matches.
- If unsuccessful, preserve `<fill>` and leave actionable remediation notes.
