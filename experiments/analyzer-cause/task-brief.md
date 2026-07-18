# Task brief: analyzer-slowness-cause

- Task name: analyzer-slowness-cause — identify the dominant cause of a performance problem, with evidence.
- Mode: research (explicitly declared).
- Target project: /private/tmp/claude-501/-Users-shuntasato-workspace-agent-instructions-playbook/3ef6bea6-2f2e-4dff-b2ae-392b4019d6ac/scratchpad/fixture-a-research — analyzer.py, gen_data.py, app.log. Canonical commands: `python3 gen_data.py 300000` (regenerate data), `python3 analyzer.py app.log` (run + prints elapsed).
- Governing playbook: /private/tmp/claude-501/-Users-shuntasato-workspace-agent-instructions-playbook/3ef6bea6-2f2e-4dff-b2ae-392b4019d6ac/scratchpad/wt-research-os — its AGENTS.md, research-workflow, experiment-loop skills.
- Constraints: no git branch/checkout/commit anywhere; do not modify the target project's files; probe code under experiments/analyzer-cause/; ledger records only via scripts/research_run.py.
- Allowed files: new files under experiments/analyzer-cause/; research ledger/artifacts via the designated runner only.
- Task: analyzer.py takes ~7.5s on the 300k-line app.log. Identify the DOMINANT cause of the slowness (the single change that would recover most of the time), with evidence. Do not fix it. Several plausible suspects exist; be right, not fast to guess.
- Required in final report: (a) dominant cause + evidence; (b) chronological list of every shell command executed; (c) every file created, with line counts.
