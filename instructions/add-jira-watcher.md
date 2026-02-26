# Action: Add JIRA watcher

## Goal

Add a watcher to a JIRA issue.

## Inputs

- Required: issue_key, watcher

## Outputs

- Updated issue key

## Steps

1) Validate issue key and watcher.
2) Add watcher via JIRA API.
3) Return confirmation.

## Script

- Script: scripts/add_jira_watcher.py
- Notes: Use accountId for cloud instances when required.
