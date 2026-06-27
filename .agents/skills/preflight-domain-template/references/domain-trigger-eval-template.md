# Domain Trigger Eval Template

Create `evals/skill-triggers/preflight-<domain>.json` with two positive and
two negative cases. Positives should ask for preflight preparation before risky
or multi-agent work. Negatives should let ordinary implementation proceed when
AGENTS/context/test routing are already current.

```json
{
  "version": 1,
  "cases": [
    {
      "id": "preflight-<domain>-positive-prep-before-risky-work",
      "prompt": "Before implementing <domain-risk>, prepare <domain> invariants, first docs/files, test routing, approvals, reviewers, and handoff context.",
      "should_trigger": [
        "preflight-<domain>"
      ],
      "should_not_trigger": [
        "test-driven-development"
      ],
      "expected_output_contains": [
        "Domain preflight result",
        "Domain invariants",
        "Test routing"
      ]
    },
    {
      "id": "preflight-<domain>-positive-multi-agent-investigation",
      "prompt": "Prepare <domain> preflight context before assigning subagents to investigate <domain-risk> across docs, files, tests, approvals, and handoff fragments.",
      "should_trigger": [
        "preflight-<domain>"
      ],
      "should_not_trigger": [
        "project-initialization"
      ],
      "expected_output_contains": [
        "Confirmed facts",
        "Inferred facts",
        "Unknowns"
      ]
    },
    {
      "id": "preflight-<domain>-negative-current-context",
      "prompt": "Fix <domain bug>. AGENTS.md, .agent/ctx/<domain>.md, and targeted tests are already current.",
      "should_trigger": [],
      "should_not_trigger": [
        "preflight-<domain>"
      ],
      "expected_decisions": [
        "Domain preflight is skipped because context and test routing are already current"
      ]
    },
    {
      "id": "preflight-<domain>-negative-unrelated-small-change",
      "prompt": "Make a one-line copy edit in unrelated documentation.",
      "should_trigger": [],
      "should_not_trigger": [
        "preflight-<domain>",
        "preflight-engineering"
      ],
      "expected_decisions": [
        "Domain preflight is not needed for unrelated small documentation work"
      ]
    }
  ]
}
```
