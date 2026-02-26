# Action: Create acceptance criteria from Confluence

## Goal

Generate acceptance criteria using a Confluence page.

## Inputs

- Required: page_id
- Optional: style (gherkin|bullets)

## Outputs

- Acceptance criteria text

## Steps

1) Read page content.
2) Identify requirements and constraints.
3) Generate acceptance criteria.

## Script

- Script: scripts/create_acceptance_criteria_from_confluence.py
- Notes: Prefer Gherkin when style is gherkin.
