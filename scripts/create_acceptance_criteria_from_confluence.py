"""Action script: create_acceptance_criteria_from_confluence.

Usage:
  python scripts/create_acceptance_criteria_from_confluence.py --help
"""

from __future__ import annotations

import argparse
import json
import sys

from _actions import run_action


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate acceptance criteria from a Confluence page.")
    parser.add_argument('--page-id', required=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    result = run_action("create_acceptance_criteria_from_confluence", vars(args))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
