# Action: Add Confluence attachment

## Goal

Attach a file to a Confluence page.

## Inputs

- Required: page_id, file_path

## Outputs

- Attachment ID

## Steps

1) Validate page ID and file path.
2) Upload attachment via Confluence API.
3) Return attachment ID.

## Script

- Script: scripts/add_confluence_attachment.py
- Notes: Handle file name collisions.
