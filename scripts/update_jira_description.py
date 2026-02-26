"""Action script: update_jira_description.

Usage:
  python scripts/update_jira_description.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update the description of a JIRA issue.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--description', required=True)
    parser.add_argument('--mode', required=False, choices=['replace', 'append'])

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("update_jira_description", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
