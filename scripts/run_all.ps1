# Starts the FastAPI backend and the Vite frontend on Windows (PowerShell).
# Run from anywhere:  powershell -ExecutionPolicy Bypass -File scripts\run_all.ps1
$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir

if (-not (Test-Path "models\classifier\config.json")) {
    Write-Warning "No model in models\classifier - every document will go to human review."
}

$python = Join-Path $ProjectDir "backend\venv\Scripts\python.exe"
if (-not (Test-Path $python)) { $python = "python" }

Write-Host "[AI Scategorizer] Backend:  http://localhost:8000  (docs: /api/docs)"
$backend = Start-Process -FilePath $python -ArgumentList "-m", "uvicorn", "backend.app.main:app", "--host", "127.0.0.1", "--port", "8000", "--reload" -WorkingDirectory $ProjectDir -PassThru -NoNewWindow

Write-Host "[AI Scategorizer] Frontend: http://localhost:5173"
$frontend = Start-Process -FilePath "npm.cmd" -ArgumentList "run", "dev", "--", "--port", "5173" -WorkingDirectory (Join-Path $ProjectDir "frontend") -PassThru -NoNewWindow

Write-Host "Press Ctrl+C to stop both servers."
try { Wait-Process -Id $backend.Id, $frontend.Id }
finally {
    Stop-Process -Id $backend.Id, $frontend.Id -ErrorAction SilentlyContinue
}
