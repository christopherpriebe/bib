"""Command-line interface for ``managebib``."""

import argparse
import logging
import sys

from . import serialization, transforms


def run_format(args):
    _silence_bibtexparser_warnings()

    try:
        library = serialization.read_file(args.bibfile)
    except FileNotFoundError:
        sys.exit(f"managebib: no such file: {args.bibfile}")

    library = transforms.strip_failure_markers(library)
    _report_failed_blocks(library, args.bibfile)

    library = transforms.sort_entries(library, case_insensitive=not args.case_sensitive)
    if not args.no_titlecase:
        library = transforms.format_titles(library)

    _write_output(args, serialization.write_string(library))


def _silence_bibtexparser_warnings():
    """Quiet bibtexparser's misleading 'Unknown block type' log for failed blocks.

    Unparseable blocks are reported to the user by :func:`_report_failed_blocks`,
    so the library's own warning is redundant noise.
    """
    logging.getLogger("bibtexparser").setLevel(logging.ERROR)


def _report_failed_blocks(library, source):
    """Warn about blocks the parser could not handle (e.g. duplicate keys)."""
    for block in library.failed_blocks:
        key = getattr(block, "key", None)
        line_number = getattr(block, "start_line", None)
        key_note = f" (key: {key})" if key else ""
        location_note = f" near line {line_number}" if line_number is not None else ""
        print(
            f"managebib: warning: could not parse a block{key_note}{location_note} "
            f"[{type(block).__name__}] in {source}; it was left unsorted.",
            file=sys.stderr,
        )


def _write_output(args, text):
    if args.in_place:
        _write_file(args.bibfile, text)
    elif args.out:
        _write_file(args.out, text)
    else:
        sys.stdout.write(text)


def _write_file(path, text):
    with open(path, "w", encoding="utf-8") as destination:
        destination.write(text)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="managebib",
        description="BibTeX operations CLI."
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    format_parser = subparsers.add_parser(
        "format",
        help="Sort entries by citation key and title-case titles "
             "(text inside {curly braces} is preserved verbatim)."
    )
    format_parser.add_argument("bibfile", help="Path to input .bib file")
    output_group = format_parser.add_mutually_exclusive_group()
    output_group.add_argument("-o", "--out", help="Write result to this file (default: stdout)")
    output_group.add_argument("-i", "--in-place", action="store_true",
                              help="Overwrite the input file in place")
    format_parser.add_argument("--case-sensitive", action="store_true",
                               help="Use case-sensitive sort (default: case-insensitive)")
    format_parser.add_argument("--no-titlecase", action="store_true",
                               help="Only sort; do not change title capitalization")
    format_parser.set_defaults(func=run_format)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        parser.exit(2)
    return args.func(args)
