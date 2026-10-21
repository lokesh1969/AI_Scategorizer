import os
import warnings
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_PROJECT_DIR = os.path.dirname(_BACKEND_DIR)
_DEV_SECRET = "dev-only-insecure-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(_PROJECT_DIR, ".env"), case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "AI Scategorizer"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = _DEV_SECRET
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "metromind"  # legacy name kept so existing data is not orphaned
    SQLITE_FALLBACK_PATH: str = os.path.join(_BACKEND_DIR, "metromind.db")  # legacy filename kept for existing data

    # Documents below this confidence (%) go to the human verification queue.
    # Choose it with research/evaluate.py (threshold sweep), not by hand.
    DEFAULT_CONFIDENCE_THRESHOLD: float = 70.0

    # Creates the demo accounts listed in PROJECT.md on startup; set False outside demos
    SEED_DEMO_USERS: bool = True

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    BASE_DIR: str = _BACKEND_DIR
    UPLOAD_DIR: str = os.path.join(_BACKEND_DIR, "uploads")
    MODEL_DIR: str = os.path.join(_PROJECT_DIR, "models", "classifier")

    @property
    def PREPROCESSED_DIR(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "preprocessed")

    @property
    def PDF_PAGES_DIR(self) -> str:
        return os.path.join(self.UPLOAD_DIR, "pdf_pages")


settings = Settings()

if settings.SECRET_KEY == _DEV_SECRET:
    warnings.warn("SECRET_KEY is not set; using an insecure development key. Set SECRET_KEY in .env before deploying.")

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PREPROCESSED_DIR, exist_ok=True)
os.makedirs(settings.PDF_PAGES_DIR, exist_ok=True)
