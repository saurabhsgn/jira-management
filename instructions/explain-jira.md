# Action: Explain JIRA

## Goal

Summarize a JIRA issue into a human-friendly explanation.

## Inputs

- Required: issue_key
- Optional: tone (brief|detailed), focus (summary|risks|requirements)

## Outputs

- Natural language explanation

## Steps

1) Fetch issue details.
2) Extract key fields and context.
3) Generate a concise explanation.

## Script

- Script: scripts/explain_jira.py
- Notes: Use issue data from the pull action.
