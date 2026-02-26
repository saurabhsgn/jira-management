# Action: Assign JIRA issue

## Goal

Assign a JIRA issue to a user.

## Inputs

- Required: issue_key, assignee

## Outputs

- Updated issue key

## Steps

1) Validate issue key and assignee.
2) Update assignee via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/assign_jira_issue.py
- Notes: Use accountId for cloud instances when required.
