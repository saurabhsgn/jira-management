# Action: Search Confluence pages

## Goal

Search Confluence pages using CQL.

## Inputs

- Required: cql

## Outputs

- Page list

## Steps

1) Validate CQL query.
2) Execute search via Confluence API.
3) Normalize results and return.

## Script

- Script: scripts/search_confluence_pages.py
- Notes: Support pagination when needed.
