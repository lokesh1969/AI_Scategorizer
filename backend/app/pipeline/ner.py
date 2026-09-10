import re
from typing import List, Dict, Any

def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extracts key named entities (PERSON, ORGANIZATION, LOCATION, DATE, MONEY, PHONE, EMAIL, STATION, DOCUMENT_NUMBER).
    Supports English & Hindi text patterns.
    """
    if not text:
        return []

    entities = []
    seen = set()

    def add_entity(txt: str, label: str):
        cleaned = txt.strip(" .,;:()[]")
        key = (cleaned.lower(), label)
        if cleaned and len(cleaned) > 1 and key not in seen:
            seen.add(key)
            entities.append({"text": cleaned, "label": label})

    # 1. MONEY (₹4,50,000 / Rs. 50,000 / $10,000 / INR 5000 / 5,00,000 रुपये)
    money_matches = re.findall(r'(?:₹|Rs\.?|INR|\$)\s*[\d,]+(?:\.\d+)?|\b[\d,]+\s*(?:रुपये|रु|rupees)\b', text, re.IGNORECASE)
    for m in money_matches:
        add_entity(m, "MONEY")

    # 2. DATE (10 September 2026 / 10/09/2026 / 2026-09-10 / 10 सितम्बर 2026)
    date_matches = re.findall(r'\b\d{1,2}[-/\.]\d{1,2}[-/\.]\d{2,4}\b|\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|June|July|August|September|October|November|December|जनवरी|फरवरी|मार्च|अप्रैल|मई|जून|जुलाई|अगस्त|सितम्बर|अक्टूबर|नवंबर|दिसंबर)\s+\d{4}\b', text, re.IGNORECASE)
    for d in date_matches:
        add_entity(d, "DATE")

    # 3. EMAIL
    email_matches = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    for e in email_matches:
        add_entity(e, "EMAIL")

    # 4. PHONE
    phone_matches = re.findall(r'\b(?:\+91[\-\s]?)?[6-9]\d{9}\b|\b\d{3,4}[\-\s]?\d{6,8}\b', text)
    for p in phone_matches:
        add_entity(p, "PHONE")

    # 5. DOCUMENT NUMBER / INVOICE NUMBER
    doc_no_matches = re.findall(r'\b(?:Invoice|Bill|PO|Order|Report|Doc|ID|Ref|फाइल संख्या|रसीद संख्या)\s*(?:#|No\.?|:)?\s*([A-Za-z0-9\-]+)\b', text, re.IGNORECASE)
    for dn in doc_no_matches:
        add_entity(dn, "DOCUMENT_NUMBER")

    # 6. METRO STATION / PLATFORM / LOCATION
    station_matches = re.findall(r'\b(?:Platform\s*\d+|Platform\s*number\s*\d+|प्लेटफॉर्म\s*(?:नंबर\s*)?\d+|[A-Z][a-z]+\s+(?:Central|West|East|North|South|Junction|Station|Terminal|Chowk|Marg))\b', text, re.IGNORECASE)
    for st in station_matches:
        add_entity(st, "STATION")

    # 7. EQUIPMENT / MACHINERY
    equipment_matches = re.findall(r'\b(?:HVAC|escalator|elevator|motor|transformer|fire alarm|compressor|generator|track switch|अग्निशामक|एस्केलेटर|मोटर|जनरेटर)\b', text, re.IGNORECASE)
    for eq in equipment_matches:
        add_entity(eq, "EQUIPMENT")

    # 8. PERSON / ORGANIZATION
    person_matches = re.findall(r'\b(?:Mr\.?|Ms\.?|Dr\.?|Officer|Manager|Shri|Smt\.?)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b', text)
    for pr in person_matches:
        add_entity(pr, "PERSON")

    org_matches = re.findall(r'\b(?:Metro Rail Corporation|DMRC|MMRCL|Indian Railways|Finance Dept|Maintenance Corp|Safety Board)\b', text, re.IGNORECASE)
    for og in org_matches:
        add_entity(og, "ORGANIZATION")

    return entities[:12] # Limit top 12 extracted entities
