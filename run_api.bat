@echo off
REM SnatchVid API - Jalankan server web dalam virtual environment
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8

if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
    goto :RUN
)
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    goto :RUN
)

echo [!] Virtual environment tidak ditemukan.
echo     Silakan jalankan setup.bat terlebih dahulu untuk membuat venv.
echo.
pause
exit /b 1

:RUN
echo [*] Memulai SnatchVid Web Server di http://127.0.0.1:8000...
echo [*] Tekan Ctrl+C untuk menghentikan server.
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000