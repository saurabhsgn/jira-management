# Action: Get GitHub workflow runs

## Goal

Fetch workflow runs for a repository or a specific workflow.

## Inputs

- Optional: repo (`owner/repo`), workflow_id, branch, status, per_page

## Outputs

- Workflow runs payload

## Steps

1) Resolve repository from CLI or `GITHUB_REPOSITORY`.
2) Call GitHub Actions API for workflow runs.
3) Apply optional filters and return results.

## Script

- Script: scripts/github_actions/get_workflow_runs.py
- Notes: Requires `GITHUB_TOKEN`.
