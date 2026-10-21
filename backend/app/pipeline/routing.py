from typing import Tuple
from backend.app.core.categories import DEPARTMENT_MAP, HUMAN_QUEUE


def route_document(category: str, confidence: float, threshold: float) -> Tuple[str, str]:
    """
    Determines assigned department and verification status based on classification & confidence threshold.
    Unknown categories are never auto-routed.
    Returns: (assigned_department, verification_status)
    """
    if category in DEPARTMENT_MAP and confidence >= threshold:
        return DEPARTMENT_MAP[category], "AI VERIFIED"
    return HUMAN_QUEUE, "HUMAN VERIFICATION REQUIRED"
