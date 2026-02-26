# Action: Pull JIRA

## Goal

Fetch a JIRA issue and return a normalized summary of its fields.

## Inputs

- Required: issue_key
- Optional: fields, include_comments (true|false)

## Outputs

- Issue data payload

## Steps

1) Validate issue key format.
2) Fetch issue details via JIRA API.
3) Normalize fields into a stable schema.
4) Return issue data.

## Script

- Script: scripts/pull_jira.py
- Notes: Use authenticated JIRA REST API calls.
