# Action: Set JIRA priority

## Goal

Update the priority of a JIRA issue.

## Inputs

- Required: issue_key, priority

## Outputs

- Updated issue key

## Steps

1) Validate issue key and priority name or ID.
2) Update priority via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/set_jira_priority.py
- Notes: Map priority name to ID if needed.
