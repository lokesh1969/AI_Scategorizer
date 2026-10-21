import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.pipeline.classifier import classifier_engine
from scripts.seed_db import seed_demo_data

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    seed_demo_data()


def _token(email, password):
    res = client.post("/api/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


ADMIN = ("admin@aiscategorizer.local", "admin123")
UPLOADER = ("uploader@aiscategorizer.local", "user123")
LEGAL = ("legal@aiscategorizer.local", "legal123")
HR = ("hr@aiscategorizer.local", "hr123")
FINANCE = ("finance@aiscategorizer.local", "finance123")


def _upload(monkeypatch, text, category, confidence, name="doc.txt"):
    """Uploads a .txt file with the classifier stubbed to a fixed prediction."""
    probs = {c: 0.0 for c in ["FINANCE", "HR", "LEGAL", "OPERATIONS"]}
    probs[category] = confidence
    monkeypatch.setattr(classifier_engine, "predict", lambda _text: (category, confidence, probs))
    res = client.post("/api/documents/upload", headers=_token(*UPLOADER),
                      files={"file": (name, text.encode(), "text/plain")})
    assert res.status_code == 200, res.text
    return res.json()


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ONLINE"


def test_user_login():
    res = client.post("/api/auth/login", json={"email": ADMIN[0], "password": ADMIN[1]})
    assert res.status_code == 200
    assert res.json()["user"]["role"] == "ADMIN"


def test_rbac_unauthorized_access():
    assert client.get("/api/users").status_code == 401


def test_high_confidence_is_auto_routed(monkeypatch):
    doc = _upload(monkeypatch, "Please review the attached non-disclosure agreement before signing.", "LEGAL", 92.0)
    assert doc["verification_status"] == "AI VERIFIED"
    assert doc["assigned_department"] == "Legal Counsel"
    assert doc["classification"]["model_prediction"] == "LEGAL"


def test_department_rbac(monkeypatch):
    doc = _upload(monkeypatch, "Signed vendor contract with indemnity clause for review by counsel.", "LEGAL", 95.0)
    assert client.get(f"/api/documents/{doc['_id']}", headers=_token(*LEGAL)).status_code == 200
    assert client.get(f"/api/documents/{doc['_id']}", headers=_token(*HR)).status_code == 403
    hr_ids = [d["_id"] for d in client.get("/api/documents", headers=_token(*HR)).json()]
    assert doc["_id"] not in hr_ids


def test_low_confidence_human_verification_keeps_model_prediction(monkeypatch):
    doc = _upload(monkeypatch, "Employee raised a grievance about the revised leave policy and overtime pay.", "FINANCE", 41.0)
    assert doc["verification_status"] == "HUMAN VERIFICATION REQUIRED"

    # Every department reviewer can see and verify the queue (HR here, not just Finance)
    queue = client.get("/api/verification", headers=_token(*HR)).json()
    assert doc["_id"] in [d["_id"] for d in queue]

    res = client.post(f"/api/verification/verify/{doc['_id']}", headers=_token(*HR),
                      json={"verified_category": "HR", "notes": "Leave policy grievance"})
    assert res.status_code == 200
    assert res.json()["assigned_department"] == "HR Manager"

    stored = client.get(f"/api/documents/{doc['_id']}", headers=_token(*ADMIN)).json()
    assert stored["classification"]["predicted_category"] == "HR"
    assert stored["classification"]["model_prediction"] == "FINANCE"
    assert stored["human_override"] is True

    # A routed document cannot be re-labelled by a department reviewer
    again = client.post(f"/api/verification/verify/{doc['_id']}", headers=_token(*FINANCE),
                        json={"verified_category": "FINANCE"})
    assert again.status_code == 409


def test_empty_document_goes_to_human_queue():
    res = client.post("/api/documents/upload", headers=_token(*UPLOADER),
                      files={"file": ("blank.txt", b"   \n  .  ", "text/plain")})
    assert res.status_code == 200
    assert res.json()["verification_status"] == "HUMAN VERIFICATION REQUIRED"


def test_upload_filename_cannot_escape_upload_dir(monkeypatch):
    doc = _upload(monkeypatch, "Quarterly budget variance report for the finance committee.", "FINANCE", 90.0,
                  name="..\\..\\evil.txt")
    assert doc["original_filename"] == "evil.txt"


def test_preprocessed_image_rejects_traversal():
    assert client.get("/api/documents/preprocessed-image/..%5C..%5Cmetromind.db").status_code == 404
    assert client.get("/api/documents/preprocessed-image/test.db").status_code == 404


def test_settings_threshold_is_validated():
    headers = _token(*ADMIN)
    assert client.patch("/api/settings", headers=headers, json={"confidence_threshold": 150}).status_code == 422
    assert client.patch("/api/settings", headers=headers, json={"confidence_threshold": 75}).status_code == 200
    assert client.get("/api/settings", headers=headers).json()["confidence_threshold"] == 75.0


def test_dashboard_stats(monkeypatch):
    _upload(monkeypatch, "Shipment delayed at the warehouse due to a forklift breakdown.", "OPERATIONS", 88.0)
    data = client.get("/api/dashboard/stats", headers=_token(*ADMIN)).json()
    assert data["total_documents"] >= 1
    assert set(["FINANCE", "HR", "LEGAL", "OPERATIONS"]) <= set(data["category_counts"])
