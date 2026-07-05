# Function Design Eval Reports

Store manual or semi-automated agent-run reports here:

```text
reports/function-design-evals/YYYYMMDD-HHMMSS/<scenario>/
  task.md
  transcript.md or summary.md
  diff.patch
  oracle-output.txt
  verification-output.txt
  decision.json
```

These reports compare agent behavior over time. They must include oracle output and verification output; final-response prose alone is not sufficient evidence.
