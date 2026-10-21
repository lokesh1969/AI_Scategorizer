# AI Scategorizer

Human-in-the-loop classification and routing of enterprise documents in English and Hindi.

Upload a PDF, Word, Excel, text file or scanned image. The system:
1. extracts the text, using OCR (Tesseract `eng+hin` with OpenCV preprocessing) for scans;
2. classifies the document into **FINANCE, HR, LEGAL or OPERATIONS** with a fine-tuned transformer;
3. adds a priority score, summary, key entities and sentiment;
4. **auto-routes** confident predictions to the department, and sends the rest to a **Human Verification Queue**, with role-based access control and an audit trail.

📘 **Full documentation:** [PROJECT.md](PROJECT.md) covers the architecture, how each pipeline step works, the API, roles, setup on Windows and macOS/Linux, and the research and paper guide.

## Quick start

```bash
# backend (from this folder)
python -m venv backend/venv
backend\venv\Scripts\activate            # macOS/Linux: source backend/venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env                     # set SECRET_KEY
python -m uvicorn backend.app.main:app --port 8000 --reload

# frontend (second terminal)
cd frontend && npm install && npm run dev
```

- App: http://localhost:5173
- API docs: http://localhost:8000/api/docs
- Demo login: `admin@aiscategorizer.local` / `admin123`. Other roles are listed in [PROJECT.md §5](PROJECT.md#5-users-roles-and-access-control).
- Put the fine-tuned model in `models/classifier/`. Without it, every document goes to human review.

## Tests

```bash
python -m pytest tests -v
```

## Research

The `research/` folder contains reproducible experiments:
- a dataset split;
- a TF-IDF baseline and fine-tuning for DistilBERT, MuRIL or XLM-R;
- an evaluation that reports accuracy and macro-F1 with confidence intervals, per-language scores, calibration, confidence-threshold trade-offs and significance tests.

See [PROJECT.md §12](PROJECT.md#12-research-guide-turning-this-into-a-paper).

## Stack

FastAPI · Pydantic v2 · MongoDB/SQLite · PyMuPDF · Tesseract · OpenCV · Hugging Face Transformers · React 19 · Vite
