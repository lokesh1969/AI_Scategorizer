import os
import re
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.core.categories import can_view_document
from backend.app.db.database import db_adapter
from backend.app.api.deps import get_current_user
from backend.app.pipeline.ingestion import validate_and_ingest_file
from backend.app.pipeline.extraction import extract_text_from_file
from backend.app.pipeline.ocr import run_ocr_on_file
from backend.app.pipeline.language import detect_language
from backend.app.pipeline.cleaner import clean_and_normalize_text
from backend.app.pipeline.classifier import classifier_engine
from backend.app.pipeline.priority import calculate_priority
from backend.app.pipeline.summarizer import generate_summary
from backend.app.pipeline.ner import extract_entities
from backend.app.pipeline.sentiment import analyze_sentiment
from backend.app.pipeline.routing import route_document

router = APIRouter(prefix="/documents", tags=["Documents"])


def safe_filename(name: str) -> str:
    """Drops any directory part (both / and \\) and characters that are unsafe on disk."""
    base = re.split(r"[\\/]", name or "")[-1]
    base = re.sub(r"[^\w.\- ()ऀ-ॿ]", "_", base).strip(" .")
    return base[:150] or "document"


def _within(directory: str, path: str) -> bool:
    directory = os.path.realpath(directory)
    return os.path.commonpath([directory, os.path.realpath(path)]) == directory


# Plain `def` (not `async def`): OCR and model inference are blocking, so FastAPI
# runs this in its thread pool and other requests keep being served.
@router.post("/upload")
def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    file_bytes = file.file.read()
    filename = safe_filename(file.filename)

    # 1. Ingestion & Validation
    is_valid, error_msg, file_info = validate_and_ingest_file(filename, file_bytes)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    doc_id = str(uuid.uuid4())
    file_save_path = os.path.join(settings.UPLOAD_DIR, f"{doc_id}_{filename}")
    with open(file_save_path, "wb") as f:
        f.write(file_bytes)

    # 2. Text Extraction
    raw_text, is_ocr_needed, _ = extract_text_from_file(file_save_path, file_info)
    ocr_metadata = {"ocr_used": False, "language": "N/A", "preprocessing_applied": [], "preprocessed_image_url": None}

    # 3. OCR Engine (scanned image or scanned PDF)
    if is_ocr_needed:
        extracted_text, ocr_metadata = run_ocr_on_file(file_save_path, file_info, doc_id)
    else:
        extracted_text = raw_text

    # 4-5. Cleaning & Language Detection
    cleaned_text = clean_and_normalize_text(extracted_text)
    lang = detect_language(cleaned_text)

    # 6. Classification (blank/unreadable text returns UNCLASSIFIED with 0% confidence)
    predicted_category, confidence, probability_dist = classifier_engine.predict(cleaned_text)

    # 7-10. Priority, Summary, Entities, Sentiment
    priority_level, priority_score, priority_reason = calculate_priority(predicted_category, cleaned_text)
    summary_text = generate_summary(cleaned_text)
    entities = extract_entities(cleaned_text)
    sentiment = analyze_sentiment(cleaned_text)

    # 11. Routing against the confidence threshold
    conf_threshold = float(db_adapter.get_setting("confidence_threshold", settings.DEFAULT_CONFIDENCE_THRESHOLD))
    assigned_dept, verification_status = route_document(predicted_category, confidence, conf_threshold)

    doc_record = {
        "_id": doc_id,
        "original_filename": filename,
        "file_type": file_info["extension"].upper(),
        "file_path": file_save_path,
        "uploader_id": current_user["_id"],
        "uploader_name": current_user["name"],
        "upload_timestamp": datetime.now().isoformat(),
        "extracted_text": cleaned_text,
        "language": lang,
        "ocr_metadata": ocr_metadata,
        "classification": {
            # predicted_category is the *current* category (updated by human review);
            # model_* fields are the original model output and are never overwritten,
            # so model accuracy can be measured later (research/export_feedback.py).
            "predicted_category": predicted_category,
            "confidence": confidence,
            "probabilities": probability_dist,
            "model_prediction": predicted_category,
            "model_confidence": confidence,
            "model_name": classifier_engine.model_name,
            "threshold_used": conf_threshold,
        },
        "priority": {"level": priority_level, "score": priority_score, "reason": priority_reason},
        "summary": summary_text,
        "sentiment": sentiment,
        "entities": entities,
        "assigned_department": assigned_dept,
        "verification_status": verification_status,
        "verified_category": None,
        "verifier_id": None,
        "verifier_name": None,
        "verification_notes": None,
        "verification_timestamp": None,
        "processing_status": "COMPLETED",
    }

    db_adapter.insert_document(doc_record)
    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "UPLOAD",
        "document_id": doc_id,
        "details": {
            "filename": filename,
            "category": predicted_category,
            "confidence": confidence,
            "status": verification_status,
        },
    })
    return doc_record


@router.get("", response_model=List[dict])
def get_documents(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Lists documents with backend RBAC (see core/categories.can_view_document):
    - ADMIN: all documents
    - Department roles: their categories + the human verification queue + own uploads
    - UPLOADER: own uploads only
    """
    query = {"uploader_id": current_user["_id"]} if current_user["role"] == "UPLOADER" else {}
    docs = [d for d in db_adapter.get_documents(query) if can_view_document(current_user, d)]

    if category:
        docs = [d for d in docs if d.get("classification", {}).get("predicted_category") == category]
    if priority:
        docs = [d for d in docs if d.get("priority", {}).get("level") == priority]
    if status_filter:
        docs = [d for d in docs if d.get("verification_status") == status_filter]
    if language:
        docs = [d for d in docs if d.get("language") == language]
    if search:
        s_lower = search.lower()
        docs = [d for d in docs if s_lower in d.get("original_filename", "").lower() or s_lower in d.get("extracted_text", "").lower()]

    return docs


@router.get("/{doc_id}")
def get_document_by_id(doc_id: str, current_user: dict = Depends(get_current_user)):
    doc = db_adapter.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if not can_view_document(current_user, doc):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "DOCUMENT_VIEWED",
        "document_id": doc_id,
        "details": {"filename": doc.get("original_filename")},
    })
    return doc


@router.delete("/{doc_id}")
def delete_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    doc = db_adapter.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if current_user["role"] != "ADMIN" and doc.get("uploader_id") != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this document")

    db_adapter.delete_document(doc_id)

    # Remove the stored upload and its OCR artifacts
    artifacts = [doc.get("file_path", "")]
    for folder in (settings.PDF_PAGES_DIR, settings.PREPROCESSED_DIR):
        artifacts += [os.path.join(folder, n) for n in os.listdir(folder) if doc_id in n]
    for path in artifacts:
        if path and _within(settings.UPLOAD_DIR, path) and os.path.isfile(path):
            os.remove(path)

    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "DOCUMENT_DELETED",
        "document_id": doc_id,
        "details": {"filename": doc.get("original_filename")},
    })
    return {"message": "Document deleted successfully", "doc_id": doc_id}


@router.get("/preprocessed-image/{filename}")
def serve_preprocessed_image(filename: str):
    # Served without a token because <img> tags cannot send one; names contain a
    # random UUID. The path must stay inside PREPROCESSED_DIR (blocks ..\ traversal).
    image_path = os.path.join(settings.PREPROCESSED_DIR, filename)
    if not re.fullmatch(r"preprocessed_[\w\-]+\.png", filename) or not _within(settings.PREPROCESSED_DIR, image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    if not os.path.isfile(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(image_path)
