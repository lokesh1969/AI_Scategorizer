#!/bin/bash
echo "=========================================================="
echo " Starting MetroMind Enterprise Application Stack..."
echo "=========================================================="

# Determine project directory
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

# 1. Activate Python virtual environment
source backend/venv/bin/activate

# 2. Train model if not already present
if [ ! -f "ml/models/classifier.pkl" ]; then
    echo "[MetroMind] Pre-training ML classifier model..."
    python ml/train_classifier.py
fi

# 3. Seed Database
echo "[MetroMind] Seeding database accounts and demo documents..."
python scripts/seed_db.py

# 4. Start FastAPI Backend in background
echo "[MetroMind] Starting FastAPI backend on http://localhost:8000 ..."
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# 5. Start Vite React Frontend in background
echo "[MetroMind] Starting React Frontend on http://localhost:5173 ..."
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo "=========================================================="
echo " MetroMind is running!"
echo " Backend API:  http://localhost:8000"
echo " API Documentation: http://localhost:8000/api/docs"
echo " Frontend App: http://localhost:5173"
echo "=========================================================="
echo " Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
