SHELL := /bin/sh
PYTHON ?= python3
UV ?= uv

.PHONY: test test-prepare test-unit test-int test-e2e check-core-contract check-bootstrap-smoke check-make-contract docs-guardrails fmt lint typecheck require-uv

test: test-prepare test-unit test-int test-e2e

# Preparation gate: local-only checks that never contact Hermes/Discord or other external services.
test-prepare: fmt lint typecheck docs-guardrails check-make-contract check-bootstrap-smoke

require-uv:
	@if ! command -v $(UV) >/dev/null 2>&1; then \
		echo "require-uv: uv is required for Python scaffold checks; install uv or set UV=/path/to/uv" >&2; \
		exit 2; \
	fi
	@if [ ! -f pyproject.toml ]; then \
		echo "require-uv: pyproject.toml is required for Python scaffold checks" >&2; \
		exit 2; \
	fi

fmt: require-uv
	@$(UV) run ruff format --check .

lint: require-uv
	@$(UV) run ruff check .

typecheck: require-uv
	@$(UV) run mypy src

docs-guardrails:
	@$(PYTHON) scripts/guardrails.py

check-make-contract:
	@$(PYTHON) scripts/check_make_contract.py

check-core-contract:
	@$(PYTHON) scripts/check_core_contract.py

check-bootstrap-smoke: require-uv
	@$(UV) run python scripts/check_bootstrap_smoke.py

test-unit: require-uv
	@$(UV) run pytest tests/unit

test-int: require-uv
	@KAN_EXTERNAL=0 $(UV) run pytest tests/integration

test-e2e: require-uv
	@KAN_E2E=1 HERMES_HOME="$${HERMES_TEST_HOME:-$$(mktemp -d)}" DISCORD_TEST_TARGET="" $(UV) run pytest tests/e2e
