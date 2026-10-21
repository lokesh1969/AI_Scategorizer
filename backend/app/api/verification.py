from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from backend.app.models.schemas import VerificationInput
from backend.app.db.database import db_adapter
from backend.app.api.deps import require_roles
from backend.app.core.categories import DEPARTMENT_MAP, REVIEWER_ROLES

router = APIRouter(prefix="/verification", tags=["Human Verification"])


@router.get("", response_model=list)
def get_verification_queue(current_user: dict = Depends(require_roles(REVIEWER_ROLES))):
    """Returns documents flagged for human verification."""
    return db_adapter.get_documents({"verification_status": "HUMAN VERIFICATION REQUIRED"})


@router.post("/verify/{doc_id}")
def submit_human_verification(
    doc_id: str,
    payload: VerificationInput,
    current_user: dict = Depends(require_roles(REVIEWER_ROLES)),
):
    doc = db_adapter.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Department reviewers work the queue; only an admin may re-label an already routed document
    if doc.get("verification_status") != "HUMAN VERIFICATION REQUIRED" and current_user["role"] != "ADMIN":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document is not awaiting human verification")

    new_category = payload.verified_category.upper()
    if new_category not in DEPARTMENT_MAP:
        raise HTTPException(status_code=400, detail=f"Invalid target category '{new_category}'")

    classification = doc.get("classification", {})
    # Older records predate model_prediction; fall back to the category they were saved with
    model_prediction = classification.get("model_prediction", classification.get("predicted_category"))
    target_department = DEPARTMENT_MAP[new_category]

    updates = {
        "verification_status": "HUMAN VERIFIED",
        "verified_category": new_category,
        "assigned_department": target_department,
        "verifier_id": current_user["_id"],
        "verifier_name": current_user["name"],
        "verification_notes": payload.notes or "",
        "verification_timestamp": datetime.now().isoformat(),
        "human_override": new_category != model_prediction,
        # Current category changes; classification.model_prediction keeps the model's answer
        "classification.predicted_category": new_category,
        "classification.model_prediction": model_prediction,
    }
    db_adapter.update_document(doc_id, updates)

    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "HUMAN_VERIFIED",
        "document_id": doc_id,
        "details": {
            "model_prediction": model_prediction,
            "verified_category": new_category,
            "verifier": current_user["name"],
            "notes": payload.notes,
        },
    })

    return {
        "message": "Human verification completed successfully",
        "doc_id": doc_id,
        "status": "HUMAN VERIFIED",
        "category": new_category,
        "assigned_department": target_department,
    }
