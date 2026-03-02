# JIRA/Confluence/GitHub Actions Instruction Index

This file is the main entry point for all instruction markdown files. Each action has a dedicated instruction file and a matching script that executes the action.

## Setup

- Edit `config.json` with your Atlassian Cloud base URLs, email, and API tokens.
- Confluence defaults to `/wiki` under the JIRA base URL if not provided.

## Actions

| Action | Instruction | Script |
| --- | --- | --- |
| Create JIRA | instructions/create-jira.md | scripts/create_jira.py |
| Create Confluence page | instructions/create-confluence-page.md | scripts/create_confluence_page.py |
| Update JIRA summary | instructions/update-jira-summary.md | scripts/update_jira_summary.py |
| Update JIRA description | instructions/update-jira-description.md | scripts/update_jira_description.py |
| Update JIRA comments | instructions/update-jira-comments.md | scripts/update_jira_comments.py |
| Pull JIRA | instructions/pull-jira.md | scripts/pull_jira.py |
| Explain JIRA | instructions/explain-jira.md | scripts/explain_jira.py |
| Create test cases from JIRA | instructions/create-test-cases-from-jira.md | scripts/create_test_cases_from_jira.py |
| Create acceptance criteria from JIRA description | instructions/create-acceptance-criteria-from-jira.md | scripts/create_acceptance_criteria_from_jira.py |
| Read Confluence page | instructions/read-confluence-page.md | scripts/read_confluence_page.py |
| Create acceptance criteria from Confluence page | instructions/create-acceptance-criteria-from-confluence.md | scripts/create_acceptance_criteria_from_confluence.py |
| Create JIRA from Confluence page | instructions/create-jira-from-confluence.md | scripts/create_jira_from_confluence.py |
| Transition JIRA status | instructions/transition-jira-status.md | scripts/transition_jira_status.py |
| Assign JIRA issue | instructions/assign-jira-issue.md | scripts/assign_jira_issue.py |
| Add JIRA labels | instructions/add-jira-labels.md | scripts/add_jira_labels.py |
| Remove JIRA labels | instructions/remove-jira-labels.md | scripts/remove_jira_labels.py |
| Set JIRA priority | instructions/set-jira-priority.md | scripts/set_jira_priority.py |
| Add JIRA attachment | instructions/add-jira-attachment.md | scripts/add_jira_attachment.py |
| Link JIRA issues | instructions/link-jira-issues.md | scripts/link_jira_issues.py |
| Add JIRA watcher | instructions/add-jira-watcher.md | scripts/add_jira_watcher.py |
| Set JIRA due date | instructions/set-jira-due-date.md | scripts/set_jira_due_date.py |
| Search JIRA | instructions/search-jira.md | scripts/search_jira.py |
| Create JIRA subtask | instructions/create-jira-subtask.md | scripts/create_jira_subtask.py |
| Delete JIRA issue | instructions/delete-jira-issue.md | scripts/delete_jira_issue.py |
| Update JIRA components | instructions/update-jira-components.md | scripts/update_jira_components.py |
| Add JIRA worklog | instructions/add-jira-worklog.md | scripts/add_jira_worklog.py |
| Get JIRA changelog | instructions/get-jira-changelog.md | scripts/get_jira_changelog.py |
| Update Confluence page | instructions/update-confluence-page.md | scripts/update_confluence_page.py |
| Delete Confluence page | instructions/delete-confluence-page.md | scripts/delete_confluence_page.py |
| Search Confluence pages | instructions/search-confluence-pages.md | scripts/search_confluence_pages.py |
| Add Confluence comment | instructions/add-confluence-comment.md | scripts/add_confluence_comment.py |
| Update Confluence labels | instructions/update-confluence-labels.md | scripts/update_confluence_labels.py |
| Add Confluence attachment | instructions/add-confluence-attachment.md | scripts/add_confluence_attachment.py |
| Move Confluence page | instructions/move-confluence-page.md | scripts/move_confluence_page.py |
| Export Confluence page | instructions/export-confluence-page.md | scripts/export_confluence_page.py |
| Discovery session | instructions/discovery-session.md | scripts/discover_existing_functionality.py |
| Create technical specification from FDR | instructions/create-tech-spec-from-fdr.md | scripts/create_tech_spec_from_fdr.py |

## GitHub Actions Module

- Sub-index: `instructions/github-actions/INSTRUCTIONS.md`
- Scripts folder: `scripts/github_actions/`

| Action | Instruction | Script |
| --- | --- | --- |
| List GitHub workflows | instructions/github-actions/list-workflows.md | scripts/github_actions/list_workflows.py |
| Get GitHub workflow runs | instructions/github-actions/get-workflow-runs.md | scripts/github_actions/get_workflow_runs.py |
| Resolve GitHub connectivity | instructions/github-actions/resolve-connectivity.md | scripts/github_actions/resolve_connectivity.py |

## Add a new action

1) Copy `instructions/_template.md` to a new file in `instructions/`.
2) Copy `scripts/_template.py` to a new script in `scripts/`.
3) Add the new action to this file under `Actions`.

## Conventions

- One instruction file per action.
- One script per action.
- Keep filenames kebab-case in `instructions/` and snake_case in `scripts/`.
- Scripts should accept CLI flags for required inputs and print a machine-readable result.
- Use `templates/jira-story-template.md` as the default Jira story structure.

## Jira Story Update Rules (Session)

- Always review the target story content first before updating; do not assume missing context.
- For new Jira creation, gather inputs interactively section-by-section using `templates/jira-story-template.md`.
- If content for any section is missing and not found in provided reference pages, ask follow-up questions before creating/updating the Jira.
- No update/write/change/modify/delete action should be performed without prior review and user confirmation.
- Always retain pre-change history/snapshots before any change so full rollback to previous state is possible.
- Retention period for rollback history is infinite unless explicitly requested otherwise.
- If user asks for formatting/style only, do not change business content.
- Use `INV-3187` as the style reference for section titles and acceptance-criteria presentation.
- For generated Jira story descriptions, use bold blue section titles (target color: `#4C9AFF`).
- Preserve line breaks and newline pattern from the existing story wherever possible.
- For acceptance criteria updates, add a dedicated `Acceptance Criteria` section in checklist/task-list style.
- Keep existing description text intact unless user explicitly requests content edits.

## GitHub Operations & Jira Comment Policy

- Always map work to a Jira issue key before any GitHub operation (`clone`, `pull`, `commit`, `push`, `merge`).
- Always provide a pre-change work summary for review before any Jira comment update.
- Never post/update Jira comments until user explicitly approves the prepared summary.
- Commit message format must include Jira key: `<type>(<scope>): <summary> [<JIRA-KEY>]`.
- Commit body should include: what changed, why changed, validation/tests, and rollback note.
- Keep commits scoped to one story/task; avoid unrelated file changes in the same commit.
- Push only after local review summary is prepared and validated.
- Merge only after review + validations are complete and acceptance criteria mapping is clear.
- After push/merge, Jira comment must include completed work, files/modules impacted, test evidence, pending items/blockers, and PR/commit links.

### Jira Comment Template (Review Draft First)

```text
Jira: <JIRA-KEY>
Branch/PR: <branch-name> | <pr-link-or-na>
Commit(s): <commit-sha-list>

Work Completed
- <item-1>
- <item-2>

Files/Modules Updated
- <path-or-module-1>
- <path-or-module-2>

Validation / Testing
- <test-or-check-1>
- <test-or-check-2>

Pending / Follow-up
- <pending-item-or-none>

Risks / Notes
- <risk-note-or-none>
```
