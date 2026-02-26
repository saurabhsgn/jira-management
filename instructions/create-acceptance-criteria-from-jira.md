# Action: Create acceptance criteria from JIRA

## Goal

Generate acceptance criteria using the JIRA description.

## Inputs

- Required: issue_key
- Optional: style (gherkin|bullets)

## Outputs

- Acceptance criteria text

## Steps

1) Pull issue description.
2) Identify requirements and constraints.
3) Generate acceptance criteria.

## Script

- Script: scripts/create_acceptance_criteria_from_jira.py
- Notes: Prefer Gherkin when style is gherkin.
