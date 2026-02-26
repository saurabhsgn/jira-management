# Action: Get JIRA changelog

## Goal

Retrieve the changelog for a JIRA issue.

## Inputs

- Required: issue_key

## Outputs

- Changelog entries

## Steps

1) Validate issue key.
2) Fetch changelog via JIRA API.
3) Normalize and return entries.

## Script

- Script: scripts/get_jira_changelog.py
- Notes: Support pagination when needed.
