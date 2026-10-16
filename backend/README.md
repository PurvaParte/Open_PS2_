# EvidentAI Backend

FastAPI backend for adaptive learning, sandbox coding assessments, event recording, session replay, and evidence-based integrity analysis.

## Running the Backend

Run these commands from the `backend` directory.

### Option 1: Direct Execution (Recommended on Windows — avoids PowerShell execution policy issues)
```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Option 2: 1-Click Batch File
Double-click `run_backend.bat` or run:
```cmd
run_backend.bat
```

### Option 3: PowerShell Script Activation
In PowerShell, relative scripts require leading `.\` and `.ps1` extension:
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
*(If PowerShell displays execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first, or simply use Option 1).*

## Running Tests
```powershell
.\.venv\Scripts\python -m pytest -v
```

## API Documentation
- Interactive Docs: http://127.0.0.1:8000/docs
- Health Status: http://127.0.0.1:8000/health
