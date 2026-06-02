from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAKEFILE = ROOT / "Makefile"

REQUIRED_TARGETS = (
    "test",
    "test-prepare",
    "test-unit",
    "test-int",
    "test-e2e",
    "check-core-contract",
    "check-bootstrap-smoke",
    "check-make-contract",
    "docs-guardrails",
    "fmt",
    "lint",
    "typecheck",
    "require-uv",
)
EXPECTED_TEST_DEPS = ("test-prepare", "test-unit", "test-int", "test-e2e")
EXPECTED_PREPARE_DEPS = (
    "fmt",
    "lint",
    "typecheck",
    "docs-guardrails",
    "check-make-contract",
    "check-bootstrap-smoke",
)
REQUIRE_UV_TARGETS = (
    "fmt",
    "lint",
    "typecheck",
    "check-bootstrap-smoke",
    "test-unit",
    "test-int",
    "test-e2e",
)
TARGET_MARKERS = {
    "fmt": (("$(UV) run ruff format --check .", "ruff format check"),),
    "lint": (("$(UV) run ruff check .", "ruff lint check"),),
    "typecheck": (("$(UV) run mypy src", "mypy typecheck"),),
    "docs-guardrails": (("scripts/guardrails.py", "docs guardrails script"),),
    "check-core-contract": (("scripts/check_core_contract.py", "core contract script"),),
    "check-bootstrap-smoke": (("scripts/check_bootstrap_smoke.py", "bootstrap smoke script"),),
    "check-make-contract": (("scripts/check_make_contract.py", "Makefile contract script"),),
    "require-uv": (
        ("uv is required for Python scaffold checks", "uv fail-safe message"),
        ("pyproject.toml is required for Python scaffold checks", "pyproject fail-safe message"),
    ),
    "test-int": (("KAN_EXTERNAL=0", "offline integration default"),),
    "test-e2e": (
        ("KAN_E2E=1", "explicit e2e marker"),
        ("HERMES_TEST_HOME", "isolated Hermes test home override"),
        ('DISCORD_TEST_TARGET=""', "Discord target isolation"),
    ),
}


def target_line(makefile: str, target: str) -> re.Match[str]:
    match = re.search(rf"^{re.escape(target)}\s*:(?P<deps>[^\n]*)$", makefile, re.MULTILINE)
    if not match:
        raise SystemExit(f"missing Makefile target: {target}")
    return match


def clean_dependency_text(raw_deps: str) -> str:
    without_recipe = raw_deps.split(";", 1)[0]
    return re.sub(r"#.*$", "", without_recipe).strip()


def target_dependencies(makefile: str, target: str) -> tuple[str, ...]:
    match = target_line(makefile, target)
    return tuple(clean_dependency_text(match.group("deps")).split())


def target_body(makefile: str, target: str) -> str:
    match = target_line(makefile, target)
    body_lines: list[str] = []
    raw_deps = match.group("deps")
    if ";" in raw_deps:
        body_lines.append(raw_deps.split(";", 1)[1])

    body_start = match.end()
    if body_start < len(makefile) and makefile[body_start] == "\n":
        body_start += 1

    for line in makefile[body_start:].splitlines():
        if not line.strip():
            continue
        if line.startswith(("\t", " ")):
            body_lines.append(line)
            continue
        break
    return "\n".join(body_lines)


def active_recipe_text(body: str) -> str:
    return "\n".join(
        line for line in body.splitlines() if not re.match(r"^\s*@?#", line)
    )


def require_target_contains(makefile: str, target: str, needle: str, label: str) -> None:
    body = active_recipe_text(target_body(makefile, target))
    if needle not in body:
        raise SystemExit(f"Makefile {target} missing {label}: {needle}")


def require_dependency(makefile: str, target: str, dependency: str) -> None:
    deps = target_dependencies(makefile, target)
    if dependency not in deps:
        raise SystemExit(f"Makefile {target} missing {dependency} dependency")


def require_target(makefile: str, target: str) -> None:
    target_dependencies(makefile, target)


def require_phony(makefile: str) -> None:
    phony_lines = re.findall(r"^\.PHONY\s*:(?P<targets>[^\n]*)$", makefile, re.MULTILINE)
    declared = {name for line in phony_lines for name in clean_dependency_text(line).split()}
    missing = sorted(set(REQUIRED_TARGETS).difference(declared))
    if missing:
        raise SystemExit(f"Makefile .PHONY missing targets: {missing}")


def main() -> None:
    makefile = MAKEFILE.read_text(encoding="utf-8")

    for target in REQUIRED_TARGETS:
        require_target(makefile, target)
    require_phony(makefile)

    test_deps = target_dependencies(makefile, "test")
    if test_deps != EXPECTED_TEST_DEPS:
        raise SystemExit(f"Makefile test deps mismatch: {test_deps} != {EXPECTED_TEST_DEPS}")

    prepare_deps = target_dependencies(makefile, "test-prepare")
    if prepare_deps != EXPECTED_PREPARE_DEPS:
        raise SystemExit(
            f"Makefile test-prepare deps mismatch: {prepare_deps} != {EXPECTED_PREPARE_DEPS}"
        )

    for target in REQUIRE_UV_TARGETS:
        require_dependency(makefile, target, "require-uv")

    for target, markers in TARGET_MARKERS.items():
        for needle, label in markers:
            require_target_contains(makefile, target, needle, label)

    print("check-make-contract: ok")


if __name__ == "__main__":
    main()
