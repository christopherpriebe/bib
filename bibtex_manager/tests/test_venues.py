import json

from bibtexmanager import venues


def test_bundled_conferences_include_sample():
    tables = venues.load_tables()
    assert "afips" in tables["conferences"]


def test_bundled_journals_are_empty():
    tables = venues.load_tables()
    assert tables["journals"] == {}


def test_override_paths_replace_bundled_files(tmp_path):
    conferences = tmp_path / "conferences.json"
    conferences.write_text(json.dumps(
        {"data": {"isca": {"full_name": "International Symposium",
                           "abbreviation": "ISCA", "name": "ISCA"}}}
    ))
    journals = tmp_path / "journals.json"
    journals.write_text(json.dumps(
        {"data": {"cacm": {"full_name": "Communications of the ACM",
                           "abbreviation": "CACM", "name": "CACM"}}}
    ))
    tables = venues.load_tables(str(conferences), str(journals))
    assert tables["conferences"]["isca"]["abbreviation"] == "ISCA"
    assert tables["journals"]["cacm"]["full_name"] == "Communications of the ACM"


def test_table_for_field_routes_by_field_name():
    assert venues.table_for_field("booktitle") == "conferences"
    assert venues.table_for_field("BookTitle") == "conferences"
    assert venues.table_for_field("journal") == "journals"
    assert venues.table_for_field("year") is None


def test_find_name_selects_the_requested_form():
    tables = {
        "conferences": {"isca": {"full_name": "International Symposium",
                                 "abbreviation": "ISCA", "name": "ISCA short"}},
        "journals": {},
    }
    assert venues.find_name(tables, "conferences", "isca", "full") == "International Symposium"
    assert venues.find_name(tables, "conferences", "isca", "abbrev") == "ISCA"
    assert venues.find_name(tables, "conferences", "isca", "name") == "ISCA short"
    assert venues.find_name(tables, "conferences", "unknown", "full") is None
