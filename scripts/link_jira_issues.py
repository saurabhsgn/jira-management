"""Action script: link_jira_issues.

Usage:
  python scripts/link_jira_issues.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Link two JIRA issues.")
    parser.add_argument('--inward-issue-key', required=True)
    parser.add_argument('--outward-issue-key', required=True)
    parser.add_argument('--link-type', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("link_jira_issues", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
