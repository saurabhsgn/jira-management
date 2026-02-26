# Action: Add JIRA labels

## Goal

Add one or more labels to a JIRA issue.

## Inputs

- Required: issue_key, labels

## Outputs

- Updated issue key

## Steps

1) Validate issue key and label list.
2) Add labels via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/add_jira_labels.py
- Notes: Preserve existing labels.
