from fastapi import APIRouter, HTTPException, Request, status, Depends
from backend.app.models.schemas import UserLogin, TokenResponse
from backend.app.core.security import verify_password, create_access_token
from backend.app.db.database import db_adapter
from backend.app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, request: Request):
    user = db_adapter.get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated")

    token = create_access_token(subject=user["_id"], role=user["role"])

    # Audit log
    db_adapter.insert_audit_log({
        "user_email": user["email"],
        "action": "LOGIN",
        "details": {"role": user["role"], "ip": request.client.host if request.client else None}
    })

    user_data = {
        "id": user["_id"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"]
    }

    return {"access_token": token, "token_type": "bearer", "user": user_data}

@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["_id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "role": current_user["role"],
        "is_active": current_user.get("is_active", True)
    }
