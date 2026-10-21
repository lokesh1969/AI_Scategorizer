import re
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

DEVANAGARI_WORD = re.compile(r"[ऀ-ॿ]+")
LATIN_WORD = re.compile(r"[A-Za-z]{2,}")

# A script must make up at least this share of words for the text to count as mixed,
# so a Hindi letter that quotes one English acronym is still "Hindi".
MIXED_MIN_SHARE = 0.10


def detect_language(text: str) -> str:
    """
    Returns 'English', 'Hindi', or 'Mixed (Hindi + English)' using word-level
    script counts, with langdetect as a tie-breaker for Latin-only text.
    """
    if not text or not text.strip():
        return "English"

    dev_words = len(DEVANAGARI_WORD.findall(text))
    lat_words = len(LATIN_WORD.findall(text))
    total = dev_words + lat_words
    if total == 0:
        return "English"

    dev_share = dev_words / total
    if dev_words and lat_words and MIXED_MIN_SHARE <= dev_share <= 1 - MIXED_MIN_SHARE:
        return "Mixed (Hindi + English)"
    if dev_share > 0.5:
        return "Hindi"

    try:
        if detect(text) == "hi":
            return "Hindi"
    except Exception:
        pass
    return "English"
