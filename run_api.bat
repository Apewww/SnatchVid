@echo off
REM SnatchVid API — buka http://localhost:8000
cd /d "%~dp0"
py -3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000