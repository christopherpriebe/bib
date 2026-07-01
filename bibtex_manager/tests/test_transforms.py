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
    # The bare reference stays a reference, not an expanded literal.
    assert "booktitle = isca" in out
    assert "{ISCA}" not in out.split("@article")[1]  # not expanded inside the entry


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
    # 'the' -> 'The' in the title, but the protected venue name is untouched.
    assert "The {NVIDIA} Architecture" in out


def test_strip_failure_markers_removes_prior_run_comments():
    marked = "% WARNING Parsing failed for the following 3 lines.\n" + SAMPLE
    lib = serialization.read_string(marked)
    cleaned = transforms.strip_failure_markers(lib)
    out = serialization.write_string(cleaned)
    assert "WARNING Parsing failed" not in out
