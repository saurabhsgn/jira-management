# Action: Transition JIRA status

## Goal

Move a JIRA issue to a new workflow status.

## Inputs

- Required: issue_key, transition_id or status_name

## Outputs

- Updated issue key

## Steps

1) Validate issue key and transition input.
2) Lookup transition ID when status name is provided.
3) Perform transition via JIRA API.
4) Return confirmation.

## Script

- Script: scripts/transition_jira_status.py
- Notes: Use authenticated JIRA REST API calls.
