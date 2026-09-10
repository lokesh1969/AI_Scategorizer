# MetroMind — Intelligent Enterprise Document Classification & Routing System

**MetroMind** is a production-style, bilingual (English + Hindi) enterprise document classification and intelligent routing platform engineered as a B.Tech Capstone Project. 

It automates the ingestion, preprocessing, optical character recognition (OCR), NLP understanding, ML classification, priority evaluation, AI summarization, named entity extraction, sentiment scoring, department routing, and human verification workflow for incoming organizational documents.

---

## Key Features

1. **Bilingual OCR & Document Ingestion**
   - Direct text extraction for digital PDF, DOCX, XLSX, and TXT files.
   - Real Tesseract OCR (`eng` + `hin`) for scanned PDFs and PNG/JPG images.
   - OpenCV image preprocessing pipeline (Grayscale, CLAHE contrast enhancement, median denoising, Otsu binarization, sharpening, and deskewing).
   - Bilingual language detection (English, Devanagari Hindi, and Mixed Hindi + English).

2. **Machine Learning Classifier**
   - Calibrated TF-IDF + Logistic Regression NLP classifier predicting document category across **SAFETY**, **FINANCE**, **MAINTENANCE**, and **OPERATIONS**.
   - Outputs full probability distribution and exact confidence percentage score.

3. **Configurable Confidence Threshold & Human Verification Queue**
   - Configurable confidence threshold (default `70%`).
   - High confidence ($\ge 70\%$) documents automatically route to responsible department with status `AI VERIFIED`.
   - Low confidence ($< 70\%$) documents route to the **Human Verification Queue** with status `HUMAN VERIFICATION REQUIRED`.
   - Reviewers can view preprocessed image previews, edit categories, record audit notes, and approve re-routing.

4. **Urgency & Priority Engine**
   - Priority rating (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`), score (0–100), and transparent reasoning based on emergency terms, safety hazards, equipment breakdowns, and category context.

5. **AI Summarizer, NER & Sentiment Analysis**
   - Extractive AI summarizer preserving original Hindi & English text.
   - Named Entity Recognition (NER) extracting `MONEY`, `DATE`, `STATION`, `PERSON`, `PHONE`, `EMAIL`, `EQUIPMENT`, and `DOCUMENT_NUMBER`.
   - Bilingual sentiment analysis (`POSITIVE`, `NEUTRAL`, `NEGATIVE`).

6. **Role-Based Access Control (RBAC)**
   - Backend-enforced authorization for 5 distinct roles:
     - `UPLOADER`: Upload & view own documents.
     - `STATION_CONTROLLER`: Access Safety & Operations documents + Verification.
     - `FINANCE_MANAGER`: Access Finance documents + Verification.
     - `MAINTENANCE_HEAD`: Access Maintenance documents + Verification.
     - `ADMIN`: Full access to documents, user management, audit logs, and settings.

7. **Dual Database Persistence (MongoDB + Persistent SQLite Fallback)**
   - Connects to local MongoDB automatically when running (`mongodb://localhost:27017`).
   - Seamlessly uses a persistent SQLite document store (`backend/metromind.db`) if MongoDB is inactive, ensuring zero setup friction on macOS.

---

## Demo User Credentials

The database is pre-seeded with 5 demo accounts for immediate testing:

| Role | Email Address | Password | Department Access |
| :--- | :--- | :--- | :--- |
| **System Admin** | `admin@metromind.local` | `admin123` | All System Modules & Settings |
| **Station Controller** | `station@metromind.local` | `station123` | Safety & Operations |
| **Finance Manager** | `finance@metromind.local` | `finance123` | Finance & Payments |
| **Maintenance Head** | `maintenance@metromind.local` | `maint123` | Maintenance & Equipment Faults |
| **Document Uploader** | `uploader@metromind.local` | `user123` | Document Upload & Self Records |

---

## macOS Installation & Prerequisites

### 1. Install System Dependencies via Homebrew
```bash
brew install tesseract tesseract-lang poppler
```

### 2. Set Up Python Virtual Environment
```bash
python3 -m venv backend/venv
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

### 3. Install Frontend Node Dependencies
```bash
cd frontend
npm install
cd ..
```

---

## Quick Start & Execution

### Option A: Run via Single Command Script
```bash
./scripts/run_all.sh
```

### Option B: Run Services Manually

1. **Train ML Model & Seed Database**:
   ```bash
   source backend/venv/bin/activate
   python ml/train_classifier.py
   python scripts/seed_db.py
   ```

2. **Start Backend API Service**:
   ```bash
   source backend/venv/bin/activate
   python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Start Frontend React Application**:
   ```bash
   cd frontend
   npm run dev
   ```

- **Frontend App**: [http://localhost:5173](http://localhost:5173)
- **Backend Swagger API Docs**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

---

## Automated Test Suite

Run unit and integration tests covering Authentication, RBAC, Image Preprocessing, OCR, Classification, Priority Scoring, and Verification workflows:

```bash
source backend/venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

---

## Technical Stack

- **Backend**: Python 3.11, FastAPI, Pydantic V2, PyMongo / SQLite3, PyMuPDF, python-docx, openpyxl, OpenCV, Pillow, PyTesseract.
- **Machine Learning**: Scikit-Learn (TF-IDF + Logistic Regression), Joblib, SpaCy, NLTK, Langdetect.
- **Frontend**: React 18, Vite, React Router V6, Axios, Lucide React, Glassmorphism Custom CSS.
