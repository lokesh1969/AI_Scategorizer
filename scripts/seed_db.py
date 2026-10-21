import os
from datetime import datetime
from backend.app.core.security import get_password_hash
from backend.app.db.database import db_adapter
from backend.app.core.config import settings

DEMO_USERS = [
    {
        "_id": "user_admin_001",
        "email": "admin@aiscategorizer.local",
        "name": "System Administrator",
        "password_hash": get_password_hash("admin123"),
        "role": "ADMIN",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_hr_002",
        "email": "hr@aiscategorizer.local",
        "name": "HR Manager (Anita Desai)",
        "password_hash": get_password_hash("hr123"),
        "role": "HR_MANAGER",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_finance_003",
        "email": "finance@aiscategorizer.local",
        "name": "Finance Manager (Priya Sharma)",
        "password_hash": get_password_hash("finance123"),
        "role": "FINANCE_MANAGER",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_legal_004",
        "email": "legal@aiscategorizer.local",
        "name": "Legal Counsel (Ravi Iyer)",
        "password_hash": get_password_hash("legal123"),
        "role": "LEGAL_COUNSEL",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_ops_006",
        "email": "operations@aiscategorizer.local",
        "name": "Operations Manager (Karan Singh)",
        "password_hash": get_password_hash("ops123"),
        "role": "OPERATIONS_MANAGER",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    },
    {
        "_id": "user_upload_005",
        "email": "uploader@aiscategorizer.local",
        "name": "Document Uploader (Sunil Patel)",
        "password_hash": get_password_hash("user123"),
        "role": "UPLOADER",
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }
]

DEMO_DOCUMENTS = []

def seed_demo_data():
    # 1. Seed Demo Users
    for u in (DEMO_USERS if settings.SEED_DEMO_USERS else []):
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
    if db_adapter.get_setting("confidence_threshold") is None:
        db_adapter.set_setting("confidence_threshold", settings.DEFAULT_CONFIDENCE_THRESHOLD)

if __name__ == "__main__":
    seed_demo_data()
