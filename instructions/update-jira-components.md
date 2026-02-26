# Action: Update JIRA components

## Goal

Set or update components on a JIRA issue.

## Inputs

- Required: issue_key, components

## Outputs

- Updated issue key

## Steps

1) Validate issue key and component list.
2) Update components via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/update_jira_components.py
- Notes: Support replace or merge mode if needed.
