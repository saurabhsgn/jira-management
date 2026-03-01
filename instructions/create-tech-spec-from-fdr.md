# Action: Create Technical Specification from FDR

## Goal

Create a draft technical specification from a Functional Design Requirement (FDR) using:
- interactive clarification questions,
- Confluence/Jira/codebase discovery (parallel),
- story-level Jira draft planning.

## Inputs

- Required: project_name, jira_project_key
- Required: one FDR source
  - plain text, or
  - file path, or
  - PDF path, or
  - Confluence page URL
- Optional: additional open questions captured interactively

## Outputs

- Tech spec draft markdown (`outputs/tech_spec_draft.md`)
- Jira story draft plan (`outputs/jira_plan_draft.json`)

## Workflow Rules

1) Ask project name first (simple word).
2) Do not assume missing details; ask follow-up questions.
3) Prefer parallel discovery across Confluence, Jira, and codebase.
4) Always draft at least one `Story` for new requirements.
5) Create Jira issues only after explicit user approval.

## Script

- Script: `scripts/create_tech_spec_from_fdr.py`
- Related script: `scripts/discover_existing_functionality.py`
- Template: `templates/tech-spec-v1.md`

