"""Command-line interface for ``managebib``."""

import argparse
import logging
import sys

from bibtexparser import Library

from . import serialization, transforms, venues


def run_format(args: argparse.Namespace) -> None:
    _silence_bibtexparser_warnings()
    _validate_generation_flags(args)

    try:
        library = serialization.read_file(args.bibfile)
    except FileNotFoundError:
        sys.exit(f"managebib: no such file: {args.bibfile}")

    library = transforms.strip_failure_markers(library)
    _report_failed_blocks(library, args.bibfile)

    if args.keep is not None:
        library = transforms.keep_fields(library, args.keep)
    elif args.drop is not None:
        library = transforms.drop_fields(library, args.drop)

    if args.strings:
        library = _define_string_references(args, library)

    library = transforms.sort_entries(library, case_insensitive=not args.case_sensitive)
    if not args.no_titlecase:
        library = transforms.format_titles(library)

    _write_output(args, serialization.write_string(library))


def _validate_generation_flags(args: argparse.Namespace) -> None:
    if args.strings and not args.out:
        sys.exit(
            "managebib: --strings requires -o/--out; "
            "it only applies when writing to a new file."
        )
    if (args.keep is not None or args.drop is not None) and args.in_place:
        sys.exit(
            "managebib: --keep/--drop cannot be used with -i/--in-place; "
            "write to a new file with -o or preview on stdout."
        )


def _define_string_references(args: argparse.Namespace, library: Library) -> Library:
    tables = venues.load_tables(args.conferences, args.journals)
    definitions, unresolved = transforms.collect_string_definitions(
        library, tables, args.strings
    )
    for reference_key in sorted(set(unresolved)):
        print(
            f"managebib: warning: no '{args.strings}' name for reference "
            f"'{reference_key}'; left undefined.",
            file=sys.stderr,
        )
    return transforms.prepend_string_definitions(library, definitions)


def _silence_bibtexparser_warnings() -> None:
    """Quiet bibtexparser's misleading 'Unknown block type' log for failed blocks.

    Unparseable blocks are reported to the user by :func:`_report_failed_blocks`,
    so the library's own warning is redundant noise.
    """
    logging.getLogger("bibtexparser").setLevel(logging.ERROR)


def _report_failed_blocks(library: Library, source: str) -> None:
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


def _write_output(args: argparse.Namespace, text: str) -> None:
    if args.in_place:
        _write_file(args.bibfile, text)
    elif args.out:
        _write_file(args.out, text)
    else:
        sys.stdout.write(text)


def _write_file(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as destination:
        destination.write(text)


def _field_list(value: str) -> list[str]:
    return [name.strip() for name in value.split(",") if name.strip()]


def build_parser() -> argparse.ArgumentParser:
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
    field_group = format_parser.add_mutually_exclusive_group()
    field_group.add_argument("--keep", metavar="FIELDS", type=_field_list,
                             help="Keep only these comma-separated fields on each entry "
                                  "(cannot be used with -i)")
    field_group.add_argument("--drop", metavar="FIELDS", type=_field_list,
                             help="Remove these comma-separated fields from each entry "
                                  "(cannot be used with -i)")
    format_parser.add_argument("--strings", choices=list(venues.NAME_FORMS),
                               help="Define @string references in the output using this "
                                    "venue-name form (requires -o): full name, abbreviation, "
                                    "or short name")
    format_parser.add_argument("--conferences", metavar="PATH",
                               help="Conferences JSON file to use instead of the bundled one")
    format_parser.add_argument("--journals", metavar="PATH",
                               help="Journals JSON file to use instead of the bundled one")
    format_parser.set_defaults(func=run_format)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        parser.exit(2)
    return args.func(args)
