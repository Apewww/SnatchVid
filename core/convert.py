"""
SnatchVid convert — post-processing output video.
WhatsApp Status butuh H.264 + AAC (codec lain kayak HEVC/AV1/VP9 sering
ditolak atau gagal diputar/di-post). Di sini kita re-encode via ffmpeg.

Fungsi:
  - to_wa_status(): H.264+AAC MP4, portrait 9:16, trim ≤ durasi maks, faststart
  - to_mp3()      : ekstrak audio jadi MP3
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _run(args: list[str]) -> None:
    """Jalankan ffmpeg, raise RuntimeError kalau gagal."""
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg gagal: {proc.stderr.strip() or 'unknown error'}")


def _duration_sec(path: Path) -> float | None:
    """Durasi video via ffprobe. Return None kalau gagal."""
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True,
        )
        return float(proc.stdout.strip()) if proc.returncode == 0 else None
    except Exception:
        return None


def _has_audio(path: Path) -> bool:
    """Cek apakah file media memiliki setidaknya 1 audio stream."""
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a",
             "-show_entries", "stream=codec_type",
             "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
            capture_output=True, text=True,
        )
        return bool(proc.stdout.strip())
    except Exception:
        return False


def to_wa_status(src: str | Path, dst: str | Path, max_sec: int = 30) -> Path:
    """
    Re-encode ke format WhatsApp Status:
      - H.264 (libx264) + AAC (atau -an jika video tanpa audio)
      - Portrait 9:16 dengan letterbox (video landscape tetap muat)
      - Trim ke max_sec (default 30s — batas status WA)
      - faststart biar langsung bisa diputar
    """
    src_p, dst_p = Path(src), Path(dst)
    if not dst_p.suffix:
        dst_p = dst_p.with_suffix(".mp4")

    dur = _duration_sec(src_p)
    trim = []
    if dur is not None and dur > max_sec:
        trim = ["-t", str(max_sec)]
    elif dur is not None:
        trim = ["-t", str(max_sec)]

    # Jika video bisu (tidak punya stream audio), gunakan -an agar ffmpeg tidak error
    has_audio = _has_audio(src_p)
    audio_args = ["-c:a", "aac", "-b:a", "128k"] if has_audio else ["-an"]

    args = [
        "-i", str(src_p),
        *trim,
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,"
        "pad=1080:1920:(ow-iw)/2:(oh-ih)/2",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-pix_fmt", "yuv420p",
        *audio_args,
        "-movflags", "+faststart",
        str(dst_p),
    ]
    _run(args)
    return dst_p


def to_mp3(src: str | Path, dst: str | Path, bitrate: int = 192) -> Path:
    """Ekstrak audio jadi MP3 (bitrate default 192kbps)."""
    src_p, dst_p = Path(src), Path(dst)
    if not dst_p.suffix:
        dst_p = dst_p.with_suffix(".mp3")

    if not _has_audio(src_p):
        raise ValueError("Video ini tidak memiliki audio track (video bisu), sehingga tidak dapat dikonversi ke MP3.")

    args = [
        "-i", str(src_p),
        "-vn",
        "-c:a", "libmp3lame",
        "-b:a", f"{bitrate}k",
        str(dst_p),
    ]
    _run(args)
    return dst_p


OUTPUT_TYPES = {
    "original": {
        "label": "Original",
        "emoji": "📦",
        "desc": "File asli sesuai platform (HEVC/AV1/VP9 — bisa ditolak WA)",
        "needs_ffmpeg": False,
    },
    "wa_status": {
        "label": "WhatsApp Status",
        "emoji": "📱",
        "desc": "Re-encode H.264+AAC, portrait 9:16, siap di-post ke status",
        "needs_ffmpeg": True,
    },
    "mp3": {
        "label": "MP3 Audio",
        "emoji": "🎵",
        "desc": "Ekstrak audio saja (buat nada dering / musik)",
        "needs_ffmpeg": True,
    },
}