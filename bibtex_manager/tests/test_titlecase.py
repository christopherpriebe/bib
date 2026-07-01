import pytest

from bibtexmanager.titlecase import capitalize_title


@pytest.mark.parametrize("raw, expected", [
    # Plain title case: first word capitalized, short words lowercased.
    ("a study of the machine", "A Study of the Machine"),
    # Unbraced acronyms keep their existing capitalization.
    ("efficient FPGA and GPU acceleration", "Efficient FPGA and GPU Acceleration"),
    # Unbraced camelCase names are preserved (already carry an uppercase letter).
    ("the iPhone and eDRAM era", "The iPhone and eDRAM Era"),
    # A single braced token is left completely untouched.
    ("the {iPhone} era", "The {iPhone} Era"),
    # A multi-word braced phrase is opaque: no splitting, no re-casing.
    ("study of {the LLM Compiler} today", "Study of {the LLM Compiler} Today"),
    # Braces mixed inside a hyphenated word.
    ("an {ML}-based scheduler", "An {ML}-Based Scheduler"),
    # Short word inside braces is NOT lowercased.
    ("results {for the win}", "Results {for the win}"),
    # First word after a colon (subtitle) is capitalized even if it is short.
    ("axbench: a benchmark suite", "Axbench: A Benchmark Suite"),
    # Hyphenated compounds capitalize each unprotected part.
    ("in-dram near-data acceleration", "In-Dram Near-Data Acceleration"),
    # Protected hyphenated name stays verbatim.
    ("the {RISC-V} manual", "The {RISC-V} Manual"),
    # Leading punctuation is skipped when capitalizing.
    ('"quoted" beginnings', '"Quoted" Beginnings'),
    # A brace-protected capital keeps the rest of the token lowercase.
    ("{JAX}: composable {P}ython programs", "{JAX}: Composable {P}ython Programs"),
])
def test_capitalize_title(raw, expected):
    assert capitalize_title(raw) == expected


def test_capitalize_title_is_idempotent():
    once = capitalize_title("study of {the LLM Compiler}: an {ML}-based approach for us")
    assert capitalize_title(once) == once


def test_capitalize_title_never_touches_brace_contents():
    # Whatever is inside the outermost braces must appear verbatim in the output.
    assert "{tHe wEIRD CaSe}" in capitalize_title("look at {tHe wEIRD CaSe} now")
