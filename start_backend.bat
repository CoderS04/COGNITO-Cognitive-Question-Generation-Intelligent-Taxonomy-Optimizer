@echo off
echo ===================================================
echo Starting COGNITO Backend (FastAPI + ChromaDB)
echo ===================================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
