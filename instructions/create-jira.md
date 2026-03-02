# Action: Create JIRA

## Goal

Create a new JIRA issue from structured inputs.

## Inputs

- Required: either
  - project_key, issue_type, summary, or
  - tech_spec_file (refined tech spec with mandatory sections completed)
- Optional: description, labels, assignee, priority, components, attachments

## Outputs

- JIRA issue key
- JIRA issue URL

## Steps

1) Validate required fields and sanitize text.
2) If `tech_spec_file` is provided, validate mandatory sections before create:
   - `6.2 Impacted Components, Classes, and Methods` has at least one row.
   - `9.2 Test Scenarios` has at least one row.
   - `11.1 Story Draft` has concrete Story Type + Summary.
   - `11.2 Acceptance Criteria (AC)` has at least one concrete AC.
   - Fail fast if any mandatory section is missing/incomplete.
3) Ask interactive questions for each required section from `templates/jira-story-template.md`.
4) Use provided reference pages (Confluence/Jira/docs) to prefill only confirmed details.
5) If any section remains incomplete, ask follow-up questions; do not assume.
6) Build the JIRA payload with optional fields.
7) Create the issue via JIRA API only after user confirmation.
8) Return issue key and URL.

## Script

- Script: scripts/create_jira.py
- Notes: Use authenticated JIRA REST API calls.
