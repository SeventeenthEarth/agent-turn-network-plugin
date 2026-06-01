SHELL := /bin/sh

.PHONY: test test-prepare test-unit test-int test-e2e docs-guardrails check-core-contract fmt lint typecheck

test: test-prepare test-unit test-int test-e2e

# Preparation gate: local-only checks that never contact Hermes/Discord or other external services.
test-prepare: fmt lint typecheck docs-guardrails

fmt:
	@if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then \
		uv run ruff format --check .; \
	else \
		echo "fmt: uv/pyproject unavailable; skipped until Python plugin scaffold exists"; \
	fi

lint:
	@if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then \
		uv run ruff check .; \
	else \
		echo "lint: uv/pyproject unavailable; skipped until Python plugin scaffold exists"; \
	fi

typecheck:
	@if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then \
		uv run mypy src; \
	else \
		echo "typecheck: uv/pyproject unavailable; skipped until Python plugin scaffold exists"; \
	fi

docs-guardrails:
	@python3 scripts/guardrails.py

check-core-contract:
	@python3 scripts/check_core_contract.py

test-unit:
	@if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then \
		uv run pytest tests/unit; \
	else \
		echo "test-unit: no Python scaffold yet; docs-only pass"; \
	fi

test-int:
	@if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then \
		KAN_EXTERNAL=0 uv run pytest tests/integration; \
	else \
		echo "test-int: no Python scaffold yet; docs-only pass"; \
	fi

test-e2e:
	@if command -v uv >/dev/null 2>&1 && [ -f pyproject.toml ]; then \
		KAN_E2E=1 HERMES_HOME="$${HERMES_TEST_HOME:-$$(mktemp -d)}" DISCORD_TEST_TARGET="$${DISCORD_TEST_TARGET:-}" uv run pytest tests/e2e; \
	else \
		echo "test-e2e: no Python scaffold yet; docs-only pass"; \
	fi
