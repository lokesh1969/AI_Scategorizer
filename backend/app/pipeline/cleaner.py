import re

def clean_and_normalize_text(text: str) -> str:
    """
    Cleans extracted raw text while preserving UTF-8 Devanagari script and English alphanumeric formatting.
    """
    if not text:
        return ""

    # Replace multiple newlines with double newline for clean readability
    cleaned = re.sub(r'\n\s*\n+', '\n\n', text)

    # Replace multiple spaces with a single space
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)

    # Remove non-printable control characters (except newline, tab)
    cleaned = "".join(ch for ch in cleaned if ch in ['\n', '\t'] or (ord(ch) >= 32 and ord(ch) != 127))

    return cleaned.strip()
