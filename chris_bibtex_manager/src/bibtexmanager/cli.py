import argparse
import sys
import bibtexparser
from bibtexparser import Library
from bibtexparser.model import Entry as BibEntry


def sort_entries_new_library(library: Library, case_insensitive: bool = True) -> Library:
    entries_sorted = sorted(
        (b for b in library.blocks if isinstance(b, BibEntry)),
        key=lambda e: (e.key or "").lower() if case_insensitive else (e.key or "")
    )
    it = iter(entries_sorted)

    new_blocks = []
    for b in library.blocks:
        if isinstance(b, BibEntry):
            new_blocks.append(next(it))
        else:
            new_blocks.append(b)

    return Library(blocks=new_blocks)


def cmd_sort(args):
    library = bibtexparser.parse_file(args.bibfile)
    library = sort_entries_new_library(library, case_insensitive=not args.case_sensitive)

    if args.in_place:
        bibtexparser.write_file(args.bibfile, library)
    elif args.out:
        bibtexparser.write_file(args.out, library)
    else:
        sys.stdout.write(bibtexparser.write_string(library))


def build_parser():
    parser = argparse.ArgumentParser(
        prog="managebib",
        description="BibTeX operations CLI."
    )
    subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")

    p_format = subparsers.add_parser(
        "format",
        help="Format all entries (sort lexicographically by citation key, capitalize titles)."
    )
    p_format.add_argument("bibfile", help="Path to input .bib file")
    out = p_format.add_mutually_exclusive_group()
    out.add_argument("-o", "--out", help="Write result to this file (default: stdout)")
    out.add_argument("-i", "--in-place", action="store_true",
                     help="Overwrite the input file in place")
    p_format.add_argument("--case-sensitive", action="store_true",
                        help="Use case-sensitive sort (default: case-insensitive)")
    p_format.set_defaults(func=cmd_sort)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        parser.exit(2)
    return args.func(args)


if __name__ == "__main__":
    main()
