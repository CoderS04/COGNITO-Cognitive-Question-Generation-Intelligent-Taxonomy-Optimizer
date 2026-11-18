@echo off
echo ===================================================
echo Running COGNITO Comprehensive Verification Suite
echo ===================================================
cd /d "%~dp0"
call .venv\Scripts\activate.bat
cd backend
python test_system.py
pause
