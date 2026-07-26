"""Command-line entry point for dupefinder-cli."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

from .core import find_duplicates, wasted_bytes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dupefinder-cli",
        description="Find duplicate files in a directory tree by content hash.",
    )
    parser.add_argument("directory", help="Directory to scan recursively")
    parser.add_argument(
        "--min-size", type=int, default=0, help="Ignore files smaller than this many bytes"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete all but the first (alphabetically) file in each duplicate group",
    )
    parser.add_argument(
        "--move",
        metavar="DEST",
        help="Move duplicates (all but the first in each group) into DEST instead of deleting",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what --delete/--move would do without changing anything",
    )
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.isdir(args.directory):
        print(f"dupefinder-cli: error: not a directory: {args.directory}", file=sys.stderr)
        return 2

    duplicates = find_duplicates(args.directory, min_size=args.min_size)

    if args.json:
        print(json.dumps(duplicates, indent=2))
    else:
        if not duplicates:
            print("No duplicates found.")
        for digest, paths in duplicates.items():
            print(f"{digest[:12]}  ({len(paths)} copies)")
            for p in paths:
                print(f"  {p}")
        print(f"\nWasted space: {wasted_bytes(duplicates)} bytes")

    if args.delete or args.move:
        for paths in duplicates.values():
            keep, *rest = paths
            for path in rest:
                if args.move:
                    os.makedirs(args.move, exist_ok=True)
                    dest = os.path.join(args.move, os.path.basename(path))
                    action = f"move {path} -> {dest}"
                    if args.dry_run:
                        print(f"[dry-run] {action}")
                    else:
                        shutil.move(path, dest)
                        print(action)
                else:
                    action = f"delete {path}"
                    if args.dry_run:
                        print(f"[dry-run] {action}")
                    else:
                        os.remove(path)
                        print(action)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
