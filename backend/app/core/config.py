import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "MetroMind — Intelligent Enterprise Document Classification & Routing System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "metromind_super_secret_jwt_key_capstone_2026_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours

    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "metromind")
    SQLITE_FALLBACK_PATH: str = os.getenv("SQLITE_FALLBACK_PATH", "backend/metromind.db")

    DEFAULT_CONFIDENCE_THRESHOLD: float = 70.0

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    PREPROCESSED_DIR: str = os.path.join(BASE_DIR, "uploads", "preprocessed")
    MODEL_PATH: str = os.path.join(BASE_DIR, "ml", "models", "classifier.pkl")
    DATASET_DIR: str = os.path.join(BASE_DIR, "ml", "dataset")
    DEMO_DIR: str = os.path.join(BASE_DIR, "data", "demo_documents")

    class Config:
        case_sensitive = True

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PREPROCESSED_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.MODEL_PATH), exist_ok=True)
os.makedirs(settings.DATASET_DIR, exist_ok=True)
os.makedirs(settings.DEMO_DIR, exist_ok=True)
