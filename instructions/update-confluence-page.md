# Action: Update Confluence page

## Goal

Update the title or body of a Confluence page.

## Inputs

- Required: page_id, title, body

## Outputs

- Updated page ID

## Steps

1) Validate page ID and content.
2) Increment version and update page via API.
3) Return confirmation.

## Script

- Script: scripts/update_confluence_page.py
- Notes: Confluence updates require version increments.
