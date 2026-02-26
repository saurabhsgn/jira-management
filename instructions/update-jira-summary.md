# Action: Update JIRA summary

## Goal

Update the summary field for a JIRA issue.

## Inputs

- Required: issue_key, summary

## Outputs

- Updated issue key

## Steps

1) Validate issue key format.
2) Update the summary field via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/update_jira_summary.py
- Notes: Use authenticated JIRA REST API calls.
