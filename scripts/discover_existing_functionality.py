"""Discover existing functionality from repository files.

Usage:
  python scripts/discover_existing_functionality.py --help
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


EXCLUDED_DIRS = {".git", ".idea", ".venv", "__pycache__", "node_modules"}
FRONTEND_HINTS = {"react", "next", "angular", "vue", "frontend", "ui", "web", "styles"}
BACKEND_HINTS = {"api", "server", "backend", "service", "controller", "model", "scripts"}
MOBILE_HINTS = {"android", "ios", "mobile", "react-native", "flutter"}
UIUX_HINTS = {"figma", "design", "wireframe", "ux", "ui", "prototype"}
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".kt",
    ".swift",
    ".go",
    ".rb",
    ".php",
    ".cs",
    ".html",
    ".css",
    ".scss",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover functionality from local codebase.")
    parser.add_argument("--root", default=".", help="Project root to scan.")
    parser.add_argument("--max-paths", type=int, default=20, help="Max sample paths per category.")
    return parser


def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_DIRS for part in path.parts)


def _classify(path: Path) -> set[str]:
    tokens = {token.lower() for token in path.parts}
    categories = set()

    if tokens & FRONTEND_HINTS or path.suffix.lower() in {".jsx", ".tsx", ".css", ".scss"}:
        categories.add("frontend")
    if tokens & BACKEND_HINTS or path.suffix.lower() in {".py", ".java", ".go", ".rb", ".cs"}:
        categories.add("backend")
    if tokens & MOBILE_HINTS or path.suffix.lower() in {".kt", ".swift"}:
        categories.add("mobile")
    if tokens & UIUX_HINTS:
        categories.add("uiux")

    if not categories and path.suffix.lower() in CODE_EXTENSIONS:
        categories.add("backend")
    return categories


def _scan(root: Path, max_paths: int) -> dict:
    categories: dict[str, list[str]] = {
        "frontend": [],
        "backend": [],
        "mobile": [],
        "uiux": [],
    }
    total_files = 0
    code_files = 0

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if _is_excluded(path):
            continue

        total_files += 1
        if path.suffix.lower() in CODE_EXTENSIONS:
            code_files += 1

        for category in _classify(path):
            if len(categories[category]) < max_paths:
                categories[category].append(str(path.relative_to(root)))

    return {
        "root": str(root.resolve()),
        "total_files": total_files,
        "code_files": code_files,
        "categories": categories,
    }


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    root = Path(args.root).resolve()

    result = _scan(root, args.max_paths)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

