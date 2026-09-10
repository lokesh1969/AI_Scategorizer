from fastapi import APIRouter, Depends
from backend.app.db.database import db_adapter
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/stats")
def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    role = current_user["role"]
    query = {}
    if role == "UPLOADER":
        query["uploader_id"] = current_user["_id"]

    all_docs = db_adapter.get_documents(query)

    total_docs = len(all_docs)
    processed = len([d for d in all_docs if d.get("processing_status") == "COMPLETED"])
    pending = total_docs - processed
    human_verification_count = len([d for d in all_docs if d.get("verification_status") == "HUMAN VERIFICATION REQUIRED"])

    # Priorities
    priority_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for d in all_docs:
        p_lvl = d.get("priority", {}).get("level", "LOW")
        if p_lvl in priority_counts:
            priority_counts[p_lvl] += 1

    # Categories
    category_counts = {"SAFETY": 0, "FINANCE": 0, "MAINTENANCE": 0, "OPERATIONS": 0}
    for d in all_docs:
        cat = d.get("classification", {}).get("predicted_category", "OPERATIONS")
        if cat in category_counts:
            category_counts[cat] += 1
        else:
            category_counts[cat] = category_counts.get(cat, 0) + 1

    # Languages
    language_counts = {"English": 0, "Hindi": 0, "Mixed (Hindi + English)": 0}
    for d in all_docs:
        lang = d.get("language", "English")
        language_counts[lang] = language_counts.get(lang, 0) + 1

    # Average confidence
    confidences = [d.get("classification", {}).get("confidence", 0.0) for d in all_docs if d.get("classification")]
    avg_confidence = round(sum(confidences) / len(confidences), 1) if confidences else 0.0

    human_verification_rate = round((human_verification_count / total_docs * 100.0), 1) if total_docs > 0 else 0.0

    recent_documents = all_docs[:5]
    critical_documents = [d for d in all_docs if d.get("priority", {}).get("level") == "CRITICAL"][:5]

    return {
        "total_documents": total_docs,
        "processed_documents": processed,
        "pending_documents": pending,
        "human_verification_count": human_verification_count,
        "human_verification_rate": human_verification_rate,
        "average_confidence": avg_confidence,
        "priority_counts": priority_counts,
        "category_counts": category_counts,
        "language_counts": language_counts,
        "recent_documents": recent_documents,
        "critical_documents": critical_documents
    }
