"""Action script: add_confluence_comment.

Usage:
  python scripts/add_confluence_comment.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add a Confluence comment.")
    parser.add_argument('--page-id', required=True)
    parser.add_argument('--comment', required=True)
    parser.add_argument('--representation', required=False)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("add_confluence_comment", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
