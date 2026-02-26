# Action: Create JIRA subtask

## Goal

Create a subtask under an existing JIRA issue.

## Inputs

- Required: parent_issue_key, summary

## Outputs

- Subtask issue key

## Steps

1) Validate parent issue and summary.
2) Build subtask payload.
3) Create subtask via JIRA API.

## Script

- Script: scripts/create_jira_subtask.py
- Notes: Issue type must be a subtask type.
