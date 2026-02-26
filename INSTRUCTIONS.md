# JIRA/Confluence Instruction Index

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

## Add a new action

1) Copy `instructions/_template.md` to a new file in `instructions/`.
2) Copy `scripts/_template.py` to a new script in `scripts/`.
3) Add the new action to this file under `Actions`.

## Conventions

- One instruction file per action.
- One script per action.
- Keep filenames kebab-case in `instructions/` and snake_case in `scripts/`.
- Scripts should accept CLI flags for required inputs and print a machine-readable result.
