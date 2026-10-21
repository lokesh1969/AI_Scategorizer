"""
Single source of truth for document categories, departments and role access.
Every other module (routing, RBAC, dashboard, settings) imports from here so the
taxonomy can never drift out of sync again.
"""

CATEGORIES = ["FINANCE", "HR", "LEGAL", "OPERATIONS"]

# Category -> department that receives auto-routed documents
DEPARTMENT_MAP = {
    "FINANCE": "Finance Manager",
    "HR": "HR Manager",
    "LEGAL": "Legal Counsel",
    "OPERATIONS": "Operations Manager",
}

HUMAN_QUEUE = "Human Verification Queue"

# Department role -> categories that role may view
ROLE_CATEGORIES = {
    "FINANCE_MANAGER": ["FINANCE"],
    "HR_MANAGER": ["HR"],
    "LEGAL_COUNSEL": ["LEGAL"],
    "OPERATIONS_MANAGER": ["OPERATIONS"],
}

# Roles allowed to review the human verification queue (ADMIN is always allowed)
REVIEWER_ROLES = list(ROLE_CATEGORIES.keys())


def can_view_document(user: dict, doc: dict) -> bool:
    """Backend RBAC rule shared by the list and detail endpoints."""
    role = user.get("role")
    if role == "ADMIN":
        return True
    if doc.get("uploader_id") == user.get("_id"):
        return True
    if role in ROLE_CATEGORIES:
        if doc.get("verification_status") == "HUMAN VERIFICATION REQUIRED":
            return True
        category = doc.get("classification", {}).get("predicted_category")
        return category in ROLE_CATEGORIES[role]
    return False
