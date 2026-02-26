"""Action script: transition_jira_status.

Usage:
  python scripts/transition_jira_status.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transition a JIRA issue to a new status.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--transition-id', required=False)
    parser.add_argument('--status-name', required=False)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("transition_jira_status", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
