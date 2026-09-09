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

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

ENV_FILE = ROOT_DIR / ".env"
try:
    from dotenv import load_dotenv
    if ENV_FILE.is_file():
        load_dotenv(dotenv_path=ENV_FILE)
    else:
        load_dotenv()
except ImportError:
    # Fallback parser sederhana jika python-dotenv belum terpasang
    if ENV_FILE.is_file():
        try:
            with open(ENV_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception:
            pass

from core.downloader import (  # noqa: E402
    PLATFORMS,
    detect_platform,
    download,
    ffmpeg_available,
    get_info,
    normalize_quality,
)
from core.convert import OUTPUT_TYPES  # noqa: E402
from core.metrics import (  # noqa: E402
    get_metrics_summary,
    record_download,
    record_inspection,
)
from core.ratelimit import rate_limit_dependency  # noqa: E402

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


@app.get("/api/metrics")
def api_metrics():
    """Ambil ringkasan metrik penggunaan (platform breakdown, durasi, persentase)."""
    return get_metrics_summary()


@app.get("/api/info", dependencies=[Depends(rate_limit_dependency)])
def api_info(url: str = Query(..., description="URL video")):
    """Ambil metadata video (title, durasi, thumbnail, resolusi)."""
    detected_p = detect_platform(url)
    if not detected_p:
        raise HTTPException(400, detail="URL tidak didukung. Support: YouTube, TikTok, Instagram.")
    try:
        info = get_info(url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(422, detail=f"Gagal mengekstrak info: {e}")

    # Catat statistik pemeriksaan
    try:
        record_inspection(info.platform)
    except Exception:
        pass

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


@app.get("/api/download", dependencies=[Depends(rate_limit_dependency)])
def api_download(
    url: str = Query(..., description="URL video"),
    quality: str = Query("best", description="Kualitas: 'best' atau tinggi piksel (misal 720, 1080, 1920)"),
    output: str = Query("original", description="Format output: original | wa_status | mp3"),
    wa_duration: int = Query(30, description="Max durasi detik untuk wa_status (default 30)"),
):
    """Download video dan kirim sebagai file attachment."""
    detected_p = detect_platform(url)
    if not detected_p:
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
        # Catat metrik download sukses
        try:
            record_download(
                platform=result.get("platform", detected_p),
                duration_sec=result.get("duration_sec", 0),
                output_type=output,
                success=True,
            )
        except Exception:
            pass
    except Exception as e:
        _cleanup(job_dir)
        # Catat metrik download gagal
        try:
            record_download(
                platform=detected_p,
                duration_sec=0,
                output_type=output,
                success=False,
            )
        except Exception:
            pass
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
    import argparse
    import uvicorn

    default_host = os.getenv("HOST", "0.0.0.0").strip() or "0.0.0.0"
    default_port_str = os.getenv("PORT", "8000").strip()
    try:
        default_port = int(default_port_str)
    except ValueError:
        default_port = 8000

    parser = argparse.ArgumentParser(description="SnatchVid Web API Server")
    parser.add_argument("--host", default=default_host, help=f"Host to bind (default: {default_host})")
    parser.add_argument("--port", type=int, default=default_port, help=f"Port to bind (default: {default_port})")
    parser.add_argument("--reload", action="store_true", default=True, help="Enable auto-reload (default: True)")
    parser.add_argument("--no-reload", action="store_false", dest="reload", help="Disable auto-reload")

    args, _ = parser.parse_known_args()

    display_host = "127.0.0.1" if args.host in ("0.0.0.0", "") else args.host
    print(f"[*] Memulai SnatchVid Web Server di http://{display_host}:{args.port}...")
    print("[*] Tekan Ctrl+C untuk menghentikan server.\n")

    uvicorn.run("api.main:app", host=args.host, port=args.port, reload=args.reload)