from fastapi import APIRouter, Depends
from backend.app.models.schemas import SettingsUpdate
from backend.app.core.config import settings
from backend.app.db.database import db_adapter
from backend.app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/settings", tags=["System Settings"])

@router.get("")
def get_system_settings(current_user: dict = Depends(get_current_user)):
    confidence_threshold = db_adapter.get_setting("confidence_threshold", settings.DEFAULT_CONFIDENCE_THRESHOLD)
    categories = db_adapter.get_setting("categories", ["SAFETY", "FINANCE", "MAINTENANCE", "OPERATIONS"])
    
    return {
        "confidence_threshold": float(confidence_threshold),
        "categories": categories,
        "supported_languages": ["English", "Hindi", "Mixed (Hindi + English)"],
        "ocr_engine": "Tesseract OCR (eng + hin)"
    }

@router.patch("")
def update_system_settings(payload: SettingsUpdate, current_user: dict = Depends(require_roles(["ADMIN"]))):
    if payload.confidence_threshold is not None:
        db_adapter.set_setting("confidence_threshold", float(payload.confidence_threshold))

    if payload.categories is not None:
        db_adapter.set_setting("categories", payload.categories)

    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "SETTINGS_CHANGED",
        "details": {"confidence_threshold": payload.confidence_threshold}
    })

    return {
        "message": "Settings updated successfully",
        "confidence_threshold": payload.confidence_threshold,
        "categories": payload.categories
    }
