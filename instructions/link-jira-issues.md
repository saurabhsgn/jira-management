# Action: Link JIRA issues

## Goal

Create a link between two JIRA issues.

## Inputs

- Required: inward_issue_key, outward_issue_key, link_type

## Outputs

- Link ID

## Steps

1) Validate issue keys and link type.
2) Create issue link via JIRA API.
3) Return link ID.

## Script

- Script: scripts/link_jira_issues.py
- Notes: Link types depend on JIRA configuration.
