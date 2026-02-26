# Action: Delete Confluence page

## Goal

Delete a Confluence page.

## Inputs

- Required: page_id

## Outputs

- Deleted page ID

## Steps

1) Validate page ID.
2) Delete page via Confluence API.
3) Return confirmation.

## Script

- Script: scripts/delete_confluence_page.py
- Notes: This action is destructive.
