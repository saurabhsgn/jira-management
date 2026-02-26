# Action: Read Confluence page

## Goal

Fetch a Confluence page and return normalized content.

## Inputs

- Required: page_id
- Optional: expand (body,metadata), format (storage|view|text)

## Outputs

- Page content payload

## Steps

1) Validate page ID.
2) Fetch page content via Confluence API.
3) Normalize response into a stable schema.

## Script

- Script: scripts/read_confluence_page.py
- Notes: Use authenticated Confluence REST API calls.
