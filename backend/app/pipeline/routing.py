from typing import Tuple

DEPARTMENT_MAP = {
    "SAFETY": "Station Controller",
    "OPERATIONS": "Station Controller",
    "FINANCE": "Finance Manager",
    "MAINTENANCE": "Maintenance Head"
}

def route_document(category: str, confidence: float, threshold: float) -> Tuple[str, str]:
    """
    Determines assigned department and verification status based on classification & confidence threshold.
    Returns: (assigned_department, verification_status)
    """
    target_department = DEPARTMENT_MAP.get(category, "Station Controller")

    if confidence >= threshold:
        verification_status = "AI VERIFIED"
        assigned_department = target_department
    else:
        verification_status = "HUMAN VERIFICATION REQUIRED"
        assigned_department = "Human Verification Queue"

    return assigned_department, verification_status
