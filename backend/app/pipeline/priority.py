from typing import Tuple
from backend.app.pipeline.text_utils import find_keywords

# Rule-based heuristic (not a learned model). Keywords are matched as whole
# tokens/phrases, so "fire" does not fire on "firewall" or "fired".
CRITICAL_KEYWORDS = [
    "fire", "explosion", "accident", "injury", "injuries", "fatal", "emergency", "gas leak",
    "evacuation", "hazard", "casualty", "collapse", "data breach", "court order",
    "summons", "arrest warrant", "harassment", "fraud",
    "आपातकालीन", "आग", "दुर्घटना", "घायल", "खतरा", "इमरजेंसी", "धमाका", "धोखाधड़ी", "उत्पीड़न"
]

HIGH_KEYWORDS = [
    "breakdown", "fault", "defect", "failure", "outage", "urgent", "urgently", "immediately",
    "stoppage", "delay", "breach", "complaint", "lawsuit", "legal notice", "penalty",
    "overdue", "deadline", "termination", "dispute", "non-compliance", "escalation",
    "खराबी", "रुकावट", "तुरंत", "गंभीर", "शिकायत", "जुर्माना", "समय सीमा", "कानूनी नोटिस"
]

MEDIUM_KEYWORDS = [
    "invoice", "budget", "expenditure", "payment", "due date", "inspection", "schedule",
    "audit", "purchase order", "contract", "agreement", "renewal", "appraisal", "leave",
    "बजट", "भुगतान", "इनवॉइस", "निरीक्षण", "अनुबंध", "छुट्टी"
]

# Baseline urgency contributed by the predicted category
CATEGORY_BASE = {
    "LEGAL": 25,
    "OPERATIONS": 20,
    "FINANCE": 15,
    "HR": 10,
}


def calculate_priority(category: str, text: str) -> Tuple[str, int, str]:
    """
    Evaluates urgency of a document from category context + keyword evidence.
    Returns: (priority_level, score 0-100, reason_description)
    """
    found_critical = find_keywords(text, CRITICAL_KEYWORDS)
    found_high = find_keywords(text, HIGH_KEYWORDS)
    found_medium = find_keywords(text, MEDIUM_KEYWORDS)

    score = 30 + CATEGORY_BASE.get(category, 0)
    if found_critical:
        score += 40 + len(found_critical) * 5
    elif found_high:
        score += 25 + len(found_high) * 3
    elif found_medium:
        score += 10

    score = min(99, max(15, score))

    if score >= 85:
        level = "CRITICAL"
        if found_critical:
            reason = f"Critical incident terms detected: '{', '.join(found_critical[:3])}'."
        else:
            reason = f"Critical severity evaluated for category '{category}'."
    elif score >= 65:
        level = "HIGH"
        if found_high:
            reason = f"Urgent or disruptive terms detected: '{', '.join(found_high[:3])}'."
        else:
            reason = f"High priority based on '{category}' category impact."
    elif score >= 40:
        level = "MEDIUM"
        reason = "Standard business document."
    else:
        level = "LOW"
        reason = "Routine low priority document."

    return level, score, reason
