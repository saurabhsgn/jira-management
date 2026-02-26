# Action: Delete JIRA issue

## Goal

Delete a JIRA issue.

## Inputs

- Required: issue_key

## Outputs

- Deleted issue key

## Steps

1) Validate issue key.
2) Delete issue via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/delete_jira_issue.py
- Notes: This action is destructive.
