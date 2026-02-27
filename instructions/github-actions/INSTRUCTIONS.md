# GitHub Actions Instruction Index

This file is the entry point for GitHub Actions automation instructions. Each action has a dedicated instruction file and a matching script.

## Setup

- Export `GITHUB_TOKEN` with permissions to read workflows and runs.
- Pass `--repo owner/repo` to scripts, or set `GITHUB_REPOSITORY`.

## Actions

| Action | Instruction | Script |
| --- | --- | --- |
| List GitHub workflows | instructions/github-actions/list-workflows.md | scripts/github_actions/list_workflows.py |
| Get GitHub workflow runs | instructions/github-actions/get-workflow-runs.md | scripts/github_actions/get_workflow_runs.py |
| Resolve GitHub connectivity | instructions/github-actions/resolve-connectivity.md | scripts/github_actions/resolve_connectivity.py |

## Add a new action

1) Copy `instructions/github-actions/_template.md` to a new file in `instructions/github-actions/`.
2) Copy `scripts/github_actions/_template.py` to a new script in `scripts/github_actions/`.
3) Add the new action to this file under `Actions`.

## Conventions

- One instruction file per action.
- One script per action.
- Keep filenames kebab-case in `instructions/github-actions/` and snake_case in `scripts/github_actions/`.
- Scripts should accept CLI flags for required inputs and print machine-readable JSON.
