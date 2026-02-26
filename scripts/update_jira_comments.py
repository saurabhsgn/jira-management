"""Action script: update_jira_comments.

Usage:
  python scripts/update_jira_comments.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add or update a JIRA comment.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--comment', required=True)
    parser.add_argument('--comment-id', required=False)
    parser.add_argument('--mode', required=False, choices=['add', 'update'])

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("update_jira_comments", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
