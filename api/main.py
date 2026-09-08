"""
SnatchVid API — FastAPI service untuk demo.
Frontend: http://localhost:8000/
Docs    : http://localhost:8000/docs

Run:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import os
import shutil
import tempfile
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.downloader import (  # noqa: E402
    PLATFORMS,
    detect_platform,
    download,
    ffmpeg_available,
    get_info,
    normalize_quality,
)
from core.convert import OUTPUT_TYPES  # noqa: E402

app = FastAPI(
    title="SnatchVid API",
    description="Download video dari TikTok, Instagram & YouTube — demo build.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folder temp untuk hasil download API (dibersihkan otomatis)
TMP_ROOT = Path(tempfile.gettempdir()) / "snatchvid_api"
TMP_ROOT.mkdir(parents=True, exist_ok=True)


def _cleanup(dir_path: Path):
    """Hapus folder temp setelah file terkirim."""
    try:
        shutil.rmtree(dir_path, ignore_errors=True)
    except Exception:
        pass


@app.get("/")
def index():
    """Redirect ke frontend demo."""
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/favicon.ico")
def favicon():
    """Serve brand favicon."""
    icon_path = Path(__file__).parent / "static" / "assets" / "snatchvid-icon.png"
    if icon_path.exists():
        return FileResponse(icon_path, media_type="image/png")
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "snatchvid",
        "ffmpeg": ffmpeg_available(),
    }


@app.get("/api/platforms")
def platforms():
    """Daftar platform yang didukung."""
    return {k: {"name": v["name"], "emoji": v["emoji"]} for k, v in PLATFORMS.items()}


@app.get("/api/output-types")
def output_types():
    """Daftar format output yang tersedia."""
    return OUTPUT_TYPES


@app.get("/api/info")
def api_info(url: str = Query(..., description="URL video")):
    """Ambil metadata video (title, durasi, thumbnail, resolusi)."""
    if not detect_platform(url):
        raise HTTPException(400, detail="URL tidak didukung. Support: YouTube, TikTok, Instagram.")
    try:
        info = get_info(url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(422, detail=f"Gagal mengekstrak info: {e}")

    return {
        "platform": info.platform,
        "platform_display": info.platform_display,
        "title": info.title,
        "duration": info.duration,
        "duration_sec": info.duration_sec,
        "thumbnail": info.thumbnail,
        "uploader": info.uploader,
        "formats": info.formats,
        "ffmpeg": ffmpeg_available(),
        # Tanpa ffmpeg, YouTube cuma bisa progressive (biasanya ≤720p)
        "quality_note": (
            "ffmpeg tidak terdeteksi — kualitas YouTube dibatasi format progressive (maks ~720p). "
            "Install ffmpeg untuk kualitas penuh: winget install ffmpeg"
            if not ffmpeg_available() else None
        ),
    }


@app.get("/api/download")
def api_download(
    url: str = Query(..., description="URL video"),
    quality: str = Query("best", description="Kualitas: 'best' atau tinggi piksel (misal 720, 1080, 1920)"),
    output: str = Query("original", description="Format output: original | wa_status | mp3"),
    wa_duration: int = Query(30, description="Max durasi detik untuk wa_status (default 30)"),
):
    """Download video dan kirim sebagai file attachment."""
    if not detect_platform(url):
        raise HTTPException(400, detail="URL tidak didukung. Support: YouTube, TikTok, Instagram.")
    try:
        quality = normalize_quality(quality)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    if output not in OUTPUT_TYPES:
        raise HTTPException(400, detail=f"output harus salah satu dari: {', '.join(OUTPUT_TYPES)}")

    # Folder temp unik per request → aman untuk concurrent
    job_dir = TMP_ROOT / uuid.uuid4().hex
    job_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = download(
            url,
            outdir=job_dir,
            quality=quality,
            output_type=output,
            wa_duration=wa_duration,
        )
    except Exception as e:
        _cleanup(job_dir)
        raise HTTPException(422, detail=f"Download gagal: {e}")

    file_path = Path(result["path"])

    # Media type berdasarkan ekstensi
    ext_media = {
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "opus": "audio/opus",
    }
    media_type = ext_media.get(result["ext"], "application/octet-stream")

    # Kirim file, lalu bersihkan folder setelah response selesai
    return FileResponse(
        file_path,
        media_type=media_type,
        filename=f"{result['title']}.{result['ext']}",
        background=BackgroundTask(_cleanup, job_dir),
    )


# Serve frontend static (kalau ada file di api/static)
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists() and any(STATIC_DIR.iterdir()):
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)