# Action: Export Confluence page

## Goal

Export a Confluence page to a given format.

## Inputs

- Required: page_id, format

## Outputs

- Exported file path

## Steps

1) Validate page ID and export format.
2) Request export via Confluence API.
3) Download export and return path.

## Script

- Script: scripts/export_confluence_page.py
- Notes: Formats depend on Confluence configuration.
