import re
from typing import Tuple, Dict, Any

CRITICAL_KEYWORDS = [
    "fire", "explosion", "accident", "injury", "fatal", "emergency", "gas leak",
    "evacuation", "terror", "hazard", "threat", "casualty", "collapse",
    "आपातकालीन", "आग", "दुर्घटना", "घायल", "खतरा", "इमरजेंसी", "धमाका"
]

HIGH_KEYWORDS = [
    "breakdown", "fault", "defect", "failure", "halt", "urgent", "stoppage",
    "delay", "breach", "complaint", "power outage", "derailment",
    "खराबी", "तकनिकी समस्या", "रुकावट", "तुरंत", "गंभीर", "मशीन बंद"
]

MEDIUM_KEYWORDS = [
    "invoice", "budget", "expenditure", "payment", "due date", "servicing",
    "inspection", "schedule", "audit", "purchase order",
    "बजट", "भुगतान", "इनवॉइस", "निरीक्षण", "मरम्मत"
]

def calculate_priority(category: str, text: str) -> Tuple[str, int, str]:
    """
    Evaluates urgency and priority level of document text based on category + emergency context.
    Returns: (priority_level, score, reason_description)
    """
    text_lower = text.lower()

    # Find matching keywords
    found_critical = [kw for kw in CRITICAL_KEYWORDS if kw in text_lower]
    found_high = [kw for kw in HIGH_KEYWORDS if kw in text_lower]
    found_medium = [kw for kw in MEDIUM_KEYWORDS if kw in text_lower]

    base_score = 30
    if category == "SAFETY":
        base_score += 35
    elif category == "MAINTENANCE":
        base_score += 25
    elif category == "OPERATIONS":
        base_score += 20
    elif category == "FINANCE":
        base_score += 15

    # Keyword bonuses
    if found_critical:
        base_score += 35 + (len(found_critical) * 5)
    elif found_high:
        base_score += 25 + (len(found_high) * 3)
    elif found_medium:
        base_score += 15

    score = min(99, max(15, base_score))

    if score >= 85:
        level = "CRITICAL"
        if found_critical:
            reason = f"Safety-related emergency incident detected. Found emergency terms: '{', '.join(found_critical[:3])}'."
        else:
            reason = f"Critical document severity evaluated for category '{category}'."
    elif score >= 65:
        level = "HIGH"
        if found_high:
            reason = f"High priority operational/equipment disruption detected. Found terms: '{', '.join(found_high[:3])}'."
        else:
            reason = f"High priority rating assigned based on '{category}' category impact."
    elif score >= 40:
        level = "MEDIUM"
        reason = f"Standard medium priority operational/financial document."
    else:
        level = "LOW"
        reason = f"Routine low priority administrative document."

    return level, score, reason
