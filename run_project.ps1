# run_project.ps1
# This script starts all the services required for testing the Kenya Health Access application.

$ROOT_DIR = Get-Location
$BACKEND_DIR = Join-Path $ROOT_DIR "backend"
$FRONTEND_DIR = Join-Path $ROOT_DIR "frontend"
$VENV_PYTHON = Join-Path $ROOT_DIR "venv\Scripts\python.exe"
$VENV_CELERY = Join-Path $ROOT_DIR "venv\Scripts\celery.exe"

Write-Host "🚀 Starting Kenya Health Access services..." -ForegroundColor Cyan

# 1. Start Django Backend
Write-Host "📦 Starting Django Backend on port 8000..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $BACKEND_DIR; & '$VENV_PYTHON' manage.py runserver" -WindowStyle Normal

# 2. Start Celery Worker
Write-Host "👷 Starting Celery Worker..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $BACKEND_DIR; & '$VENV_CELERY' -A backend worker -l info" -WindowStyle Normal

# 3. Start Celery Beat
Write-Host "⏰ Starting Celery Beat..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $BACKEND_DIR; & '$VENV_CELERY' -A backend beat -l info" -WindowStyle Normal

# 4. Start Ngrok Tunnel (using domain from settings)
Write-Host "🌐 Starting Ngrok Tunnel..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "ngrok http 8000 --domain=sphygmographic-unrising-farah.ngrok-free.dev" -WindowStyle Normal

# 5. Start Frontend
Write-Host "💻 Starting Frontend on port 5173..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd $FRONTEND_DIR; npm run dev" -WindowStyle Normal

Write-Host "✅ All services initiated. Please check the individual terminal windows for logs." -ForegroundColor Yellow
Write-Host "API: http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
Write-Host "Ngrok: https://sphygmographic-unrising-farah.ngrok-free.dev"
