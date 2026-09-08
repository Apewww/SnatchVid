@echo off
REM Setup SnatchVid — install dependencies + cek ffmpeg
cd /d "%~dp0"
echo === SnatchVid Setup ===
py -3 -m pip install -r requirements.txt
echo.
echo Cek ffmpeg (WAJIB buat merge video YouTube)...
where ffmpeg >nul 2>nul && (echo OK: ffmpeg ditemukan) || (
  echo [!] ffmpeg TIDAK ditemukan. Install lewat: winget install ffmpeg
)
echo.
echo Selesai! Jalankan:
echo   CLI : run_cli.bat <URL>
echo   API : run_api.bat  ^(buka http://localhost:8000^)
pause