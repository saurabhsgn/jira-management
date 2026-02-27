from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


class GitHubConfigError(RuntimeError):
    pass


@dataclass
class GitHubConnectivityConfig:
    owner: str
    auth_order: list[str]
    ssh_host: str
    ssh_user: str
    ssh_private_key_path: str
    ssh_fallback_failures: int
    https_username: str
    https_token_env: str
    default_branch: str


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_github_config() -> GitHubConnectivityConfig:
    config_path = _project_root() / "github_config.json"
    if not config_path.exists():
        raise GitHubConfigError("github_config.json not found at project root.")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    github = data.get("github") or {}

    owner = (github.get("owner") or "").strip()
    auth_order = github.get("auth_order") or ["ssh", "https_basic"]

    ssh = github.get("ssh") or {}
    ssh_host = (ssh.get("host") or "github.com").strip()
    ssh_user = (ssh.get("user") or "git").strip()
    ssh_private_key_path = (ssh.get("private_key_path") or "").strip()
    ssh_fallback_failures = int(ssh.get("fallback_failures") or 5)

    https_basic = github.get("https_basic") or {}
    https_username = (https_basic.get("username") or "").strip()
    https_token_env = (https_basic.get("token_env") or "GITHUB_TOKEN").strip()

    defaults = github.get("defaults") or {}
    default_branch = (defaults.get("branch") or "main").strip()

    if not owner or owner == "REPLACE_ME":
        raise GitHubConfigError("github.owner is required in github_config.json.")
    if not isinstance(auth_order, list) or not auth_order:
        raise GitHubConfigError("github.auth_order must be a non-empty list.")
    if ssh_fallback_failures < 1:
        raise GitHubConfigError("github.ssh.fallback_failures must be >= 1.")

    return GitHubConnectivityConfig(
        owner=owner,
        auth_order=[str(x).strip() for x in auth_order if str(x).strip()],
        ssh_host=ssh_host,
        ssh_user=ssh_user,
        ssh_private_key_path=ssh_private_key_path,
        ssh_fallback_failures=ssh_fallback_failures,
        https_username=https_username,
        https_token_env=https_token_env,
        default_branch=default_branch,
    )


def github_token_from_env(token_env: str) -> str:
    token = os.getenv(token_env, "").strip()
    if not token:
        raise GitHubConfigError(f"Environment variable {token_env} is required for HTTPS basic auth.")
    return token
