# Action: Interactive Discovery Session

## Goal

Gather project-specific context before writing technical specs or creating Jira issues.

## Required Questions

1) Project name (simple word)
2) Jira project key
3) FDR source type (text/file/pdf/confluence-url)

## Conditional Questions

- Ask for Confluence space key and labels only when user asks to create or refine Confluence pages.
- Ask for Confluence URL when user asks to read existing content.
- Ask story type preferences (Story/Task/Bug) only when not already specified in instructions.

## Output

- A validated context package for the next step:
  - project name
  - jira project key
  - FDR source
  - open questions list

