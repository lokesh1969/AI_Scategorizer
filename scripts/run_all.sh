#!/bin/bash
# Starts the FastAPI backend and the Vite frontend (macOS / Linux).
# Demo users and the default threshold are seeded automatically on API startup.
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

source backend/venv/bin/activate

if [ ! -f "models/classifier/config.json" ]; then
    echo "[AI Scategorizer] WARNING: no model in models/classifier - every document will go to human review."
fi

echo "[AI Scategorizer] Backend:  http://localhost:8000  (docs: /api/docs)"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

echo "[AI Scategorizer] Frontend: http://localhost:5173"
(cd frontend && npm run dev -- --port 5173) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
