import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from scripts.seed_db import seed_demo_data

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    seed_demo_data()

def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ONLINE"

def test_user_login():
    response = client.post("/api/auth/login", json={
        "email": "admin@metromind.local",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"

def test_rbac_unauthorized_access():
    # Attempt to access admin users list without token
    response = client.get("/api/users")
    assert response.status_code == 401

def test_dashboard_stats():
    login_res = client.post("/api/auth/login", json={"email": "admin@metromind.local", "password": "admin123"})
    token = login_res.json()["access_token"]

    response = client.get("/api/dashboard/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert data["total_documents"] >= 5

def test_document_upload_and_verification():
    login_res = client.post("/api/auth/login", json={"email": "uploader@metromind.local", "password": "user123"})
    token = login_res.json()["access_token"]

    # Upload test txt file
    file_content = b"Emergency fire hazard detected at Platform 2. Evacuate station area immediately."
    files = {"file": ("test_fire_notice.txt", file_content, "text/plain")}

    upload_res = client.post("/api/documents/upload", headers={"Authorization": f"Bearer {token}"}, files=files)
    assert upload_res.status_code == 200
    doc_data = upload_res.json()
    assert doc_data["classification"]["predicted_category"] == "SAFETY"
    assert doc_data["priority"]["level"] == "CRITICAL"

    doc_id = doc_data["_id"]

    # Perform Human Verification with Station Controller
    st_login = client.post("/api/auth/login", json={"email": "station@metromind.local", "password": "station123"})
    st_token = st_login.json()["access_token"]

    verify_res = client.post(
        f"/api/verification/verify/{doc_id}",
        headers={"Authorization": f"Bearer {st_token}"},
        json={"verified_category": "SAFETY", "notes": "Verified by Station Controller"}
    )
    assert verify_res.status_code == 200
    assert verify_res.json()["status"] == "HUMAN VERIFIED"
