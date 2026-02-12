.PHONY: help build-debug build-release format lint analysis test-unit test-integration verify

.DEFAULT_GOAL := help

define require_initialized
	@printf "[uninitialized] target '%s' is not configured yet.\n" "$(1)"
	@printf '%s\n' "Run the project initialization wizard (project-initialization or /initialize),"
	@printf '%s\n' "then rerun 'make verify'."
	@exit 2
endef

help:
	@echo "Project command wrapper (initialization required)"
	@echo ""
	@echo "Available targets:"
	@echo "  make build-debug"
	@echo "  make build-release"
	@echo "  make format"
	@echo "  make lint"
	@echo "  make analysis"
	@echo "  make test-unit"
	@echo "  make test-integration"
	@echo "  make verify"
	@echo ""
	@echo "Status: uninitialized template. Run project-initialization or /initialize."

build-debug:
	$(call require_initialized,build-debug)

build-release:
	$(call require_initialized,build-release)

format:
	$(call require_initialized,format)

lint:
	$(call require_initialized,lint)

analysis:
	$(call require_initialized,analysis)

test-unit:
	$(call require_initialized,test-unit)

test-integration:
	$(call require_initialized,test-integration)

verify: build-debug lint analysis test-unit
	@echo "Verification completed."
