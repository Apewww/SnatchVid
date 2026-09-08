"""
SnatchVid core — shared downloader logic untuk CLI & API.
Dibungkus di atas yt-dlp dengan flag yang sudah diuji:
  - YouTube  : merge DASH (video+audio) via ffmpeg
  - TikTok   : impersonate chrome + extractor args app_info
  - Instagram: impersonate chrome + js runtime node
"""

from __future__ import annotations

import os
import re
import shutil
import sys
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

try:
    import yt_dlp
    from yt_dlp.networking.impersonate import ImpersonateTarget
except ImportError:
    print("[!] yt-dlp belum terinstall. Jalankan: pip install -r requirements.txt")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Konfigurasi platform
# ---------------------------------------------------------------------------

PLATFORMS = {
    "youtube": {
        "name": "YouTube",
        "emoji": "▶️",
        "color": "#FF0000",
        "regex": r"(youtube\.com|youtu\.be)",
    },
    "tiktok": {
        "name": "TikTok",
        "emoji": "🎵",
        "color": "#00F2EA",
        "regex": r"(tiktok\.com)",
    },
    "instagram": {
        "name": "Instagram",
        "emoji": "📸",
        "color": "#E1306C",
        "regex": r"(instagram\.com)",
    },
}

QUALITIES = ["360", "480", "720", "1080", "best"]


def normalize_quality(quality: str | int) -> str:
    """
    Normalisasi parameter kualitas → format yang dipahami yt-dlp.
    - "best" → "best"
    - angka berapa pun (misal "1920", 1080) → "1920" (dipakai sebagai batas
      tinggi video, misal bestvideo[height<=1920]).
    Raise ValueError kalau bukan angka positif atau "best".
    """
    if isinstance(quality, (int, float)) and quality > 0:
        return str(int(quality))
    q = str(quality).strip().lower()
    if q == "best":
        return "best"
    if q.isdigit() and int(q) > 0:
        return q
    raise ValueError(
        f"Kualitas harus 'best' atau angka tinggi piksel (misal 360, 720, 1080, 1920). "
        f"Received: {quality!r}"
    )


def detect_platform(url: str) -> Optional[str]:
    """Deteksi platform dari URL. Return key platform atau None."""
    for key, conf in PLATFORMS.items():
        if re.search(conf["regex"], url, re.IGNORECASE):
            return key
    return None


def default_opts() -> dict:
    """Opsi dasar yang aman untuk semua platform."""
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,          # jangan download playlist/auto-play
        "retries": 3,
        "socket_timeout": 30,
        "restrictfilenames": True,
    }


def ffmpeg_available() -> bool:
    """Cek apakah ffmpeg tersedia di PATH (dipakai merge DASH video+audio)."""
    return shutil.which("ffmpeg") is not None


def platform_opts(platform: str, quality: str = "720") -> dict:
    """Opsi tambahan spesifik platform (hasil spike test)."""
    opts = default_opts()

    if platform == "youtube":
        # YouTube pakai DASH: video & audio terpisah → merge pakai ffmpeg.
        # (download() sudah fast-fail kalau ffmpeg tidak ada.)
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]"
        opts.update({
            "format": fmt,
            "merge_output_format": "mp4",
            "js_runtimes": {"node": {}},  # butuh node/deno buat extract format lengkap
            "outtmpl": "%(title).80s.%(ext)s",
        })
    elif platform == "tiktok":
        opts.update({
            "impersonate": ImpersonateTarget(client="chrome"),  # butuh curl_cffi terinstall
            "js_runtimes": {"node": {}},
            "extractor_args": {"tiktok": {"app_info": ["com.ss.android.ugc.trill"]}},
            "outtmpl": "%(title).80s.%(ext)s",
        })
    elif platform == "instagram":
        opts.update({
            "impersonate": ImpersonateTarget(client="chrome"),
            "js_runtimes": {"node": {}},
            "outtmpl": "%(title).80s.%(ext)s",
        })
    else:
        opts["outtmpl"] = "%(title).80s.%(ext)s"

    return opts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_title(info: dict) -> str:
    """Judul yang aman buat nama file (potong kalau kepanjangan)."""
    title = info.get("title") or info.get("id") or "snatchvid"
    safe = re.sub(r'[\\/:*?"<>|]', "_", title).strip()
    return safe[:100] or "snatchvid"


def _fmt_duration(sec: Optional[float]) -> str:
    if not sec:
        return "?"
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _fmt_size(b: Optional[int]) -> str:
    if not b:
        return "?"
    for unit in ["B", "KB", "MB", "GB"]:
        if b < 1024:
            return f"{b:.1f}{unit}"
        b /= 1024
    return f"{b:.1f}TB"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@dataclass
class MediaInfo:
    platform: str
    title: str
    duration: str
    duration_sec: Optional[float]
    thumbnail: Optional[str]
    uploader: Optional[str]
    formats: list = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    @property
    def platform_display(self) -> str:
        return f"{PLATFORMS[self.platform]['emoji']} {PLATFORMS[self.platform]['name']}"


_progress_lock = threading.Lock()


def get_info(url: str, progress_hook: Optional[Callable] = None) -> MediaInfo:
    """Ambil metadata video tanpa mendownload."""
    platform = detect_platform(url)
    if not platform:
        raise ValueError(
            "URL tidak didukung. Support: YouTube, TikTok, Instagram."
        )

    opts = platform_opts(platform)
    if progress_hook:
        opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)

    if info is None:
        raise RuntimeError("Gagal mengekstrak info video.")

    # List format & resolusi yang tersedia (untuk UI)
    formats = []
    seen = set()
    for f in info.get("formats") or []:
        h = f.get("height")
        if h and f.get("vcodec") != "none" and h not in seen:
            seen.add(h)
            formats.append({"height": h, "ext": f.get("ext", "mp4"), "size": f.get("filesize")})
    formats.sort(key=lambda x: x["height"], reverse=True)

    return MediaInfo(
        platform=platform,
        title=info.get("title", "Untitled"),
        duration=_fmt_duration(info.get("duration")),
        duration_sec=info.get("duration"),
        thumbnail=info.get("thumbnail"),
        uploader=info.get("uploader") or info.get("channel") or info.get("creator"),
        formats=formats,
        raw=info,
    )


