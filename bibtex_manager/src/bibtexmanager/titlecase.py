"""Title-case strings while protecting names that must not be re-cased.

Two kinds of text are preserved verbatim:

* anything wrapped in ``{curly braces}`` (BibTeX's own case-protection), and
* any token that already carries an uppercase letter (acronyms such as ``FPGA``
  or camelCase names such as ``iPhone``).

Everything else is title-cased: the first word of the title and of each
subtitle is capitalized, common short words are lowercased, and the first
letter of every other word is capitalized.

This module is pure text processing and has no BibTeX dependency.
"""

_WORDS_KEPT_LOWERCASE = frozenset({
    "a", "an", "the",
    "and", "as", "but", "for", "if", "nor", "or", "so", "yet",
    "at", "by", "in", "of", "off", "on", "per", "to", "up", "via", "vs",
})

_CLAUSE_ENDING_PUNCTUATION = (":", "?", "!")


def capitalize_title(title):
    """Return ``title`` in title case, leaving ``{brace-protected}`` text as-is."""
    must_capitalize = True
    result = []
    for is_whitespace, token in _iterate_tokens(title):
        if is_whitespace:
            result.append(token)
            continue
        result.append(_recase_word(token, must_capitalize))
        must_capitalize = token.rstrip().endswith(_CLAUSE_ENDING_PUNCTUATION)
    return "".join(result)


def _iterate_tokens(title):
    """Yield ``(is_whitespace, text)`` tokens, not splitting inside braces."""
    token_characters = []
    brace_depth = 0
    current_is_whitespace = None
    for character in title:
        is_whitespace = character.isspace() and brace_depth == 0
        if character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth = max(0, brace_depth - 1)

        if current_is_whitespace is None:
            current_is_whitespace = is_whitespace
            token_characters = [character]
        elif is_whitespace == current_is_whitespace:
            token_characters.append(character)
        else:
            yield current_is_whitespace, "".join(token_characters)
            current_is_whitespace = is_whitespace
            token_characters = [character]

    if token_characters:
        yield current_is_whitespace, "".join(token_characters)


def _recase_word(word, must_capitalize):
    """Apply title-case rules to a single whitespace-delimited word.

    Any ``{...}`` region is left verbatim: it is never re-cased, never split,
    and a braced word is never treated as one that stays lowercase.
    """
    leading, core, trailing = _strip_edge_punctuation(word)
    if not core:
        return word

    if not must_capitalize and _stays_lowercase(core):
        return leading + core.lower() + trailing

    recased_parts = [
        part if _is_already_cased(part) else _capitalize_first_unprotected(part)
        for part in _split_unprotected(core, "-")
    ]
    return leading + "-".join(recased_parts) + trailing


def _stays_lowercase(core):
    """Report whether a word stays lowercase mid-title and is not brace-protected."""
    return "{" not in core and core.lower() in _WORDS_KEPT_LOWERCASE


def _is_already_cased(part):
    """Report whether a token's casing is deliberate and must be preserved.

    A token that already contains an uppercase letter is assumed to be an
    acronym (``FPGA``), a camelCase name (``iPhone``), or a brace-protected
    capital (``{P}ython``), none of which should be re-cased.
    """
    return any(character.isupper() for character in part)


def _strip_edge_punctuation(word):
    """Split a word into ``(leading, core, trailing)`` punctuation runs.

    Curly braces count as part of the core, never as edge punctuation, so a
    protected token like ``{ML})`` keeps its opening brace.
    """
    def is_edge_character(character):
        return not (character.isalnum() or character in "{}")

    start = 0
    end = len(word)
    while start < end and is_edge_character(word[start]):
        start += 1
    while end > start and is_edge_character(word[end - 1]):
        end -= 1
    return word[:start], word[start:end], word[end:]


def _capitalize_first_unprotected(text):
    """Uppercase the first letter that is not inside curly braces."""
    brace_depth = 0
    for index, character in enumerate(text):
        if character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth = max(0, brace_depth - 1)
        elif brace_depth == 0 and character.isalpha():
            return text[:index] + character.upper() + text[index + 1:]
    return text


def _split_unprotected(text, separator):
    """Split ``text`` on ``separator``, but only at brace depth zero."""
    parts = []
    current_part = []
    brace_depth = 0
    for character in text:
        if character == "{":
            brace_depth += 1
        elif character == "}":
            brace_depth = max(0, brace_depth - 1)
        if character == separator and brace_depth == 0:
            parts.append("".join(current_part))
            current_part = []
        else:
            current_part.append(character)
    parts.append("".join(current_part))
    return parts
