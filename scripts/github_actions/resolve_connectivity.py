"""Resolve GitHub connectivity using SSH first, then HTTPS basic auth.

Usage:
  python scripts/github_actions/resolve_connectivity.py --help
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib import error, request

from _github_config import GitHubConfigError, github_token_from_env, load_github_config


def _probe_ssh(host: str, user: str, key_path: str) -> tuple[bool, str]:
    cmd = ["ssh", "-T", f"{user}@{host}", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8"]
    if key_path:
        cmd.extend(["-i", key_path])
    run = subprocess.run(cmd, capture_output=True, text=True)
    # GitHub can return non-zero while still proving auth; inspect output text.
    output = f"{run.stdout}\n{run.stderr}".lower()
    if "successfully authenticated" in output or "you've successfully authenticated" in output:
        return True, output.strip()
    return False, output.strip() or f"ssh exit code {run.returncode}"


def _probe_ssh_with_retries(
    host: str, user: str, key_path: str, retries: int
) -> tuple[bool, list[str]]:
    notes: list[str] = []
    for attempt in range(1, retries + 1):
        ok, reason = _probe_ssh(host, user, key_path)
        notes.append(f"ssh attempt {attempt}/{retries}: {reason}")
        if ok:
            return True, notes
    return False, notes


def _probe_https(owner: str, repo: str, username: str, token: str) -> tuple[bool, str]:
    url = f"https://api.github.com/repos/{owner}/{repo}"
    req = request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Basic "
            + __import__("base64").b64encode(f"{username}:{token}".encode("utf-8")).decode("utf-8"),
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "jira-management-gh-connectivity",
        },
        method="GET",
    )
    try:
        with request.urlopen(req, timeout=20):
            return True, "https basic auth probe passed"
    except error.HTTPError as exc:
        return False, f"https probe failed: {exc.code}"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Resolve connectivity method for GitHub repo operations.")
    parser.add_argument("--repo", required=True, help="Repository name (without owner).")
    parser.add_argument("--owner", required=False, help="Owner override; defaults from github_config.json.")
    parser.add_argument("--probe", action="store_true", help="Probe connectivity before selecting method.")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        cfg = load_github_config()
    except GitHubConfigError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, indent=2))
        return 1

    owner = args.owner or cfg.owner
    repo = args.repo

    ssh_url = f"git@{cfg.ssh_host}:{owner}/{repo}.git"
    https_url = f"https://github.com/{owner}/{repo}.git"

    selected_method = None
    reasons: list[str] = []

    for method in cfg.auth_order:
        if method == "ssh":
            ok, notes = _probe_ssh_with_retries(
                cfg.ssh_host,
                cfg.ssh_user,
                cfg.ssh_private_key_path,
                cfg.ssh_fallback_failures,
            )
            reasons.extend(notes)
            if ok:
                selected_method = "ssh"
                break
        elif method == "https_basic":
            try:
                token = github_token_from_env(cfg.https_token_env)
            except GitHubConfigError as exc:
                reasons.append(f"https_basic: {exc}")
                continue
            if not args.probe:
                selected_method = "https_basic"
                break
            ok, reason = _probe_https(owner, repo, cfg.https_username, token)
            reasons.append(f"https_basic: {reason}")
            if ok:
                selected_method = "https_basic"
                break
        else:
            reasons.append(f"{method}: unsupported auth method")

    if not selected_method:
        print(
            json.dumps(
                {
                    "status": "error",
                    "owner": owner,
                    "repo": repo,
                    "error": "No connectivity method succeeded.",
                    "reasons": reasons,
                },
                indent=2,
            )
        )
        return 1

    payload = {
        "status": "ok",
        "owner": owner,
        "repo": repo,
        "method": selected_method,
        "git_remote": ssh_url if selected_method == "ssh" else https_url,
        "notes": reasons,
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