def download(
    url: str,
    outdir: str | Path = "downloads",
    quality: str = "720",
    progress_hook: Optional[Callable] = None,
    keep_metadata: bool = False,
    output_type: str = "original",
    wa_duration: int = 30,
) -> dict:
    """
    Download video. Return dict: {path, title, platform, ext, size, ...}.
    - quality: "best" atau angka tinggi piksel berapa pun (360, 720, 1080, 1920…).
      Untuk YouTube dipakai sebagai batas tinggi video; TikTok/IG selalu
      mengambil kualitas terbaik yang tersedia (parameter diabaikan).
    - output_type: "original" | "wa_status" (H.264+AAC siap WA) | "mp3" (audio saja)
    - wa_duration: max detik untuk output_type="wa_status" (default 30 = batas status WA)
    - progress_hook: callback berformat yt-dlp (d, {status, downloaded_bytes, total_bytes, ...})
    """
    quality = normalize_quality(quality)

    platform = detect_platform(url)
    if not platform:
        raise ValueError("URL tidak didukung. Support: YouTube, TikTok, Instagram.")

    # Validasi output_type & ffmpeg
    from core.convert import OUTPUT_TYPES, to_mp3, to_wa_status
    if output_type not in OUTPUT_TYPES:
        raise ValueError(
            f"output_type harus salah satu dari: {', '.join(OUTPUT_TYPES)}"
        )
    if OUTPUT_TYPES[output_type]["needs_ffmpeg"] and not ffmpeg_available():
        raise RuntimeError(
            f"Output '{output_type}' butuh ffmpeg. Install dulu lalu restart:\n"
            "  Windows: winget install ffmpeg\n"
            "  Linux  : sudo apt install ffmpeg"
        )

    # YouTube modern: semua format DASH (video & audio terpisah) → ffmpeg WAJIB
    # untuk merge. Fast-fail dengan pesan jelas, daripada error mentah dari yt-dlp.
    if platform == "youtube" and not ffmpeg_available():
        raise RuntimeError(
            "ffmpeg tidak terdeteksi, padahal video YouTube wajib butuh ffmpeg "
            "untuk menggabungkan video+audio (format DASH).\n"
            "Install dulu lalu restart:\n"
            "  Windows: winget install ffmpeg\n"
            "  Linux  : sudo apt install ffmpeg"
        )

    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    opts = platform_opts(platform, quality)
    opts["outtmpl"] = str(outdir / "%(title).80s.%(ext)s")
    opts["noprogress"] = True
    if progress_hook:
        opts["progress_hooks"] = [progress_hook]

    with yt_dlp.YoutubeDL(opts) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            # YouTube tanpa ffmpeg: video DASH-only nggak bisa single-file
            if (
                platform == "youtube"
                and not ffmpeg_available()
                and "Requested format is not available" in msg
            ):
                raise RuntimeError(
                    "Video YouTube ini tidak memiliki format single-file (progressive), "
                    "jadi butuh ffmpeg untuk menggabungkan video+audio. "
                    "Install ffmpeg dulu lalu restart:\n"
                    "  Windows: winget install ffmpeg\n"
                    "  Linux  : sudo apt install ffmpeg"
                )
            raise

    if info is None:
        raise RuntimeError("Download gagal: tidak ada info video.")

    # Cari file hasil download (mungkin sudah di-merge jadi .mp4)
    path = Path(str(ydl.prepare_filename(info)))
    if not path.exists():
        # fallback: cari file terbaru di outdir
        candidates = sorted(outdir.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
        path = candidates[0] if candidates else None
    if path is None or not path.exists():
        raise RuntimeError("Download selesai tapi file tidak ditemukan.")

    result = {
        "path": str(path),
        "title": _clean_title(info),
        "platform": platform,
        "ext": path.suffix.lstrip("."),
        "size": path.stat().st_size,
        "thumbnail": info.get("thumbnail"),
        "ffmpeg": ffmpeg_available(),
        "merged": platform == "youtube" and ffmpeg_available(),
        "output_type": output_type,
        "wa_duration": wa_duration,
    }

    # Post-process: convert output sesuai permintaan
    if output_type == "wa_status":
        out_path = path.with_name(path.stem + "_wa.mp4")
        to_wa_status(path, out_path, max_sec=wa_duration)
        # Hapus file asli (biar nggak numpuk)
        if out_path != path:
            path.unlink(missing_ok=True)
        path = out_path
        result["path"] = str(path)
        result["ext"] = "mp4"
        result["size"] = path.stat().st_size
        result["converted"] = "wa_status"
    elif output_type == "mp3":
        out_path = path.with_name(path.stem + ".mp3")
        to_mp3(path, out_path)
        if out_path != path:
            path.unlink(missing_ok=True)
        path = out_path
        result["path"] = str(path)
        result["ext"] = "mp3"
        result["size"] = path.stat().st_size
        result["converted"] = "mp3"

    if keep_metadata:
        import json
        meta_path = path.with_suffix(".json")
        meta_path.write_text(
            json.dumps({k: info.get(k) for k in ("title", "uploader", "duration", "thumbnail", "webpage_url")}, indent=2),
            encoding="utf-8",
        )
        result["metadata_path"] = str(meta_path)

    return result