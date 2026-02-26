# Action: Add JIRA worklog

## Goal

Add a worklog entry to a JIRA issue.

## Inputs

- Required: issue_key, time_spent, comment

## Outputs

- Worklog ID

## Steps

1) Validate issue key and time format.
2) Add worklog via JIRA API.
3) Return worklog ID.

## Script

- Script: scripts/add_jira_worklog.py
- Notes: Time format example: 1h 30m.
