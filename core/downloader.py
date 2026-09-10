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
import time
import urllib.parse
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
    "twitter": {
        "name": "Twitter / X",
        "emoji": "🐦",
        "color": "#1DA1F2",
        "regex": r"(twitter\.com|x\.com)",
    },
    "facebook": {
        "name": "Facebook",
        "emoji": "📘",
        "color": "#1877F2",
        "regex": r"(facebook\.com|fb\.watch)",
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


def clean_url(url: str) -> str:
    """Bersihkan tracking parameters dari URL (terutama parameter tracking TikTok & webapp)."""
    try:
        url_str = url.strip()
        parsed = urllib.parse.urlparse(url_str)
        if "tiktok.com" in parsed.netloc.lower():
            # Hapus tracking query params (?is_from_webapp=1&sender_device=pc...)
            return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, parsed.path, "", "", ""))
        return url_str
    except Exception:
        return url.strip()


def detect_platform(url: str) -> Optional[str]:
    """Deteksi platform dari URL. Return key platform atau None."""
    cleaned = clean_url(url)
    for key, conf in PLATFORMS.items():
        if re.search(conf["regex"], cleaned, re.IGNORECASE):
            return key
    return None


class _QuietLogger:
    """Peredam output internal yt-dlp agar error transient tidak bocor ke konsol saat retry."""
    def debug(self, msg): pass
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass


def default_opts() -> dict:
    """Opsi dasar yang aman untuk semua platform."""
    return {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,          # jangan download playlist/auto-play
        "logger": _QuietLogger(),
        "retries": 5,                # retry transient network/HTTP errors
        "fragment_retries": 10,      # retry dropped DASH chunks
        "file_access_retries": 3,
        "socket_timeout": 30,
        "restrictfilenames": True,
        "remote_components": ["ejs:github"],
    }


def ffmpeg_available() -> bool:
    """Cek apakah ffmpeg tersedia di PATH (dipakai merge DASH video+audio)."""
    return shutil.which("ffmpeg") is not None


