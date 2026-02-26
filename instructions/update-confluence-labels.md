# Action: Update Confluence labels

## Goal

Add or remove labels on a Confluence page.

## Inputs

- Required: page_id, labels, mode

## Outputs

- Updated page ID

## Steps

1) Validate page ID and label list.
2) Add or remove labels via API.
3) Return confirmation.

## Script

- Script: scripts/update_confluence_labels.py
- Notes: Mode should be add or remove.
