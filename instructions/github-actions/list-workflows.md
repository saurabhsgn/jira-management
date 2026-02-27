# Action: List GitHub workflows

## Goal

List all workflows configured in a repository.

## Inputs

- Optional: repo (`owner/repo`) and per_page

## Outputs

- Workflow list payload

## Steps

1) Resolve repository from CLI or `GITHUB_REPOSITORY`.
2) Call GitHub Actions API for workflows.
3) Return workflow names, IDs, and states.

## Script

- Script: scripts/github_actions/list_workflows.py
- Notes: Requires `GITHUB_TOKEN`.
