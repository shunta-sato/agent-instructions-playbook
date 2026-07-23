.PHONY: help build-debug build-release format lint analysis test-unit test-integration verify

.DEFAULT_GOAL := help

PYTHON ?= python3

help:
	@echo "Project command wrapper"
	@echo ""
	@echo "Available targets:"
	@echo "  make build-debug       # compile repository Python scripts"
	@echo "  make build-release     # compile repository Python scripts"
	@echo "  make format            # verify generated indexes are current"
	@echo "  make lint              # validate skill metadata and eval seeds"
	@echo "  make analysis          # validate skill inventory report"
	@echo "  make test-unit         # no repository-local unit tests configured"
	@echo "  make test-integration  # run repository skill/index validation chain"
	@echo "  make verify            # run the canonical verification chain"

build-debug:
	$(PYTHON) -m py_compile scripts/*.py

build-release:
	$(PYTHON) -m py_compile scripts/*.py

format:
	$(PYTHON) scripts/generate_agent_index.py --check

git-diff-check:
	git diff --check

lint:
	$(PYTHON) scripts/validate_skills.py
	$(PYTHON) scripts/update_skill_requires.py --check
	$(PYTHON) scripts/sync_claude_skills.py --check
	$(PYTHON) scripts/generate_route_lockfile.py --check
	$(PYTHON) scripts/validate_skill_trigger_evals.py
	$(PYTHON) scripts/validate_skill_behavior_evals.py
	$(PYTHON) scripts/validate_function_design_protocol.py
	$(PYTHON) scripts/validate_model_routing.py
	$(PYTHON) scripts/validate_model_routing_evals.py
	$(PYTHON) scripts/check_research_evidence.py --check-ledger
	$(PYTHON) scripts/check_context_budget.py

analysis:
	$(PYTHON) scripts/report_skill_inventory.py --check --format text

test-unit:
	$(PYTHON) -m unittest discover -s tests

test-integration:
	$(PYTHON) scripts/validate_skills.py
	$(PYTHON) scripts/update_skill_requires.py --check
	$(PYTHON) scripts/sync_claude_skills.py --check
	$(PYTHON) scripts/generate_route_lockfile.py --check
	$(PYTHON) scripts/validate_skill_trigger_evals.py
	$(PYTHON) scripts/validate_skill_behavior_evals.py
	$(PYTHON) scripts/validate_function_design_protocol.py
	$(PYTHON) scripts/validate_model_routing.py
	$(PYTHON) scripts/validate_model_routing_evals.py
	$(PYTHON) scripts/check_research_evidence.py --check-ledger
	$(PYTHON) scripts/check_context_budget.py
	$(PYTHON) scripts/report_skill_inventory.py --check --format text
	$(PYTHON) scripts/generate_agent_index.py --check
	git diff --check

verify: build-debug lint analysis test-unit test-integration
	@echo "Verification completed."
