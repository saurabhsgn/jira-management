# Action: Update JIRA comments

## Goal

Add a new comment or edit an existing comment on a JIRA issue.

## Inputs

- Required: issue_key, comment
- Optional: comment_id, mode (add|update)

## Outputs

- Comment ID
- Updated issue key

## Steps

1) Validate issue key format.
2) If update, validate comment ID exists.
3) Add or update comment via JIRA API.
4) Return confirmation.

## Script

- Script: scripts/update_jira_comments.py
- Notes: Use authenticated JIRA REST API calls.
