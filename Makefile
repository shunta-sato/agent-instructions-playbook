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
	@echo "  make lint              # validate skill metadata and trigger evals"
	@echo "  make analysis          # validate skill inventory report"
	@echo "  make test-unit         # smoke-test the generic study-note checker"
	@echo "  make test-integration  # run repository skill/index validation chain"
	@echo "  make verify            # run the canonical verification chain"

build-debug:
	$(PYTHON) -m py_compile scripts/*.py .agents/skills/textbook-quality-gate/scripts/check_study_notes.py

build-release:
	$(PYTHON) -m py_compile scripts/*.py .agents/skills/textbook-quality-gate/scripts/check_study_notes.py

format:
	$(PYTHON) scripts/generate_agent_index.py --check

git-diff-check:
	git diff --check

lint:
	$(PYTHON) scripts/validate_skills.py
	$(PYTHON) scripts/validate_skill_trigger_evals.py

analysis:
	$(PYTHON) scripts/report_skill_inventory.py --check --format text

test-unit:
	$(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --help >/dev/null
	@tmpdir=$$(mktemp -d); \
	printf '%s\n' '---' 'tags: [study]' '---' '# Generic Index' '' 'See [[method-note]].' > $$tmpdir/index.md; \
	printf '%s\n' '# Method Note' '' 'A generic synthetic method note for checker smoke testing.' > $$tmpdir/method-note.md; \
	$(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode shared-mechanical-only $$tmpdir; \
	status=$$?; rm -rf $$tmpdir; exit $$status

test-integration:
	$(PYTHON) scripts/validate_skills.py
	$(PYTHON) scripts/validate_skill_trigger_evals.py
	$(PYTHON) scripts/report_skill_inventory.py --check --format text
	$(PYTHON) scripts/generate_agent_index.py --check
	git diff --check

verify: build-debug lint analysis test-unit test-integration
	@echo "Verification completed."
