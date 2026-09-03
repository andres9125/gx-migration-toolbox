from __future__ import annotations

import argparse
import json
from pathlib import Path

from .scanner import build_report, scan_source_tree


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gx-migration-toolbox",
        description="Build a read-only static inventory of a source tree.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    scan = subparsers.add_parser("scan", help="Scan a source directory and write a JSON report.")
    scan.add_argument("--source", type=Path, required=True, help="Directory to inspect.")
    scan.add_argument("--output", type=Path, required=True, help="JSON report path to create.")
    scan.add_argument(
        "--runtime-pattern",
        action="append",
        default=[],
        help="Case-insensitive package or namespace signal. May be repeated.",
    )
    scan.add_argument(
        "--max-file-size-mb",
        type=int,
        default=5,
        help="Skip files larger than this size. Default: 5.",
    )
    scan.set_defaults(func=run_scan)
    return parser


def run_scan(args: argparse.Namespace) -> None:
    try:
        files = scan_source_tree(
            args.source,
            runtime_patterns=args.runtime_pattern,
            max_file_size_mb=args.max_file_size_mb,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    report = build_report(args.source, files)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = report["summary"]
    print(
        f"Scanned {summary['files']} files, {summary['lines']} lines, "
        f"{summary['imports']} imports, and {summary['runtime_references']} runtime signals."
    )
    print(f"Report written to {args.output}")


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
