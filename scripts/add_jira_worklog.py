"""Action script: add_jira_worklog.

Usage:
  python scripts/add_jira_worklog.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add a JIRA worklog entry.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--time-spent', required=True)
    parser.add_argument('--comment', required=False)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("add_jira_worklog", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
