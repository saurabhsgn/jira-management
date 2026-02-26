"""Action script: add_jira_watcher.

Usage:
  python scripts/add_jira_watcher.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add a watcher to a JIRA issue.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--watcher', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("add_jira_watcher", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
