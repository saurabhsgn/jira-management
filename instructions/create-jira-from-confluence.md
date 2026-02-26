# Action: Create JIRA from Confluence

## Goal

Create a JIRA issue using details extracted from a Confluence page.

## Inputs

- Required: page_id, project_key, issue_type
- Optional: summary, labels, assignee

## Outputs

- JIRA issue key
- JIRA issue URL

## Steps

1) Read Confluence page content.
2) Extract summary, description, and criteria.
3) Build the JIRA issue payload.
4) Create the issue via JIRA API.

## Script

- Script: scripts/create_jira_from_confluence.py
- Notes: Use Confluence page as the source of truth.
