# Action: Update JIRA description

## Goal

Replace or append to the description of a JIRA issue.

## Inputs

- Required: issue_key, description
- Optional: mode (replace|append)

## Outputs

- Updated issue key

## Steps

1) Validate issue key format.
2) If append, fetch current description.
3) Update description via JIRA API.
4) Return confirmation.

## Script

- Script: scripts/update_jira_description.py
- Notes: Use authenticated JIRA REST API calls.
