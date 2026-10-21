import re
from typing import Iterable, List

# Splits on whitespace and punctuation (including the Hindi danda). Devanagari
# vowel signs are not "word" characters for Python's \b, so regex word
# boundaries cannot be used for Hindi; token matching works for both scripts.
_TOKEN_SPLIT = re.compile(r"[\s\.,;:!?\(\)\[\]{}\"'“”‘’।॥|/\\\-–—_*#&+=<>]+")


def tokenize(text: str) -> List[str]:
    return [t for t in _TOKEN_SPLIT.split(text.lower()) if t]


def find_keywords(text: str, keywords: Iterable[str]) -> List[str]:
    """
    Returns the keywords (single words or multi-word phrases) that occur in the
    text as whole tokens. "fire" matches "fire" but not "firewall" or "fired";
    "आग" (fire) does not match "आगमन" (arrival).
    """
    haystack = " " + " ".join(tokenize(text)) + " "
    found = []
    for kw in keywords:
        needle = " " + " ".join(tokenize(kw)) + " "
        if needle.strip() and needle in haystack:
            found.append(kw)
    return found
