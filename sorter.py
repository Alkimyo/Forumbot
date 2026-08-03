"""Uzbek alphabet sorting module.

Provides sorting utilities that order strings according to the official
Uzbek Latin alphabet order, including the digraphs "Sh", "Ch", "Gʻ", "Oʻ",
instead of relying on plain Python `sort()` (which uses codepoint order and
gets Uzbek-specific letters and digraphs wrong).
"""

from __future__ import annotations

from typing import Sequence, TypeVar

# Official Uzbek Latin alphabet order.
# Digraphs ("Sh", "Ch") and modified letters ("Gʻ", "Oʻ") are listed as
# multi-character tokens so they can be matched greedily before single
# letters during tokenization.
_UZBEK_ALPHABET: list[str] = [
    "A", "B", "D", "E", "F", "G", "Gʻ", "H", "I", "J", "K", "L", "M", "N",
    "O", "Oʻ", "P", "Q", "R", "S", "Sh", "T", "U", "V", "X", "Y", "Z", "Ch",
]

# Alternate apostrophe characters people commonly type instead of the
# proper modifier letter "ʻ" (U+02BB). We normalize all of them.
_APOSTROPHE_VARIANTS = ("'", "’", "`", "ʼ", "‘")


def _normalize_apostrophes(text: str) -> str:
    """Replace all apostrophe-like characters with the canonical "ʻ".

    Args:
        text: Input string.

    Returns:
        String with normalized apostrophes.
    """
    for variant in _APOSTROPHE_VARIANTS:
        text = text.replace(variant, "ʻ")
    return text


def _build_sort_key_table() -> dict[str, int]:
    """Build a lookup table mapping lowercase alphabet tokens to their rank.

    Longer (multi-character) tokens are given priority during tokenization
    since they must be matched before their single-character prefixes
    (e.g. "Sh" before "S").

    Returns:
        Mapping from lowercase token to its sort rank.
    """
    return {token.lower(): index for index, token in enumerate(_UZBEK_ALPHABET)}


_SORT_RANK = _build_sort_key_table()

# Tokens ordered from longest to shortest so tokenization can greedily
# match digraphs before single letters.
_TOKENS_BY_LENGTH_DESC = sorted(_SORT_RANK.keys(), key=len, reverse=True)

# A rank assigned to any character that doesn't belong to the Uzbek
# alphabet (digits, punctuation, foreign letters). Placed after all
# alphabet letters so such characters sort last, in their own codepoint
# order.
_UNKNOWN_RANK_BASE = len(_UZBEK_ALPHABET)


def _tokenize(text: str) -> list[str]:
    """Split a string into Uzbek-alphabet tokens (letters/digraphs).

    Args:
        text: Normalized, lowercase input string.

    Returns:
        List of tokens, each either a recognized alphabet token or a
        single unrecognized character.
    """
    tokens: list[str] = []
    i = 0
    length = len(text)
    while i < length:
        matched = False
        for token in _TOKENS_BY_LENGTH_DESC:
            token_len = len(token)
            if text[i:i + token_len] == token:
                tokens.append(token)
                i += token_len
                matched = True
                break
        if not matched:
            tokens.append(text[i])
            i += 1
    return tokens


def uzbek_sort_key(text: str) -> tuple:
    """Compute a sort key for a string using Uzbek alphabet order.

    Args:
        text: The string to compute a sort key for.

    Returns:
        A tuple of integers (and fallback codepoints) suitable for use as
        a `key=` argument to `sorted()`.
    """
    normalized = _normalize_apostrophes(text).lower().strip()
    tokens = _tokenize(normalized)

    key: list[tuple[int, int]] = []
    for token in tokens:
        rank = _SORT_RANK.get(token)
        if rank is not None:
            key.append((rank, 0))
        else:
            # Unknown character: sort after all alphabet letters, then by
            # codepoint to keep a stable, deterministic order.
            key.append((_UNKNOWN_RANK_BASE, ord(token)))
    return tuple(key)


T = TypeVar("T")


def sort_by_uzbek_alphabet(
    items: Sequence[T],
    key=lambda item: item,
) -> list[T]:
    """Sort a sequence of items according to the Uzbek alphabet.

    Args:
        items: The sequence of items to sort.
        key: A function extracting the string to sort by from each item.
            Defaults to the identity function (item is itself a string).

    Returns:
        A new list with items sorted in Uzbek alphabetical order.
    """
    return sorted(items, key=lambda item: uzbek_sort_key(key(item)))
