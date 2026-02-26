"""Action script template.

Usage:
  python scripts/<action_script>.py --help
"""

from __future__ import annotations

import argparse
import json
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="<action description>")
    # Add required and optional arguments here.
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # TODO: Replace with real action logic and API calls.
    result = {
        "status": "not_implemented",
        "action": "<action_name>",
        "inputs": vars(args),
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
