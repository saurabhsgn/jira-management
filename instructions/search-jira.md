# Action: Search JIRA

## Goal

Search JIRA issues using JQL.

## Inputs

- Required: jql

## Outputs

- Issue list

## Steps

1) Validate JQL query.
2) Execute search via JIRA API.
3) Normalize results and return.

## Script

- Script: scripts/search_jira.py
- Notes: Support pagination when needed.
