"""Action script: assign_jira_issue.

Usage:
  python scripts/assign_jira_issue.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Assign a JIRA issue to a user.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--assignee', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("assign_jira_issue", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
