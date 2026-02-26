"""Action script: set_jira_priority.

Usage:
  python scripts/set_jira_priority.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Set the priority for a JIRA issue.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--priority', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("set_jira_priority", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
