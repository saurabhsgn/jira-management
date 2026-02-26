# Action: Add Confluence comment

## Goal

Add a comment to a Confluence page.

## Inputs

- Required: page_id, comment

## Outputs

- Comment ID

## Steps

1) Validate page ID and comment.
2) Create comment via Confluence API.
3) Return comment ID.

## Script

- Script: scripts/add_confluence_comment.py
- Notes: Support inline or footer comments if needed.
