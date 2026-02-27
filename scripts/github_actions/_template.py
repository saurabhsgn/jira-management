"""Template action script for GitHub Actions tasks.

Usage:
  python scripts/github_actions/_template.py --help
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from urllib import error, parse, request


def _github_get(path: str, token: str) -> dict:
    req = request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "jira-management-template",
        },
        method="GET",
    )
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Template GitHub action script.")
    parser.add_argument("--repo", required=False, help="owner/repo")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    token = os.getenv("GITHUB_TOKEN")
    repo = args.repo or os.getenv("GITHUB_REPOSITORY")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    if not repo:
        raise SystemExit("repo is required (--repo or GITHUB_REPOSITORY)")

    try:
        result = {"status": "ok", "repo": repo}
        print(json.dumps(result, indent=2))
        return 0
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        print(json.dumps({"status": "error", "code": exc.code, "error": payload}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