def platform_opts(platform: str, quality: str = "720") -> dict:
    """Opsi tambahan spesifik platform (hasil spike test & hardening)."""
    opts = default_opts()

    if platform == "youtube":
        # YouTube pakai DASH: video & audio terpisah → merge pakai ffmpeg.
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
        opts.update({
            "format": fmt,
            "merge_output_format": "mp4",
            "js_runtimes": {"node": {}},
            "extractor_args": {
                "youtube": {
                    "player_client": ["web", "mweb", "android", "ios"]
                }
            },
            "outtmpl": "%(title).80s.%(ext)s",
        })
    elif platform == "tiktok":
        # Gunakan impersonasi Chrome TLS langsung ke webpage challenge solver.
        # Hindari app_info API JSON yang sering melempar 'rehydration data' error.
        opts.update({
            "impersonate": ImpersonateTarget(client="chrome"),
            "js_runtimes": {"node": {}},
            "outtmpl": "%(title).80s.%(ext)s",
        })
    elif platform == "instagram":
        opts.update({
            "impersonate": ImpersonateTarget(client="chrome"),
            "js_runtimes": {"node": {}},
            "outtmpl": "%(title).80s.%(ext)s",
        })
    elif platform == "twitter":
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
        opts.update({
            "format": fmt,
            "merge_output_format": "mp4",
            "impersonate": ImpersonateTarget(client="chrome"),
            "outtmpl": "%(title).80s.%(ext)s",
        })
    elif platform == "facebook":
        if quality == "best":
            fmt = "bestvideo+bestaudio/best"
        else:
            fmt = f"bestvideo[height<={quality}]+bestaudio/best[height<={quality}]/best"
        opts.update({
            "format": fmt,
            "merge_output_format": "mp4",
            "impersonate": ImpersonateTarget(client="chrome"),
            "outtmpl": "%(title).80s.%(ext)s",
        })
    else:
        opts["outtmpl"] = "%(title).80s.%(ext)s"

    return opts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_title(info: dict) -> str:
    """Judul yang aman buat nama file (potong kalau kepanjangan dan hindari reserved windows names)."""
    title = info.get("title") or info.get("id") or "snatchvid"
    safe = re.sub(r'[\x00-\x1f\x7f\\/:*?"<>|]', "_", str(title))
    safe = re.sub(r'\s+', ' ', safe).strip(" .")
    reserved = {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4",
                "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2",
                "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
    if safe.upper() in reserved:
        safe = f"{safe}_file"
    return safe[:90].rstrip(" .") or "snatchvid"


def _translate_error(err: Exception, platform: str) -> str:
    """Ubah pesan error teknis menjadi pesan yang jelas dan informatif bagi user."""
    msg = str(err)
    lower = msg.lower()
    if "sign in to confirm you're not a bot" in lower or "confirm your age" in lower:
        return "YouTube memerlukan verifikasi login / anti-bot untuk video ini."
    if "unable to extract universal data for rehydration" in lower or "bot detection" in lower:
        return "TikTok membatasi akses sementara (rate limit / bot challenge). Silakan coba sesaat lagi."
    if "please log in to access this content" in lower or "login required" in lower:
        return "Instagram membatasi akses (konten privat atau butuh login akun)."
    if "this tweet is from a private account" in lower or "requires authentication" in lower or "this media is not available" in lower:
        return "Twitter / X membatasi akses (tweet privat, sensitif, atau memerlukan login)."
    if "you must log in to continue" in lower or "login to continue" in lower:
        return "Facebook membatasi akses (video privat, grup tertutup, atau butuh login akun)."
    if "video unavailable" in lower or "this video has been removed" in lower or "private video" in lower:
        pname = PLATFORMS.get(platform, {}).get("name", "ini")
        return f"Video {pname} tidak tersedia (dihapus, privat, atau dibatasi wilayah)."
    if "requested format is not available" in lower:
        return "Format resolusi yang diminta tidak tersedia untuk video ini."
    return msg


def _extract_with_retry(
    opts: dict,
    url: str,
    download: bool = False,
    max_attempts: int = 3,
    platform: str = "general"
) -> tuple[dict, yt_dlp.YoutubeDL]:
    """
    Ekstrak metadata atau download dengan intelligent backoff retry.
    Mencegah kegagalan seketika saat terjadi transient rate limit / edge challenge.
    """
    last_exc = None
    delay = 1.5
    for attempt in range(1, max_attempts + 1):
        try:
            ydl = yt_dlp.YoutubeDL(opts)
            info = ydl.extract_info(url, download=download)
            if info is not None:
                return info, ydl
        except yt_dlp.utils.DownloadError as e:
            last_exc = e
            msg = str(e).lower()
            # Fast-fail jika error permanen (tidak ada gunanya di-retry)
            if any(p in msg for p in ["video unavailable", "private video", "has been removed", "404", "requested format is not available"]):
                raise RuntimeError(_translate_error(e, platform)) from e
            if attempt < max_attempts:
                time.sleep(delay)
                delay *= 1.8
        except Exception as e:
            last_exc = e
            if attempt < max_attempts:
                time.sleep(delay)
                delay *= 1.8

    if last_exc:
        raise RuntimeError(_translate_error(last_exc, platform)) from last_exc
    raise RuntimeError("Gagal memproses video setelah beberapa kali percobaan.")


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
    url = clean_url(url)
    platform = detect_platform(url)
    if not platform:
        raise ValueError(
            "URL tidak didukung. Support: YouTube, TikTok, Instagram, Twitter / X, Facebook."
        )

    opts = platform_opts(platform)
    if progress_hook:
        opts["progress_hooks"] = [progress_hook]

    info, ydl = _extract_with_retry(opts, url, download=False, max_attempts=3, platform=platform)

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
    url = clean_url(url)
    quality = normalize_quality(quality)

    platform = detect_platform(url)
    if not platform:
        raise ValueError("URL tidak didukung. Support: YouTube, TikTok, Instagram, Twitter / X, Facebook.")

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

    info, ydl = _extract_with_retry(opts, url, download=True, max_attempts=3, platform=platform)

    # Cari file hasil download (bisa .mp4, .mkv, .webm, atau nama hasil merge)
    prep_path = Path(str(ydl.prepare_filename(info)))
    path = prep_path
    if not path.exists():
        # Cek kemungkinan ekstensi lain yang umum (misal hasil merge jadi .mp4)
        for cand_ext in [".mp4", ".mkv", ".webm", ".m4a", ".mp3"]:
            cand = prep_path.with_suffix(cand_ext)
            if cand.exists():
                path = cand
                break
        else:
            # Fallback: cari file non-temp terbaru di outdir
            candidates = [
                p for p in outdir.glob("*")
                if not p.name.endswith((".part", ".ytdl", ".temp")) and p.is_file()
            ]
            candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
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