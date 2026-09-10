import re

NEGATIVE_WORDS = [
    "fire", "accident", "injury", "complaint", "hazard", "leak", "failure", "delay",
    "breakdown", "defect", "distress", "damaged", "urgent", "fault",
    "आपातकालीन", "आग", "दुर्घटना", "घायल", "खराबी", "शिकायत", "क्षतिग्रस्त", "खतरा"
]

POSITIVE_WORDS = [
    "resolved", "completed", "approved", "successful", "repaired", "satisfied",
    "excellent", "good", "clearance", "verified", "passed",
    "सफल", "स्वीकृत", "सुधार", "उत्कृष्ट", "सत्यापित", "पूर्ण"
]

def analyze_sentiment(text: str) -> dict:
    """
    Performs bilingual sentiment analysis returning label (POSITIVE, NEUTRAL, NEGATIVE) and score.
    """
    if not text:
        return {"label": "NEUTRAL", "score": 0.50}

    text_lower = text.lower()

    neg_count = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    pos_count = sum(1 for w in POSITIVE_WORDS if w in text_lower)

    if neg_count > pos_count:
        score = min(0.95, round(0.60 + (neg_count * 0.08), 2))
        return {"label": "NEGATIVE", "score": score}
    elif pos_count > neg_count:
        score = min(0.95, round(0.60 + (pos_count * 0.08), 2))
        return {"label": "POSITIVE", "score": score}
    else:
        return {"label": "NEUTRAL", "score": 0.75}
