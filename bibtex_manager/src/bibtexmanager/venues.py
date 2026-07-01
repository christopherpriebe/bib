"""Conference and journal name tables used to define ``@string`` references.

Each data file maps a short reference key (such as ``isca``) to several forms
of a venue's name::

    {"data": {"isca": {"name": "...", "full_name": "...", "abbreviation": "..."}}}

A field carrying a bare reference is resolved against one table: a ``booktitle``
against conferences, a ``journal`` against journals.
"""

import json
from importlib import resources
from pathlib import Path

VenueEntry = dict[str, str]
VenueTable = dict[str, VenueEntry]
VenueTables = dict[str, VenueTable]

NAME_FORMS = ("full", "abbrev", "name")

_PACKAGE = "bibtexmanager"
_BUNDLED_FILENAME = {"conferences": "conferences.json", "journals": "journals.json"}
_FORM_TO_JSON_FIELD = {"full": "full_name", "abbrev": "abbreviation", "name": "name"}
_FIELD_TO_TABLE = {"booktitle": "conferences", "journal": "journals"}


def load_tables(
    conferences_path: str | None = None,
    journals_path: str | None = None,
) -> VenueTables:
    """Return ``{"conferences": {...}, "journals": {...}}`` name tables.

    A given path overrides the bundled file for that table.
    """
    return {
        "conferences": _read_table(conferences_path, _BUNDLED_FILENAME["conferences"]),
        "journals": _read_table(journals_path, _BUNDLED_FILENAME["journals"]),
    }


def table_for_field(field_key: str) -> str | None:
    """Return the table name a field is resolved against, or ``None``."""
    return _FIELD_TO_TABLE.get(field_key.lower())


def find_name(
    tables: VenueTables,
    table_name: str,
    reference_key: str,
    form: str,
) -> str | None:
    """Return the chosen-form name for ``reference_key``, or ``None`` if unavailable."""
    venue = tables.get(table_name, {}).get(reference_key)
    if venue is None:
        return None
    return venue.get(_FORM_TO_JSON_FIELD[form])


def _read_table(path: str | None, bundled_filename: str) -> VenueTable:
    text = _read_text(path, bundled_filename)
    if not text.strip():
        return {}
    return json.loads(text).get("data", {})


def _read_text(path: str | None, bundled_filename: str) -> str:
    if path is not None:
        return Path(path).read_text(encoding="utf-8")
    return resources.files(_PACKAGE).joinpath(bundled_filename).read_text(encoding="utf-8")
