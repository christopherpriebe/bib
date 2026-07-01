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

## Development

```sh
pip install -e ".[test]"
pytest
```
