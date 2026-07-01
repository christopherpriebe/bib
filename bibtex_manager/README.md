# BibTeX Manager
A small Python package to help manage BibTeX files.

## Install

```sh
pip install -e .
```

## Usage

```sh
managebib format path/to/refs.bib          # print sorted + title-cased result to stdout
managebib format refs.bib -i               # rewrite the file in place
managebib format refs.bib -o out.bib       # write to a different file
managebib format refs.bib --no-titlecase   # only sort, don't touch titles
managebib format refs.bib --case-sensitive # case-sensitive key sort
```

`format` sorts entries by citation key and title-cases the `title` field.

### Curly braces are preserved verbatim

Anything wrapped in `{curly braces}` in a title is left exactly as written. 
It is never re-capitalized or split. Use this to protect naming conventions:

```bibtex
title = {Exploring Efficient {ML}-Based Scheduling for {RISC-V}}
```

Tokens that already contain an uppercase letter (acronyms like `FPGA`, camelCase names like `iPhone`) are also left as-is, so you only need braces for all-lowercase or multi-word names you want protected (e.g. `{gem5}`, `{the Halide compiler}`).

`@string` abbreviations are preserved as references (`booktitle = isca` stays a reference and is **not** expanded to `{ISCA}`).
Duplicate citation keys are reported on stderr and left in place for you to resolve.

### Generating `@string` definitions from venue tables

Keep your central `.bib` using bare references (`booktitle = isca`, `journal = cacm`) with **no** `@string` block. 
When you generate a concrete file, `--strings` looks each reference up and prepends the matching `@string` definitions in the form you choose:

```sh
managebib format central.bib -o venue-abbrev.bib --strings abbrev  # @string{isca = {ISCA}}
managebib format central.bib -o venue-full.bib   --strings full    # @string{isca = {International Symposium ...}}
```

- Forms: `full` (full name), `abbrev` (abbreviation), `name` (short name).
- `booktitle` references resolve against `conferences.json`; `journal` references against `journals.json`. Both ship bundled in the package; override either with `--conferences PATH` / `--journals PATH`.
- `--strings` **requires `-o`** so it can never mutate the central file; the bare references in entries are left untouched (only the `@string` block is added).
- A reference with no matching entry is reported on stderr and left undefined.

Data files use this shape:

```json
{ "data": { "isca": { "name": "...", "full_name": "...", "abbreviation": "ISCA" } } }
```

### Selecting which fields to include

Keep everything in your central `.bib`; drop fields only when generating a copy. Use `--keep` for an allowlist or `--drop` for a denylist (they are mutually exclusive):

```sh
managebib format central.bib -o conf.bib --keep author,title,booktitle,journal,year
managebib format central.bib -o slim.bib --drop publisher,isbn,abstract
```

- Field names are comma-separated and matched case-insensitively; the entry type and citation key are always kept.
- List both `booktitle` and `journal` in `--keep` so conference and journal entries each keep their own venue field.
- `--keep`/`--drop` may write to `-o` or stdout (for previewing) but **not** `-i`, so the central file never loses fields.
- Combine with `--strings`: filtering runs first, so only the references you keep get an `@string` definition.

## Development

```sh
pip install -e ".[test]"
pytest
```
