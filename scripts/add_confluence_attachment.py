"""Action script: add_confluence_attachment.

Usage:
  python scripts/add_confluence_attachment.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Add a Confluence attachment.")
    parser.add_argument('--page-id', required=True)
    parser.add_argument('--file-path', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("add_confluence_attachment", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
