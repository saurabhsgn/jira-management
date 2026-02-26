# Action: Set JIRA due date

## Goal

Set or update the due date for a JIRA issue.

## Inputs

- Required: issue_key, due_date

## Outputs

- Updated issue key

## Steps

1) Validate issue key and date format.
2) Update due date via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/set_jira_due_date.py
- Notes: Use ISO date format: YYYY-MM-DD.
