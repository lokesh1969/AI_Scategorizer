from backend.app.pipeline.text_utils import find_keywords

# Lexicon-based heuristic; matched as whole tokens so "good" does not match "goods".
NEGATIVE_WORDS = [
    "fire", "accident", "injury", "complaint", "hazard", "leak", "failure", "delay",
    "breakdown", "defect", "distress", "damaged", "urgent", "fault", "rejected",
    "overdue", "penalty", "dispute", "lawsuit", "violation", "termination",
    "आपातकालीन", "आग", "दुर्घटना", "घायल", "खराबी", "शिकायत", "क्षतिग्रस्त", "खतरा", "अस्वीकृत"
]

POSITIVE_WORDS = [
    "resolved", "completed", "approved", "successful", "repaired", "satisfied",
    "excellent", "good", "clearance", "verified", "passed", "accepted", "welcome",
    "सफल", "स्वीकृत", "सुधार", "उत्कृष्ट", "सत्यापित", "पूर्ण"
]


def analyze_sentiment(text: str) -> dict:
    """
    Bilingual lexicon sentiment returning label (POSITIVE, NEUTRAL, NEGATIVE) and score.
    """
    if not text:
        return {"label": "NEUTRAL", "score": 0.50}

    neg_count = len(find_keywords(text, NEGATIVE_WORDS))
    pos_count = len(find_keywords(text, POSITIVE_WORDS))

    if neg_count > pos_count:
        return {"label": "NEGATIVE", "score": min(0.95, round(0.60 + neg_count * 0.08, 2))}
    if pos_count > neg_count:
        return {"label": "POSITIVE", "score": min(0.95, round(0.60 + pos_count * 0.08, 2))}
    return {"label": "NEUTRAL", "score": 0.75}
