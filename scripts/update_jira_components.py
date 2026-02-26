"""Action script: update_jira_components.

Usage:
  python scripts/update_jira_components.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Update JIRA issue components.")
    parser.add_argument('--issue-key', required=True)
    parser.add_argument('--components', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("update_jira_components", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
