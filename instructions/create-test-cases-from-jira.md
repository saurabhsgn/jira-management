# Action: Create test cases from JIRA

## Goal

Generate test cases based on JIRA description and acceptance criteria.

## Inputs

- Required: issue_key
- Optional: format (markdown|json), include_edge_cases (true|false)

## Outputs

- Test cases content

## Steps

1) Pull issue details.
2) Extract requirements and acceptance criteria.
3) Draft test cases and expected results.

## Script

- Script: scripts/create_test_cases_from_jira.py
- Notes: Use JIRA description as the primary source.
