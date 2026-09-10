import re
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

def detect_language(text: str) -> str:
    """
    Detects whether text is 'English', 'Hindi', or 'Mixed (Hindi + English)'.
    Uses character set count (Devanagari vs Latin) and langdetect algorithm.
    """
    if not text or not text.strip():
        return "English"

    # Count Devanagari Unicode characters (U+0900 to U+097F)
    devanagari_chars = len(re.findall(r'[\u0900-\u097F]', text))
    latin_chars = len(re.findall(r'[a-zA-Z]', text))

    total_chars = devanagari_chars + latin_chars
    if total_chars == 0:
        return "English"

    # If both Devanagari script and Latin characters are present
    if devanagari_chars >= 1 and latin_chars >= 3:
        return "Mixed (Hindi + English)"

    if devanagari_chars > 0 and latin_chars == 0:
        return "Hindi"

    dev_ratio = devanagari_chars / total_chars if total_chars else 0
    if dev_ratio > 0.70:
        return "Hindi"

    try:
        detected = detect(text)
        if detected == 'hi':
            return "Hindi"
        elif detected == 'en':
            return "English"
    except Exception:
        pass

    return "English"
