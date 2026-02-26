"""Action script: create_jira_subtask.

Usage:
  python scripts/create_jira_subtask.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a JIRA subtask.")
    parser.add_argument('--parent-issue-key', required=True)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--issue-type', required=False)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("create_jira_subtask", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
