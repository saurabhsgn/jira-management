# Action: Move Confluence page

## Goal

Move a Confluence page to a new parent.

## Inputs

- Required: page_id, new_parent_id

## Outputs

- Updated page ID

## Steps

1) Validate page and parent IDs.
2) Move page via Confluence API.
3) Return confirmation.

## Script

- Script: scripts/move_confluence_page.py
- Notes: Ensure permissions for target parent.
