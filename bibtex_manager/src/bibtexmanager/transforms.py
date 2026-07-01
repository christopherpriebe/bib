"""Transformations over a parsed BibTeX :class:`~bibtexparser.Library`.

Each function takes a library and returns a library, so they compose. Blocks
that are not entries (``@string`` definitions, comments, blocks the parser could
not handle) are preserved in place.
"""

from bibtexparser import Library
from bibtexparser.model import Entry, ImplicitComment

from .titlecase import capitalize_title

_FAILURE_MARKER = "% WARNING Parsing failed"


def sort_entries(library: Library, case_insensitive: bool = True) -> Library:
    """Return a copy of ``library`` with entries sorted by citation key.

    Non-entry blocks keep their original positions; the sorted entries are
    slotted back into the positions the entries originally occupied.
    """
    sorted_entries = sorted(
        (block for block in library.blocks if isinstance(block, Entry)),
        key=lambda entry: _citation_key(entry, case_insensitive),
    )
    next_sorted_entry = iter(sorted_entries)

    reordered_blocks = [
        next(next_sorted_entry) if isinstance(block, Entry) else block
        for block in library.blocks
    ]
    return Library(blocks=reordered_blocks)


def format_titles(library: Library) -> Library:
    """Title-case every entry's ``title`` field in place, then return it."""
    for entry in library.entries:
        for field in entry.fields:
            if field.key.lower() == "title" and isinstance(field.value, str):
                field.value = capitalize_title(field.value)
    return library


def strip_failure_markers(library: Library) -> Library:
    """Remove parser-generated 'Parsing failed' marker comments from a prior run.

    bibtexparser writes such a marker ahead of any block it could not parse (for
    example, a duplicate key). Stripping them on input keeps reformatting
    idempotent instead of accumulating markers across successive runs.
    """
    kept_blocks = [block for block in library.blocks if not _is_failure_marker(block)]
    if len(kept_blocks) == len(library.blocks):
        return library
    return Library(blocks=kept_blocks)


def _citation_key(entry: Entry, case_insensitive: bool) -> str:
    key = entry.key or ""
    return key.lower() if case_insensitive else key


def _is_failure_marker(block) -> bool:
    return isinstance(block, ImplicitComment) and block.comment.startswith(_FAILURE_MARKER)
