"""Action script: read_confluence_page.

Usage:
  python scripts/read_confluence_page.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read a Confluence page.")
    parser.add_argument('--page-id', required=True)
    parser.add_argument('--format', required=False)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("read_confluence_page", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
