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
2) Ask interactive questions for each required section from `templates/jira-story-template.md`.
3) Use provided reference pages (Confluence/Jira/docs) to prefill only confirmed details.
4) If any section remains incomplete, ask follow-up questions; do not assume.
5) Build the JIRA payload with optional fields.
6) Create the issue via JIRA API only after user confirmation.
7) Return issue key and URL.

## Script

- Script: scripts/create_jira.py
- Notes: Use authenticated JIRA REST API calls.
