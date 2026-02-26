"""Action script: create_jira.

Usage:
  python scripts/create_jira.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Create a new JIRA issue.")
    parser.add_argument('--project-key', required=True)
    parser.add_argument('--issue-type', required=True)
    parser.add_argument('--summary', required=True)
    parser.add_argument('--description', required=False)
    parser.add_argument('--labels', required=False)
    parser.add_argument('--assignee', required=False)
    parser.add_argument('--priority', required=False)
    parser.add_argument('--components', required=False)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("create_jira", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
