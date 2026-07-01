"""Read and write BibTeX files without altering their meaning.

The default ``bibtexparser`` round trip both expands ``@string`` references and
normalizes value delimiters. This module configures the parse/write middleware
so that neither happens:

* ``@string`` abbreviations stay references (``booktitle = isca``), and
* each value keeps its original enclosing (bare / ``{...}`` / ``"..."``).

Inner brace protection (``{ML}`` inside a title) is preserved either way.
"""

import bibtexparser
from bibtexparser import Library
from bibtexparser.middlewares import RemoveEnclosingMiddleware
from bibtexparser.middlewares.enclosing import AddEnclosingMiddleware


def read_file(path: str) -> Library:
    """Parse the BibTeX file at ``path`` (may raise ``FileNotFoundError``)."""
    return bibtexparser.parse_file(path, parse_stack=_build_parse_stack())


def read_string(text: str) -> Library:
    """Parse BibTeX from a string."""
    return bibtexparser.parse_string(text, parse_stack=_build_parse_stack())


def write_string(library: Library) -> str:
    """Serialize ``library`` back to BibTeX text."""
    return bibtexparser.write_string(library, unparse_stack=_build_unparse_stack())


def _build_parse_stack():
    """Middleware used when reading.

    Keeps ``RemoveEnclosingMiddleware`` (it strips the outer ``{}``/``""`` from
    each value, recording which was used so it can be restored on write, and
    gives us the plain inner text to title-case) but deliberately omits
    ``ResolveStringReferencesMiddleware`` so that ``@string`` abbreviations such
    as ``booktitle = isca`` are preserved as references instead of being
    expanded into literals like ``{ISCA}``.
    """
    return [RemoveEnclosingMiddleware(allow_inplace_modification=True)]


def _build_unparse_stack():
    """Middleware used when writing.

    ``reuse_previous_enclosing=True`` restores each value's original delimiter,
    so a bare reference stays bare (``booktitle = isca``) rather than being
    wrapped into ``{isca}``.
    """
    return [AddEnclosingMiddleware(
        allow_inplace_modification=False,
        default_enclosing="{",
        reuse_previous_enclosing=True,
        enclose_integers=True,
    )]
