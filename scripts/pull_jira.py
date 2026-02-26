"""Action script: pull_jira.

Usage:
  python scripts/pull_jira.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fetch a JIRA issue.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--fields', required=False)
    parser.add_argument('--include-comments', action='store_true')

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("pull_jira", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
