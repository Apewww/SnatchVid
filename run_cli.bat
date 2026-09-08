@echo off
REM SnatchVid CLI - Jalankan SnatchVid downloader dalam virtual environment
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
python cli.py %*