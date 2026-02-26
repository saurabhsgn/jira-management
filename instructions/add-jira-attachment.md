# Action: Add JIRA attachment

## Goal

Attach a file to a JIRA issue.

## Inputs

- Required: issue_key, file_path

## Outputs

- Attachment ID
- Updated issue key

## Steps

1) Validate issue key and file path.
2) Upload attachment via JIRA API.
3) Return attachment ID.

## Script

- Script: scripts/add_jira_attachment.py
- Notes: Use X-Atlassian-Token: no-check header.
