import os
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends, Query
from fastapi.responses import FileResponse

from backend.app.core.config import settings
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

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    file_bytes = await file.read()
    filename = file.filename

    # 1. Ingestion & Validation
    is_valid, error_msg, file_info = validate_and_ingest_file(filename, file_bytes)
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    doc_id = str(uuid.uuid4())
    save_filename = f"{doc_id}_{filename}"
    file_save_path = os.path.join(settings.UPLOAD_DIR, save_filename)

    with open(file_save_path, "wb") as f:
        f.write(file_bytes)

    # 2. Text Extraction
    raw_text, is_ocr_needed, ext_metadata = extract_text_from_file(file_save_path, file_info)
    ocr_metadata = {
        "ocr_used": False,
        "language": "N/A",
        "preprocessing_applied": [],
        "preprocessed_image_url": None
    }

    # 3. OCR Engine (if scanned image or scanned PDF)
    if is_ocr_needed:
        ocr_text, ocr_meta = run_ocr_on_file(file_save_path, file_info, doc_id)
        extracted_text = ocr_text
        ocr_metadata = ocr_meta
    else:
        extracted_text = raw_text

    # 4. Text Cleaning & Normalization
    cleaned_text = clean_and_normalize_text(extracted_text)

    # 5. Language Detection
    lang = detect_language(cleaned_text)

    # 6. AI Classification & Confidence Calculation
    predicted_category, confidence, probability_dist = classifier_engine.predict(cleaned_text)

    # 7. Urgency / Priority Engine
    priority_level, priority_score, priority_reason = calculate_priority(predicted_category, cleaned_text)

    # 8. AI Summarizer
    summary_text = generate_summary(cleaned_text)

    # 9. NER Entity Extraction
    entities = extract_entities(cleaned_text)

    # 10. Sentiment Analysis
    sentiment = analyze_sentiment(cleaned_text)

    # 11. Intelligent Routing & Confidence Threshold Check
    conf_threshold = db_adapter.get_setting("confidence_threshold", settings.DEFAULT_CONFIDENCE_THRESHOLD)
    assigned_dept, verification_status = route_document(predicted_category, confidence, float(conf_threshold))

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
            "predicted_category": predicted_category,
            "confidence": confidence,
            "probabilities": probability_dist
        },
        "priority": {
            "level": priority_level,
            "score": priority_score,
            "reason": priority_reason
        },
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
        "processing_status": "COMPLETED"
    }

    db_adapter.insert_document(doc_record)

    # Audit log
    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "UPLOAD",
        "document_id": doc_id,
        "details": {
            "filename": filename,
            "category": predicted_category,
            "confidence": confidence,
            "status": verification_status
        }
    })

    return doc_record

@router.get("", response_model=List[dict])
def get_documents(
    search: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Returns list of documents with backend RBAC enforcement:
    - UPLOADER: only uploaded by self
    - STATION_CONTROLLER: Safety & Operations
    - FINANCE_MANAGER: Finance
    - MAINTENANCE_HEAD: Maintenance
    - ADMIN: All documents
    """
    query = {}
    role = current_user["role"]

    if role == "UPLOADER":
        query["uploader_id"] = current_user["_id"]
    elif role == "STATION_CONTROLLER":
        # Can view Safety & Operations, or documents needing verification
        pass
    elif role == "FINANCE_MANAGER":
        pass
    elif role == "MAINTENANCE_HEAD":
        pass

    docs = db_adapter.get_documents(query)

    # Filter by role domain if not admin
    if role == "STATION_CONTROLLER":
        docs = [d for d in docs if d.get("classification", {}).get("predicted_category") in ["SAFETY", "OPERATIONS"] or d.get("verification_status") == "HUMAN VERIFICATION REQUIRED"]
    elif role == "FINANCE_MANAGER":
        docs = [d for d in docs if d.get("classification", {}).get("predicted_category") == "FINANCE" or d.get("verification_status") == "HUMAN VERIFICATION REQUIRED"]
    elif role == "MAINTENANCE_HEAD":
        docs = [d for d in docs if d.get("classification", {}).get("predicted_category") == "MAINTENANCE" or d.get("verification_status") == "HUMAN VERIFICATION REQUIRED"]

    # Filter parameters
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

    role = current_user["role"]
    if role == "UPLOADER" and doc.get("uploader_id") != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this document")

    # Record audit log
    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "DOCUMENT_VIEWED",
        "document_id": doc_id,
        "details": {"filename": doc.get("original_filename")}
    })

    return doc

@router.delete("/{doc_id}")
def delete_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    doc = db_adapter.get_document_by_id(doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    role = current_user["role"]
    if role != "ADMIN" and doc.get("uploader_id") != current_user["_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this document")

    db_adapter.delete_document(doc_id)

    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "DOCUMENT_DELETED",
        "document_id": doc_id,
        "details": {"filename": doc.get("original_filename")}
    })

    return {"message": "Document deleted successfully", "doc_id": doc_id}

@router.get("/preprocessed-image/{filename}")
def serve_preprocessed_image(filename: str):
    image_path = os.path.join(settings.PREPROCESSED_DIR, filename)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    return FileResponse(image_path)
