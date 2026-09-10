from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from backend.app.models.schemas import UserCreate, UserUpdate
from backend.app.core.security import get_password_hash
from backend.app.db.database import db_adapter
from backend.app.api.deps import require_roles

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("", response_model=list)
def get_all_users(current_user: dict = Depends(require_roles(["ADMIN"]))):
    users = db_adapter.get_all_users()
    # Remove password hashes from response
    sanitized = []
    for u in users:
        u_copy = u.copy()
        u_copy.pop("password_hash", None)
        sanitized.append(u_copy)
    return sanitized

@router.post("")
def create_user(payload: UserCreate, current_user: dict = Depends(require_roles(["ADMIN"]))):
    existing = db_adapter.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    hashed_pw = get_password_hash(payload.password)
    user_dict = {
        "email": payload.email,
        "name": payload.name,
        "password_hash": hashed_pw,
        "role": payload.role.value,
        "is_active": True,
        "created_at": datetime.now().isoformat()
    }

    user_id = db_adapter.insert_user(user_dict)

    db_adapter.insert_audit_log({
        "user_email": current_user["email"],
        "action": "USER_CREATED",
        "details": {"created_user_email": payload.email, "role": payload.role.value}
    })

    return {"message": "User created successfully", "user_id": user_id, "email": payload.email}

@router.patch("/{user_id}")
def update_user(user_id: str, payload: UserUpdate, current_user: dict = Depends(require_roles(["ADMIN"]))):
    target_user = db_adapter.get_user_by_id(user_id)
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    updates = {}
    if payload.name is not None:
        updates["name"] = payload.name
    if payload.role is not None:
        updates["role"] = payload.role.value
    if payload.is_active is not None:
        updates["is_active"] = payload.is_active

    if updates:
        db_adapter.update_user(user_id, updates)
        db_adapter.insert_audit_log({
            "user_email": current_user["email"],
            "action": "ROLE_CHANGED" if "role" in updates else "USER_UPDATED",
            "details": {"updated_user": target_user["email"], "updates": updates}
        })

    return {"message": "User updated successfully", "user_id": user_id}
