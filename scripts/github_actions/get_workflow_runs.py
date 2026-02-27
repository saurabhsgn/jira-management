"""Action script: get_workflow_runs.

Usage:
  python scripts/github_actions/get_workflow_runs.py --help
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
            "User-Agent": "jira-management-gh-actions",
        },
        method="GET",
    )
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Get GitHub workflow runs.")
    parser.add_argument("--repo", required=False, help="owner/repo")
    parser.add_argument("--workflow-id", required=False)
    parser.add_argument("--branch", required=False)
    parser.add_argument("--status", required=False)
    parser.add_argument("--per-page", required=False, type=int, default=30)
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
        params = {"per_page": args.per_page}
        if args.branch:
            params["branch"] = args.branch
        if args.status:
            params["status"] = args.status

        query = parse.urlencode(params)
        if args.workflow_id:
            path = f"/repos/{repo}/actions/workflows/{args.workflow_id}/runs?{query}"
        else:
            path = f"/repos/{repo}/actions/runs?{query}"

        data = _github_get(path, token)
        result = {
            "status": "ok",
            "repo": repo,
            "total_count": data.get("total_count", 0),
            "runs": [
                {
                    "id": run.get("id"),
                    "name": run.get("name"),
                    "event": run.get("event"),
                    "status": run.get("status"),
                    "conclusion": run.get("conclusion"),
                    "head_branch": run.get("head_branch"),
                    "created_at": run.get("created_at"),
                    "html_url": run.get("html_url"),
                }
                for run in data.get("workflow_runs", [])
            ],
        }
        print(json.dumps(result, indent=2))
        return 0
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        print(json.dumps({"status": "error", "code": exc.code, "error": payload}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
