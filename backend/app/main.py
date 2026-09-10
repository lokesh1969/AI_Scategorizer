import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.auth import router as auth_router
from backend.app.api.documents import router as documents_router
from backend.app.api.verification import router as verification_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.users import router as users_router
from backend.app.api.audit import router as audit_router
from backend.app.api.settings import router as settings_router
from scripts.seed_db import seed_demo_data

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all local origins during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(verification_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(settings_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
def startup_event():
    print(f"[MetroMind] Starting MetroMind Enterprise API Service...")
    seed_demo_data()

@app.get("/")
def root():
    return {
        "title": "MetroMind — Intelligent Enterprise Document Classification & Routing System",
        "status": "ONLINE",
        "version": "1.0.0",
        "docs": "/api/docs"
    }
