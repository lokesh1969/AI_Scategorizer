from fastapi import APIRouter, Depends
from backend.app.db.database import db_adapter
from backend.app.api.deps import require_roles

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=list)
def get_audit_logs(current_user: dict = Depends(require_roles(["ADMIN"]))):
    logs = db_adapter.get_audit_logs(limit=200)
    return logs
