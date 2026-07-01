"""Chris Priebe's BibTeX Manager: sort and title-case BibTeX files.

Public API:

* :func:`bibtexmanager.titlecase.capitalize_title` -- brace-aware title casing.
* :mod:`bibtexmanager.serialization` -- reference-preserving read/write.
* :mod:`bibtexmanager.transforms` -- library transforms (sort, format, clean).
"""

from .titlecase import capitalize_title

__all__ = ["capitalize_title"]
