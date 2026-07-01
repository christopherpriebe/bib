from bibtexmanager import serialization, transforms

SAMPLE = """@string{isca = {ISCA}}
@article{zebra,
  title = {A Study of {ML} and {RISC-V}},
  booktitle = isca,
  year = {2020}
}
@inproceedings{apple,
  title = {the {NVIDIA} architecture},
  year = {2019}
}
"""


def _roundtrip(text, titlecase_titles=True):
    lib = serialization.read_string(text)
    lib = transforms.sort_entries(lib)
    if titlecase_titles:
        lib = transforms.format_titles(lib)
    return serialization.write_string(lib)


def test_string_reference_is_not_expanded():
    out = _roundtrip(SAMPLE)
    assert "booktitle = isca" in out
    entry_text = out.split("@article")[1]
    assert "{ISCA}" not in entry_text


def test_inner_braces_survive_roundtrip():
    out = _roundtrip(SAMPLE)
    assert "{ML}" in out
    assert "{RISC-V}" in out
    assert "{NVIDIA}" in out


def test_entries_are_sorted_by_key():
    out = _roundtrip(SAMPLE, titlecase_titles=False)
    assert out.index("@inproceedings{apple") < out.index("@article{zebra")


def test_string_block_is_preserved():
    out = _roundtrip(SAMPLE)
    assert "@string{isca = {ISCA}}" in out


def test_titlecasing_applies_to_titles_only():
    out = _roundtrip(SAMPLE)
    assert "The {NVIDIA} Architecture" in out


def test_strip_failure_markers_removes_prior_run_comments():
    marked = "% WARNING Parsing failed for the following 3 lines.\n" + SAMPLE
    lib = serialization.read_string(marked)
    cleaned = transforms.strip_failure_markers(lib)
    out = serialization.write_string(cleaned)
    assert "WARNING Parsing failed" not in out


CENTRAL = """@inproceedings{bare,
  booktitle = isca,
  year = {2020}
}
@inproceedings{literal,
  booktitle = {ISCA},
  year = {2021}
}
@article{journal_ref,
  journal = cacm,
  year = {2019}
}
"""

TABLES = {
    "conferences": {"isca": {"abbreviation": "ISCA", "full_name": "International Symposium"}},
    "journals": {"cacm": {"abbreviation": "CACM", "full_name": "Communications of the ACM"}},
}


def test_collect_string_definitions_uses_bare_references_only():
    library = serialization.read_string(CENTRAL)
    definitions, unresolved = transforms.collect_string_definitions(library, TABLES, "abbrev")
    assert definitions == {"isca": "ISCA", "cacm": "CACM"}
    assert unresolved == []


def test_collect_string_definitions_reports_unresolved_keys():
    library = serialization.read_string("@inproceedings{a,\n booktitle = micro,\n year = {2020}\n}\n")
    definitions, unresolved = transforms.collect_string_definitions(library, TABLES, "abbrev")
    assert definitions == {}
    assert unresolved == ["micro"]


FULL_ENTRY = """@inproceedings{a,
  title = {T},
  author = {Auth},
  booktitle = {ISCA},
  year = {2020},
  publisher = {ACM},
  isbn = {123}
}
"""


def test_keep_fields_keeps_only_named_in_original_order():
    library = serialization.read_string(FULL_ENTRY)
    library = transforms.keep_fields(library, ["Author", "TITLE"])
    field_keys = [field.key for field in library.entries[0].fields]
    assert field_keys == ["title", "author"]


def test_drop_fields_removes_named_case_insensitively():
    library = serialization.read_string(FULL_ENTRY)
    library = transforms.drop_fields(library, ["Publisher", "ISBN"])
    field_keys = {field.key for field in library.entries[0].fields}
    assert "publisher" not in field_keys
    assert "isbn" not in field_keys
    assert {"title", "author", "booktitle", "year"} <= field_keys


def test_prepend_string_definitions_is_sorted_and_skips_existing():
    library = serialization.read_string(
        "@string{isca = {ISCA}}\n@inproceedings{a,\n booktitle = isca,\n year = {2020}\n}\n"
    )
    library = transforms.prepend_string_definitions(
        library, {"isca": "ISCA", "cacm": "Communications of the ACM"}
    )
    out = serialization.write_string(library)
    assert out.count("@string{isca") == 1
    assert "@string{cacm = {Communications of the ACM}}" in out
    assert out.index("@string{cacm") < out.index("@inproceedings{a")
