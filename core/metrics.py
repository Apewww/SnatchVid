"""
SnatchVid Metrics — Pelacakan penggunaan persisten (Thread-safe).
Menyimpan statistik unduhan, perincian platform, total durasi, dan persentase keberhasilan.
File penyimpanan: data/metrics.json
"""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

METRICS_FILE = Path(__file__).resolve().parent.parent / "data" / "metrics.json"
_LOCK = threading.Lock()

DEFAULT_METRICS: Dict[str, Any] = {
    "total_requests": 0,
    "total_downloads": 0,
    "total_inspections": 0,
    "successful_downloads": 0,
    "failed_downloads": 0,
    "total_duration_sec": 0,
    "platforms": {
        "youtube": {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0},
        "tiktok": {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0},
        "instagram": {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0},
        "twitter": {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0},
        "facebook": {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0},
    },
    "formats": {
        "original": 0,
        "wa_status": 0,
        "mp3": 0,
    },
    "created_at": datetime.now(timezone.utc).isoformat(),
    "last_updated": datetime.now(timezone.utc).isoformat(),
}


def _load_metrics() -> Dict[str, Any]:
    if not METRICS_FILE.exists():
        return json.loads(json.dumps(DEFAULT_METRICS))
    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Pastikan struktur kunci lengkap
            for key, val in DEFAULT_METRICS.items():
                if key not in data:
                    data[key] = json.loads(json.dumps(val))
            for p in ["youtube", "tiktok", "instagram", "twitter", "facebook"]:
                if p not in data.get("platforms", {}):
                    data.setdefault("platforms", {})[p] = {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0}
            for fmt in ["original", "wa_status", "mp3"]:
                if fmt not in data.get("formats", {}):
                    data.setdefault("formats", {})[fmt] = 0
            return data
    except Exception:
        return json.loads(json.dumps(DEFAULT_METRICS))


def _save_metrics(data: Dict[str, Any]) -> None:
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    temp_file = METRICS_FILE.with_suffix(".tmp")
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    try:
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(METRICS_FILE)
    except Exception:
        if temp_file.exists():
            try:
                temp_file.unlink()
            except Exception:
                pass


def format_duration(seconds: int) -> Dict[str, str]:
    """Format durasi detik ke format teks multibahasa (EN & ID)."""
    if seconds <= 0:
        return {"en": "0 sec", "id": "0 dtk"}
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts_en = []
    parts_id = []

    if hours > 0:
        parts_en.append(f"{hours}h")
        parts_id.append(f"{hours}j")
    if minutes > 0:
        parts_en.append(f"{minutes}m")
        parts_id.append(f"{minutes}m")
    if secs > 0 or not parts_en:
        parts_en.append(f"{secs}s")
        parts_id.append(f"{secs}d")

    return {
        "en": " ".join(parts_en),
        "id": " ".join(parts_id),
    }


def record_inspection(platform: str) -> None:
    """Catat event pemeriksaan (inspect link)."""
    clean_p = (platform or "youtube").lower()
    with _LOCK:
        data = _load_metrics()
        data["total_requests"] += 1
        data["total_inspections"] += 1

        if clean_p not in data["platforms"]:
            data["platforms"][clean_p] = {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0}
        data["platforms"][clean_p]["inspected"] += 1

        _save_metrics(data)


def record_download(
    platform: str,
    duration_sec: int = 0,
    output_type: str = "original",
    success: bool = True,
) -> None:
    """Catat event unduhan selesai (sukses atau gagal)."""
    clean_p = (platform or "youtube").lower()
    clean_fmt = (output_type or "original").lower()
    dur = max(0, int(duration_sec or 0))

    with _LOCK:
        data = _load_metrics()
        data["total_requests"] += 1
        data["total_downloads"] += 1

        if success:
            data["successful_downloads"] += 1
            data["total_duration_sec"] += dur
        else:
            data["failed_downloads"] += 1

        if clean_p not in data["platforms"]:
            data["platforms"][clean_p] = {"inspected": 0, "downloaded": 0, "duration_sec": 0, "errors": 0}

        if success:
            data["platforms"][clean_p]["downloaded"] += 1
            data["platforms"][clean_p]["duration_sec"] += dur
        else:
            data["platforms"][clean_p]["errors"] += 1

        if clean_fmt in data["formats"]:
            data["formats"][clean_fmt] += 1
        else:
            data["formats"][clean_fmt] = 1

        _save_metrics(data)


def get_metrics_summary() -> Dict[str, Any]:
    """Mengembalikan ringkasan metrik lengkap siap pakai untuk API & Frontend."""
    with _LOCK:
        data = _load_metrics()

    total_dl = data.get("total_downloads", 0)
    success_dl = data.get("successful_downloads", 0)
    failed_dl = data.get("failed_downloads", 0)

    # Persentase keberhasilan
    if total_dl > 0:
        success_rate = round((success_dl / total_dl) * 100, 1)
    else:
        success_rate = 100.0

    total_dur_sec = data.get("total_duration_sec", 0)
    formatted_dur = format_duration(total_dur_sec)

    # Perincian platform
    platforms = data.get("platforms", {})
    total_platform_dl = sum(p.get("downloaded", 0) for p in platforms.values())

    platforms_summary = {}
    for p_name, p_data in platforms.items():
        p_dl = p_data.get("downloaded", 0)
        p_pct = round((p_dl / total_platform_dl * 100), 1) if total_platform_dl > 0 else 0.0
        platforms_summary[p_name] = {
            "inspected": p_data.get("inspected", 0),
            "downloaded": p_dl,
            "duration_sec": p_data.get("duration_sec", 0),
            "duration_formatted": format_duration(p_data.get("duration_sec", 0)),
            "errors": p_data.get("errors", 0),
            "share_percentage": p_pct,
        }

    return {
        "total_requests": data.get("total_requests", 0),
        "total_downloads": total_dl,
        "total_inspections": data.get("total_inspections", 0),
        "successful_downloads": success_dl,
        "failed_downloads": failed_dl,
        "success_rate": success_rate,
        "total_duration_sec": total_dur_sec,
        "total_duration_formatted": formatted_dur,
        "platforms": platforms_summary,
        "formats": data.get("formats", {}),
        "last_updated": data.get("last_updated", ""),
    }
