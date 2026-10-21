from fastapi import APIRouter, Depends
from backend.app.models.schemas import SettingsUpdate
from backend.app.core.config import settings
from backend.app.core.categories import CATEGORIES
from backend.app.db.database import db_adapter
from backend.app.api.deps import get_current_user, require_roles
from backend.app.pipeline.classifier import classifier_engine

router = APIRouter(prefix="/settings", tags=["System Settings"])


@router.get("")
def get_system_settings(current_user: dict = Depends(get_current_user)):
    confidence_threshold = db_adapter.get_setting("confidence_threshold", settings.DEFAULT_CONFIDENCE_THRESHOLD)
    return {
        "confidence_threshold": float(confidence_threshold),
        # Categories are fixed by the trained model's label set
        "categories": CATEGORIES,
        "model_name": classifier_engine.model_name,
        "model_loaded": classifier_engine.is_loaded,
        "supported_languages": ["English", "Hindi", "Mixed (Hindi + English)"],
        "ocr_engine": "Tesseract OCR (eng + hin)",
    }


@router.patch("")
def update_system_settings(payload: SettingsUpdate, current_user: dict = Depends(require_roles(["ADMIN"]))):
    if payload.confidence_threshold is not None:
        db_adapter.set_setting("confidence_threshold", float(payload.confidence_threshold))

    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "SETTINGS_CHANGED",
        "details": {"confidence_threshold": payload.confidence_threshold},
    })

    return {
        "message": "Settings updated successfully",
        "confidence_threshold": payload.confidence_threshold,
        "categories": CATEGORIES,
    }
