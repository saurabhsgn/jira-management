# Action: Resolve GitHub connectivity

## Goal

Resolve Git connectivity mode for a repository using configured auth priority.

## Inputs

- Required: repo
- Optional: owner, probe

## Outputs

- Selected method (`ssh` or `https_basic`) and git remote URL

## Steps

1) Load `github_config.json`.
2) Evaluate auth methods in `auth_order`.
3) Use SSH first when configured; if SSH fails continuously `fallback_failures` times (default `5`), fallback to HTTPS basic auth.
4) Return selected method and remote URL.

## Script

- Script: scripts/github_actions/resolve_connectivity.py
- Config: github_config.json
