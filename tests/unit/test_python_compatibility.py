from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def python_files() -> list[Path]:
    roots = [ROOT / "__init__.py", ROOT / "scripts", ROOT / "src", ROOT / "tests"]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        files.extend(
            path
            for path in root.rglob("*.py")
            if "__pycache__" not in path.parts and ".venv" not in path.parts
        )
    return sorted(files)


def test_repository_python_sources_parse_as_python_311() -> None:
    for path in python_files():
        ast.parse(
            path.read_text(encoding="utf-8"),
            filename=str(path.relative_to(ROOT)),
            feature_version=(3, 11),
        )
