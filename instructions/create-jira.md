# Action: Create JIRA

## Goal

Create a new JIRA issue from structured inputs.

## Inputs

- Required: project_key, issue_type, summary
- Optional: description, labels, assignee, priority, components, attachments

## Outputs

- JIRA issue key
- JIRA issue URL

## Steps

1) Validate required fields and sanitize text.
2) Build the JIRA payload with optional fields.
3) Create the issue via JIRA API.
4) Return issue key and URL.

## Script

- Script: scripts/create_jira.py
- Notes: Use authenticated JIRA REST API calls.
