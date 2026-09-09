@echo off
cd /d "%~dp0"

echo ===================================================
echo               SnatchVid Environment Setup
echo ===================================================
echo.

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 goto :USE_PY

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 goto :USE_PYTHON

echo [X] Python tidak ditemukan di sistem PATH!
echo Silakan install Python 3.11+ dari https://www.python.org/
pause
exit /b 1

:USE_PY
set PYTHON_EXE=py -3
goto :CHECK_VENV

:USE_PYTHON
set PYTHON_EXE=python
goto :CHECK_VENV

:CHECK_VENV
if exist ".venv\Scripts\activate.bat" goto :VENV_EXISTS

echo [*] Membuat virtual environment di .venv...
%PYTHON_EXE% -m venv .venv
if errorlevel 1 goto :VENV_FAILED
echo [OK] Virtual environment (.venv) berhasil dibuat.
goto :INSTALL_DEPS

:VENV_EXISTS
echo [OK] Virtual environment (.venv) sudah ada.
goto :INSTALL_DEPS

:INSTALL_DEPS
echo.
echo [*] Mengaktifkan virtual environment dan menginstall dependensi...
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [!] Terjadi kendala saat menginstall requirements.txt.
) else (
    echo [OK] Semua dependensi Python berhasil dipasang di .venv.
)

if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [OK] File .env berhasil disiapkan dari .env.example.
    )
)
goto :CHECK_FFMPEG

:CHECK_FFMPEG
echo.
echo [*] Memeriksa ketersediaan ffmpeg...
where ffmpeg >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] ffmpeg ditemukan di PATH sistem.
) else (
    echo [!] PERINGATAN: ffmpeg TIDAK ditemukan!
    echo     Merge audio/video resolusi tinggi dan WhatsApp Status membutuhkan ffmpeg.
    echo     Install via command line: winget install ffmpeg
)

echo.
echo ===================================================
echo Setup Selesai!
echo Jalankan aplikasi menggunakan:
echo   - Web App / API : run_api.bat  (buka http://localhost:8000)
echo   - Terminal CLI  : run_cli.bat ^<URL^>
echo ===================================================
pause
exit /b 0

:VENV_FAILED
echo [X] Gagal membuat virtual environment (.venv).
pause
exit /b 1