# Contributor commands

`make verify` is the canonical local/CI chain:

1. `python3 scripts/validate_playbook.py`
2. `python3 scripts/check_research_evidence.py --check-ledger`
3. `python3 -m unittest discover -s tests -v`

`make test` runs only the test suite. `make lint` runs only structural/syntax validation.
All tests use local disposable fixtures; no live model API or production target is called.
An executed test is distinct from a live model evaluation. The latter requires a separately
authorized adapter and environment; see `evals/README.md`.
