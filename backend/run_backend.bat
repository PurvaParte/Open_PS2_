@echo off
cd /d "%~dp0"
echo Starting EvidentAI Backend on http://127.0.0.1:8000 ...
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
