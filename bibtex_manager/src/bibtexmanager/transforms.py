"""Transformations over a parsed BibTeX :class:`~bibtexparser.Library`.

Each function takes a library and returns a library, so they compose. Blocks
that are not entries (``@string`` definitions, comments, blocks the parser could
not handle) are preserved in place.
"""

from collections.abc import Iterable

from bibtexparser import Library
from bibtexparser.model import Block, Entry, Field, ImplicitComment, String

from . import venues
from .titlecase import capitalize_title
from .venues import VenueTables

_FAILURE_MARKER = "% WARNING Parsing failed"
_BARE_REFERENCE = "no-enclosing"


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


def keep_fields(library: Library, field_names: Iterable[str]) -> Library:
    """Keep only the named fields on each entry, in their existing order.

    Field names are matched case-insensitively. The entry type and citation key
    are structural and always retained.
    """
    wanted = {name.lower() for name in field_names}
    for entry in library.entries:
        entry.fields = [field for field in entry.fields if field.key.lower() in wanted]
    return library


def drop_fields(library: Library, field_names: Iterable[str]) -> Library:
    """Remove the named fields from each entry, matching case-insensitively."""
    unwanted = {name.lower() for name in field_names}
    for entry in library.entries:
        entry.fields = [field for field in entry.fields if field.key.lower() not in unwanted]
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


def collect_string_definitions(
    library: Library,
    tables: VenueTables,
    form: str,
) -> tuple[dict[str, str], list[str]]:
    """Return ``({key: name}, [unresolved_key, ...])`` for the library's bare references.

    Only bare references (unbraced, e.g. ``booktitle = isca``) are considered;
    literal values like ``booktitle = {ISCA}`` are left alone. A reference whose
    name is missing from ``tables`` is reported as unresolved rather than defined.
    """
    definitions = {}
    unresolved = []
    for entry in library.entries:
        for field in entry.fields:
            table_name = venues.table_for_field(field.key)
            if table_name is None or not _is_bare_reference(entry, field):
                continue
            reference_key = field.value
            name = venues.find_name(tables, table_name, reference_key, form)
            if name is None:
                unresolved.append(reference_key)
            else:
                definitions[reference_key] = name
    return definitions, unresolved


def prepend_string_definitions(library: Library, definitions: dict[str, str]) -> Library:
    """Prepend ``@string`` blocks for keys in ``definitions`` not already defined.

    New blocks are ordered by key and placed before the existing blocks.
    """
    already_defined = {block.key for block in library.blocks if isinstance(block, String)}
    new_blocks = [
        String(key=reference_key, value=name)
        for reference_key, name in sorted(definitions.items())
        if reference_key not in already_defined
    ]
    if not new_blocks:
        return library
    return Library(blocks=new_blocks + list(library.blocks))


def _citation_key(entry: Entry, case_insensitive: bool) -> str:
    key = entry.key or ""
    return key.lower() if case_insensitive else key


def _is_failure_marker(block: Block) -> bool:
    return isinstance(block, ImplicitComment) and block.comment.startswith(_FAILURE_MARKER)


def _is_bare_reference(entry: Entry, field: Field) -> bool:
    enclosing = entry.parser_metadata.get("removed_enclosing", {})
    return enclosing.get(field.key) == _BARE_REFERENCE
