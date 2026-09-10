from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    STATION_CONTROLLER = "STATION_CONTROLLER"
    FINANCE_MANAGER = "FINANCE_MANAGER"
    MAINTENANCE_HEAD = "MAINTENANCE_HEAD"
    UPLOADER = "UPLOADER"

class DocumentCategory(str, Enum):
    SAFETY = "SAFETY"
    FINANCE = "FINANCE"
    MAINTENANCE = "MAINTENANCE"
    OPERATIONS = "OPERATIONS"

class PriorityLevel(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class VerificationStatus(str, Enum):
    AI_VERIFIED = "AI VERIFIED"
    HUMAN_VERIFICATION_REQUIRED = "HUMAN VERIFICATION REQUIRED"
    HUMAN_VERIFIED = "HUMAN VERIFIED"

# Auth Schemas
class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: UserRole

class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: str = Field(alias="_id")
    email: str
    name: str
    role: UserRole
    is_active: bool = True
    created_at: str

    class Config:
        populate_by_name = True

# Classification & Analytics Schemas
class ClassificationResult(BaseModel):
    predicted_category: str
    confidence: float
    probabilities: Dict[str, float]

class PriorityResult(BaseModel):
    level: PriorityLevel
    score: int
    reason: str

class SentimentResult(BaseModel):
    label: str # POSITIVE, NEUTRAL, NEGATIVE
    score: float

class EntityItem(BaseModel):
    text: str
    label: str

class OCRMetadata(BaseModel):
    ocr_used: bool
    language: str
    preprocessing_applied: List[str]
    confidence: Optional[float] = None
    preprocessed_image_url: Optional[str] = None

# Verification Schema
class VerificationInput(BaseModel):
    verified_category: str
    notes: Optional[str] = ""

# Document Schema
class DocumentResponse(BaseModel):
    id: str = Field(alias="_id")
    original_filename: str
    file_type: str
    file_path: str
    uploader_id: str
    uploader_name: str
    upload_timestamp: str
    extracted_text: str
    language: str
    ocr_metadata: OCRMetadata
    classification: ClassificationResult
    priority: PriorityResult
    summary: str
    sentiment: SentimentResult
    entities: List[EntityItem]
    assigned_department: str
    verification_status: VerificationStatus
    verified_category: Optional[str] = None
    verifier_id: Optional[str] = None
    verifier_name: Optional[str] = None
    verification_notes: Optional[str] = None
    verification_timestamp: Optional[str] = None
    processing_status: str = "COMPLETED"

    class Config:
        populate_by_name = True

# Dashboard & Audit Schemas
class DashboardStats(BaseModel):
    total_documents: int
    processed_documents: int
    pending_documents: int
    human_verification_count: int
    priority_counts: Dict[str, int]
    category_counts: Dict[str, int]
    language_counts: Dict[str, int]
    average_confidence: float
    human_verification_rate: float

class AuditLogItem(BaseModel):
    id: str = Field(alias="_id")
    user_email: str
    action: str
    document_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: str

    class Config:
        populate_by_name = True

class SettingsUpdate(BaseModel):
    confidence_threshold: float
    categories: Optional[List[str]] = None
