"""Action script: remove_jira_labels.

Usage:
  python scripts/remove_jira_labels.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Remove labels from a JIRA issue.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--labels', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("remove_jira_labels", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
