@echo off
cd /d "%~dp0"
echo Running EvidentAI Pytest Suite ...
.\.venv\Scripts\python -m pytest -v
pause
