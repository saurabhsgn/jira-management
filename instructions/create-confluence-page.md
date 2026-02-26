# Action: Create Confluence page

## Goal

Create a new Confluence page with given title and body content.

## Inputs

- Required: space_key, title, body
- Optional: parent_page_id, labels, attachments

## Outputs

- Confluence page ID
- Confluence page URL

## Steps

1) Validate space key and title.
2) Build the page body in storage format.
3) Create the page via Confluence API.
4) Return page ID and URL.

## Script

- Script: scripts/create_confluence_page.py
- Notes: Use authenticated Confluence REST API calls.
