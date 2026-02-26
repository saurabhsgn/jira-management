"""Action script: create_acceptance_criteria_from_jira.

Usage:
  python scripts/create_acceptance_criteria_from_jira.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate acceptance criteria from a JIRA issue.")
    parser.add_argument('--issue-key', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("create_acceptance_criteria_from_jira", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
