import os
from datetime import datetime
from backend.app.core.security import get_password_hash
from backend.app.db.database import db_adapter
from backend.app.core.config import settings

DEMO_USERS = [
    {
        "_id": "user_admin_001",
        "email": "admin@metromind.local",
        "name": "System Administrator",
        "password_hash": get_password_hash("admin123"),
        "role": "ADMIN",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_station_002",
        "email": "station@metromind.local",
        "name": "Station Controller (Rajesh Kumar)",
        "password_hash": get_password_hash("station123"),
        "role": "STATION_CONTROLLER",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_finance_003",
        "email": "finance@metromind.local",
        "name": "Finance Manager (Priya Sharma)",
        "password_hash": get_password_hash("finance123"),
        "role": "FINANCE_MANAGER",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_maint_004",
        "email": "maintenance@metromind.local",
        "name": "Maintenance Head (Amit Verma)",
        "password_hash": get_password_hash("maint123"),
        "role": "MAINTENANCE_HEAD",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_upload_005",
        "email": "uploader@metromind.local",
        "name": "Document Uploader (Sunil Patel)",
        "password_hash": get_password_hash("user123"),
        "role": "UPLOADER",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
]

DEMO_DOCUMENTS = [
    {
        "_id": "demo_doc_001",
        "original_filename": "Emergency_Fire_Hazard_Notice_Platform2.txt",
        "file_type": "TXT",
        "file_path": "uploads/demo_doc_001.txt",
        "uploader_id": "user_upload_005",
        "uploader_name": "Document Uploader (Sunil Patel)",
        "upload_timestamp": datetime.now().isoformat(),
        "extracted_text": "EMERGENCY SAFETY INCIDENT REPORT\nStation: Central Metro Station\nPlatform Number: Platform 2\nDate: 10 September 2026\nReported By: Safety Officer Officer Sharma (Phone: +91 9876543210)\n\nEmergency fire alarm detected near electrical control room at platform 2. Smoke rising near power transformer. Fire squad immediately notified. Station evacuation initiated for passenger safety.",
        "language": "English",
        "ocr_metadata": {"ocr_used": False, "language": "N/A", "preprocessing_applied": [], "preprocessed_image_url": None},
        "classification": {
            "predicted_category": "SAFETY",
            "confidence": 94.7,
            "probabilities": {"SAFETY": 94.7, "OPERATIONS": 3.1, "MAINTENANCE": 1.5, "FINANCE": 0.7}
        },
        "priority": {
            "level": "CRITICAL",
            "score": 96,
            "reason": "Safety-related emergency incident detected. Found emergency terms: 'fire', 'emergency', 'evacuation'."
        },
        "summary": "• Emergency fire alarm detected near electrical control room at platform 2.\n• Smoke rising near power transformer; fire squad notified.\n• Station evacuation initiated for passenger safety.",
        "sentiment": {"label": "NEGATIVE", "score": 0.92},
        "entities": [
            {"text": "Central Metro Station", "label": "STATION"},
            {"text": "Platform 2", "label": "STATION"},
            {"text": "10 September 2026", "label": "DATE"},
            {"text": "+91 9876543210", "label": "PHONE"}
        ],
        "assigned_department": "Station Controller",
        "verification_status": "AI VERIFIED",
        "verified_category": None,
        "verifier_id": None,
        "verifier_name": None,
        "verification_notes": None,
        "verification_timestamp": None,
        "processing_status": "COMPLETED"
    },
    {
        "_id": "demo_doc_002",
        "original_filename": "Hindi_Platform_Incident_Report.txt",
        "file_type": "TXT",
        "file_path": "uploads/demo_doc_002.txt",
        "uploader_id": "user_upload_005",
        "uploader_name": "Document Uploader (Sunil Patel)",
        "upload_timestamp": datetime.now().isoformat(),
        "extracted_text": "आपातकालीन सुरक्षा रिपोर्ट\nस्टेशन: मुंबई सेंट्रल मेट्रो स्टेशन\nदिनांक: 10 सितम्बर 2026\nरसीद संख्या: INC-8820\n\nप्लेटफॉर्म नंबर 2 पर आपातकालीन स्थिति उत्पन्न हुई। ट्रेन संख्या 104 के डिब्बे से धुआं निकलता देखा गया। यात्रियों की सुरक्षा हेतु प्लेटफॉर्म खाली कराया गया। त्वरित दुर्घटना जांच टीम एवं सुरक्षा अधिकारी को सूचित किया गया।",
        "language": "Hindi",
        "ocr_metadata": {"ocr_used": False, "language": "N/A", "preprocessing_applied": [], "preprocessed_image_url": None},
        "classification": {
            "predicted_category": "SAFETY",
            "confidence": 92.3,
            "probabilities": {"SAFETY": 92.3, "OPERATIONS": 4.5, "MAINTENANCE": 2.1, "FINANCE": 1.1}
        },
        "priority": {
            "level": "CRITICAL",
            "score": 94,
            "reason": "Safety-related emergency incident detected. Found emergency terms: 'आपातकालीन', 'धुआं', 'सुरक्षा'."
        },
        "summary": "• प्लेटफॉर्म नंबर 2 पर आपातकालीन स्थिति उत्पन्न हुई।\n• ट्रेन संख्या 104 से धुआं निकलने पर प्लेटफॉर्म खाली कराया गया।\n• त्वरित दुर्घटना जांच टीम एवं सुरक्षा अधिकारी को सूचित किया गया।",
        "sentiment": {"label": "NEGATIVE", "score": 0.88},
        "entities": [
            {"text": "प्लेटफॉर्म नंबर 2", "label": "STATION"},
            {"text": "10 सितम्बर 2026", "label": "DATE"},
            {"text": "INC-8820", "label": "DOCUMENT_NUMBER"}
        ],
        "assigned_department": "Station Controller",
        "verification_status": "AI VERIFIED",
        "verified_category": None,
        "verifier_id": None,
        "verifier_name": None,
        "verification_notes": None,
        "verification_timestamp": None,
        "processing_status": "COMPLETED"
    },
    {
        "_id": "demo_doc_003",
        "original_filename": "Invoice_Equipment_Clearance_Q3.txt",
        "file_type": "TXT",
        "file_path": "uploads/demo_doc_003.txt",
        "uploader_id": "user_upload_005",
        "uploader_name": "Document Uploader (Sunil Patel)",
        "upload_timestamp": datetime.now().isoformat(),
        "extracted_text": "INVOICE AND VENDOR CLEARANCE STATEMENT\nInvoice Number: INV-2026-4029\nDate: 05 September 2026\nVendor: Metro Infra Supplies Ltd.\nTotal Amount: ₹4,50,000\n\nPurchase order clearance for electrical transformer spare parts and station lighting equipment. Payment requested via bank wire transfer to Account #9910283741.",
        "language": "English",
        "ocr_metadata": {"ocr_used": False, "language": "N/A", "preprocessing_applied": [], "preprocessed_image_url": None},
        "classification": {
            "predicted_category": "FINANCE",
            "confidence": 95.8,
            "probabilities": {"FINANCE": 95.8, "OPERATIONS": 2.2, "MAINTENANCE": 1.2, "SAFETY": 0.8}
        },
        "priority": {
            "level": "MEDIUM",
            "score": 55,
            "reason": "Standard medium priority operational/financial document."
        },
        "summary": "• Invoice INV-2026-4029 issued by Metro Infra Supplies Ltd.\n• Total clearance amount ₹4,50,000 for electrical transformer spare parts.\n• Payment requested via bank wire transfer.",
        "sentiment": {"label": "NEUTRAL", "score": 0.80},
        "entities": [
            {"text": "₹4,50,000", "label": "MONEY"},
            {"text": "05 September 2026", "label": "DATE"},
            {"text": "INV-2026-4029", "label": "DOCUMENT_NUMBER"}
        ],
        "assigned_department": "Finance Manager",
        "verification_status": "AI VERIFIED",
        "verified_category": None,
        "verifier_id": None,
        "verifier_name": None,
        "verification_notes": None,
        "verification_timestamp": None,
        "processing_status": "COMPLETED"
    },
    {
        "_id": "demo_doc_004",
        "original_filename": "Mixed_Maintenance_Fault_Log.txt",
        "file_type": "TXT",
        "file_path": "uploads/demo_doc_004.txt",
        "uploader_id": "user_upload_005",
        "uploader_name": "Document Uploader (Sunil Patel)",
        "upload_timestamp": datetime.now().isoformat(),
        "extracted_text": "TECHNICAL MAINTENANCE FAULT REPORT\nStation: Central Line Platform 3\nDate: 08 September 2026\n\nPlatform 3 पर maintenance work urgently required machinery defect detected. एस्केलेटर मोटर नंबर 4 में खराबी के कारण परिचालन बंद है। Spare part replacement and mechanical inspection required immediately.",
        "language": "Mixed (Hindi + English)",
        "ocr_metadata": {"ocr_used": False, "language": "N/A", "preprocessing_applied": [], "preprocessed_image_url": None},
        "classification": {
            "predicted_category": "MAINTENANCE",
            "confidence": 89.4,
            "probabilities": {"MAINTENANCE": 89.4, "OPERATIONS": 6.1, "SAFETY": 3.2, "FINANCE": 1.3}
        },
        "priority": {
            "level": "HIGH",
            "score": 78,
            "reason": "High priority operational/equipment disruption detected. Found terms: 'maintenance', 'defect', 'खराबी'."
        },
        "summary": "• Platform 3 maintenance work urgently required due to machinery defect.\n• एस्केलेटर मोटर नंबर 4 में खराबी के कारण परिचालन बंद है।\n• Spare part replacement and mechanical inspection required.",
        "sentiment": {"label": "NEGATIVE", "score": 0.75},
        "entities": [
            {"text": "Platform 3", "label": "STATION"},
            {"text": "08 September 2026", "label": "DATE"},
            {"text": "escalator", "label": "EQUIPMENT"}
        ],
        "assigned_department": "Maintenance Head",
        "verification_status": "AI VERIFIED",
        "verified_category": None,
        "verifier_id": None,
        "verifier_name": None,
        "verification_notes": None,
        "verification_timestamp": None,
        "processing_status": "COMPLETED"
    },
    {
        "_id": "demo_doc_005",
        "original_filename": "Ambiguous_Multi_Topic_Notice.txt",
        "file_type": "TXT",
        "file_path": "uploads/demo_doc_005.txt",
        "uploader_id": "user_upload_005",
        "uploader_name": "Document Uploader (Sunil Patel)",
        "upload_timestamp": datetime.now().isoformat(),
        "extracted_text": "GENERAL ADMINISTRATIVE & MAINTENANCE MEMO\nDate: 09 September 2026\n\nRoutine update regarding administrative operational shift timings, ticket sales audit guidelines, general station cleanliness, and minor platform seating repair request. All supervisors are advised to review attached schedule.",
        "language": "English",
        "ocr_metadata": {"ocr_used": False, "language": "N/A", "preprocessing_applied": [], "preprocessed_image_url": None},
        "classification": {
            "predicted_category": "OPERATIONS",
            "confidence": 61.4,
            "probabilities": {"OPERATIONS": 61.4, "MAINTENANCE": 22.1, "FINANCE": 11.5, "SAFETY": 5.0}
        },
        "priority": {
            "level": "LOW",
            "score": 35,
            "reason": "Routine low priority administrative document."
        },
        "summary": "• General administrative & maintenance memo dated 09 September 2026.\n• Covers shift timings, ticket sales audit, and seating repairs.\n• Supervisors advised to review schedule.",
        "sentiment": {"label": "NEUTRAL", "score": 0.85},
        "entities": [
            {"text": "09 September 2026", "label": "DATE"}
        ],
        "assigned_department": "Human Verification Queue",
        "verification_status": "HUMAN VERIFICATION REQUIRED",
        "verified_category": None,
        "verifier_id": None,
        "verifier_name": None,
        "verification_notes": None,
        "verification_timestamp": None,
        "processing_status": "COMPLETED"
    }
]

def seed_demo_data():
    # 1. Seed Demo Users
    for u in DEMO_USERS:
        existing = db_adapter.get_user_by_email(u["email"])
        if not existing:
            db_adapter.insert_user(u)
            print(f"[Seed] Created demo user: {u['email']} ({u['role']})")

    # 2. Seed Demo Documents
    for d in DEMO_DOCUMENTS:
        existing = db_adapter.get_document_by_id(d["_id"])
        if not existing:
            # Create physical file in uploads
            os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
            with open(os.path.join(settings.BASE_DIR, d["file_path"]), "w", encoding="utf-8") as f:
                f.write(d["extracted_text"])
            db_adapter.insert_document(d)
            print(f"[Seed] Created demo document: {d['original_filename']} ({d['classification']['predicted_category']} - {d['verification_status']})")

    # 3. Seed Default Settings
    if not db_adapter.get_setting("confidence_threshold"):
        db_adapter.set_setting("confidence_threshold", 70.0)

if __name__ == "__main__":
    seed_demo_data()
