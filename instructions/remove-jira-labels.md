# Action: Remove JIRA labels

## Goal

Remove one or more labels from a JIRA issue.

## Inputs

- Required: issue_key, labels

## Outputs

- Updated issue key

## Steps

1) Validate issue key and label list.
2) Remove labels via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/remove_jira_labels.py
- Notes: Only remove provided labels.
