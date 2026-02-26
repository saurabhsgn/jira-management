from __future__ import annotations

import json
from pathlib import Path


class ConfigError(RuntimeError):
    pass


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_config() -> dict:
    config_path = _project_root() / "config.json"
    if not config_path.exists():
        raise ConfigError("config.json not found. Create it at the project root.")

    data = json.loads(config_path.read_text(encoding="utf-8"))

    jira = data.get("jira") or {}
    confluence = data.get("confluence") or {}

    jira_base = (jira.get("base_url") or "").rstrip("/")
    jira_email = jira.get("email")
    jira_token = jira.get("api_token")

    if not jira_base or not jira_email or not jira_token or "REPLACE_ME" in jira_token:
        raise ConfigError("JIRA config is incomplete in config.json.")

    confluence_base = (confluence.get("base_url") or "").rstrip("/")
    confluence_email = confluence.get("email") or jira_email
    confluence_token = confluence.get("api_token") or jira_token

    if not confluence_base:
        confluence_base = f"{jira_base}/wiki"

    return {
        "jira": {
            "base_url": jira_base,
            "email": jira_email,
            "api_token": jira_token,
        },
        "confluence": {
            "base_url": confluence_base,
            "email": confluence_email,
            "api_token": confluence_token,
        },
    }
