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
	printf '%s\n' '# Generic Index' '' 'See [[method-note]].' > $$tmpdir/index.md; \
	printf '%s\n' '# Method Note' '' 'A generic synthetic method note for checker smoke testing.' > $$tmpdir/method-note.md; \
	$(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode shared-mechanical-only $$tmpdir; \
	status=$$?; rm -rf $$tmpdir; exit $$status
	@tmpdir=$$(mktemp -d); \
	printf '%s\n' '---' 'title: Generic Case Note' 'note_type: case' '---' '# Generic Case Note' '' 'Synthetic frontmatter-only note without a tag convention.' > $$tmpdir/frontmatter-only.md; \
	$(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode shared-mechanical-only $$tmpdir; \
	status=$$?; rm -rf $$tmpdir; exit $$status
	@tmpdir=$$(mktemp -d); mkdir -p $$tmpdir/patterns; \
	printf '%s\n' '# Generic Index' '' 'See [[patterns/example-note]].' > $$tmpdir/index.md; \
	printf '%s\n' '# Example Note' '' 'Synthetic target note.' > $$tmpdir/patterns/example-note.md; \
	$(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode shared-mechanical-only $$tmpdir; \
	status=$$?; rm -rf $$tmpdir; exit $$status
	@tmpdir=$$(mktemp -d); mkdir -p $$tmpdir/a; \
	printf '%s\n' '# Generic Index' '' 'See [[missing/b]].' > $$tmpdir/index.md; \
	printf '%s\n' '# B' > $$tmpdir/a/b.md; \
	! $(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode shared-mechanical-only $$tmpdir; \
	status=$$?; rm -rf $$tmpdir; exit $$status
	@tmpdir=$$(mktemp -d); \
	printf '%s\n' '# 多言語の概念ノート' '' 'Generic synthetic concept note paragraph one describes a durable idea, practitioner context, relevant conditions, observable signals, decision support, misuse risk, transfer practice, review prompt, relation mapping, and application boundary without relying on fixed English section labels.' '' 'Generic synthetic concept note paragraph two describes a durable idea, practitioner context, relevant conditions, observable signals, decision support, misuse risk, transfer practice, review prompt, relation mapping, and application boundary without relying on fixed English section labels.' '' 'Generic synthetic concept note paragraph three describes a durable idea, practitioner context, relevant conditions, observable signals, decision support, misuse risk, transfer practice, review prompt, relation mapping, and application boundary without relying on fixed English section labels.' '' 'Generic synthetic concept note paragraph four describes a durable idea, practitioner context, relevant conditions, observable signals, decision support, misuse risk, transfer practice, review prompt, relation mapping, and application boundary without relying on fixed English section labels.' '' 'Generic synthetic concept note paragraph five describes a durable idea, practitioner context, relevant conditions, observable signals, decision support, misuse risk, transfer practice, review prompt, relation mapping, and application boundary without relying on fixed English section labels.' > $$tmpdir/textbook.md; \
	$(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode textbook-full-gate $$tmpdir; \
	status=$$?; rm -rf $$tmpdir; exit $$status
	@tmpdir=$$(mktemp -d); \
	printf '%s\n' '# Index' '' '- [[concept-a]]' '- [[method-b]]' > $$tmpdir/index.md; \
	printf '%s\n' '# Concept A' > $$tmpdir/concept-a.md; \
	printf '%s\n' '# Method B' > $$tmpdir/method-b.md; \
	$(PYTHON) .agents/skills/textbook-quality-gate/scripts/check_study_notes.py --mode textbook-full-gate $$tmpdir; \
	status=$$?; rm -rf $$tmpdir; exit $$status

test-integration:
	$(PYTHON) scripts/validate_skills.py
	$(PYTHON) scripts/validate_skill_trigger_evals.py
	$(PYTHON) scripts/report_skill_inventory.py --check --format text
	$(PYTHON) scripts/generate_agent_index.py --check
	git diff --check

verify: build-debug lint analysis test-unit test-integration
	@echo "Verification completed."
