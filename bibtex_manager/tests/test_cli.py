import json

import pytest

from bibtexmanager.cli import main

CENTRAL = "@inproceedings{a,\n  booktitle = isca,\n  year = {2020}\n}\n"


def test_strings_requires_output_file(tmp_path):
    bibfile = tmp_path / "central.bib"
    bibfile.write_text(CENTRAL)
    with pytest.raises(SystemExit) as raised:
        main(["format", str(bibfile), "--strings", "abbrev"])
    assert isinstance(raised.value.code, str)
    assert "--strings" in raised.value.code


def test_strings_defines_references_in_new_file(tmp_path):
    conferences = tmp_path / "conferences.json"
    conferences.write_text(json.dumps(
        {"data": {"isca": {"abbreviation": "ISCA", "full_name": "International Symposium",
                           "name": "ISCA"}}}
    ))
    bibfile = tmp_path / "central.bib"
    bibfile.write_text(CENTRAL)
    output = tmp_path / "out.bib"

    main(["format", str(bibfile), "-o", str(output),
          "--strings", "abbrev", "--conferences", str(conferences)])

    result = output.read_text()
    assert "@string{isca = {ISCA}}" in result
    assert "booktitle = isca" in result


def test_keep_cannot_be_used_in_place(tmp_path):
    bibfile = tmp_path / "central.bib"
    bibfile.write_text("@inproceedings{a,\n  title = {T},\n  isbn = {1}\n}\n")
    with pytest.raises(SystemExit) as raised:
        main(["format", str(bibfile), "--keep", "title", "-i"])
    assert isinstance(raised.value.code, str)
    assert "--keep/--drop" in raised.value.code


def test_drop_writes_filtered_output(tmp_path):
    bibfile = tmp_path / "central.bib"
    bibfile.write_text("@inproceedings{a,\n  title = {T},\n  isbn = {1},\n  year = {2020}\n}\n")
    output = tmp_path / "out.bib"
    main(["format", str(bibfile), "-o", str(output), "--drop", "isbn"])
    result = output.read_text()
    assert "isbn" not in result
    assert "title = {T}" in result
