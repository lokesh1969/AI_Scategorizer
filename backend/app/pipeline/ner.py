import re
from typing import List, Dict

# Rule-based (regex) entity extraction. Labels: MONEY, DATE, EMAIL, PHONE,
# DOCUMENT_NUMBER, PERSON, ORGANIZATION. Supports English and Hindi patterns.

_MONTHS = (
    "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|January|February|March|April|June|July|"
    "August|September|October|November|December|जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितम्बर|सितंबर|अक्टूबर|नवंबर|दिसंबर"
)

MONEY_RE = re.compile(r"(?:₹|Rs\.?|INR|USD|\$)\s*\d[\d,]*(?:\.\d+)?|\b\d[\d,]*(?:\.\d+)?\s*(?:रुपये|rupees)", re.IGNORECASE)
DATE_RE = re.compile(
    rf"\b\d{{1,2}}[-/.]\d{{1,2}}[-/.]\d{{2,4}}\b|\b\d{{4}}-\d{{2}}-\d{{2}}\b|\b\d{{1,2}}\s+(?:{_MONTHS})\.?,?\s+\d{{4}}\b",
    re.IGNORECASE,
)
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<![\d-])(?:\+91[\-\s]?)?[6-9]\d{9}(?![\d-])|(?<![\d-])0\d{2,4}[\-\s]\d{6,8}(?![\d-])")
# The prefix must be a whole word and the identifier must contain a digit, so
# "Documentation" or "Billing" no longer yield fragments like "umentation".
DOC_NO_RE = re.compile(
    r"\b(?:Invoice|Bill|PO|Order|Report|Doc|Ref|Case|Contract|Policy|ID|फाइल संख्या|रसीद संख्या)\b"
    r"\s*(?:#|No\.?|Number|:)?\s*:?\s*([A-Za-z]*[\-/]?\d[A-Za-z0-9\-/]*)",
    re.IGNORECASE,
)
PERSON_RE = re.compile(r"\b(?:Mr|Ms|Mrs|Dr|Shri|Smt)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b")
ORG_RE = re.compile(r"\b(?:[A-Z][A-Za-z&]+\s+){1,4}(?:Ltd|Limited|Inc|LLP|LLC|Pvt|Corporation|Corp|Company|Bank)\b\.?")


def extract_entities(text: str, limit: int = 15) -> List[Dict[str, str]]:
    if not text:
        return []

    entities = []
    seen = set()

    def add(txt: str, label: str):
        cleaned = txt.strip(" .,;:()[]")
        key = (cleaned.lower(), label)
        if len(cleaned) > 1 and key not in seen:
            seen.add(key)
            entities.append({"text": cleaned, "label": label})

    for m in MONEY_RE.findall(text):
        add(m, "MONEY")
    for m in DATE_RE.findall(text):
        add(m, "DATE")
    for m in EMAIL_RE.findall(text):
        add(m, "EMAIL")
    for m in PHONE_RE.findall(text):
        add(m, "PHONE")
    for m in DOC_NO_RE.findall(text):
        add(m, "DOCUMENT_NUMBER")
    for m in PERSON_RE.findall(text):
        add(m, "PERSON")
    for m in ORG_RE.findall(text):
        add(m, "ORGANIZATION")

    return entities[:limit]
