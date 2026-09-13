.PHONY: verify lint test evidence
PYTHON ?= python3
.DEFAULT_GOAL := verify

verify:
	$(PYTHON) scripts/validate_playbook.py
	$(PYTHON) scripts/check_research_evidence.py --check-ledger
	$(PYTHON) -m unittest discover -s tests -v

lint:
	$(PYTHON) scripts/validate_playbook.py

test:
	$(PYTHON) -m unittest discover -s tests -v

evidence:
	$(PYTHON) scripts/check_research_evidence.py --check-ledger
