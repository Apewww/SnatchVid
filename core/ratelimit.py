"""
SnatchVid Rate Limiter — Pembatasan laju permintaan untuk deployment produksi.
Membaca konfigurasi dari environment variable / file .env.
Mendukung reverse proxy (X-Forwarded-For, X-Real-IP) dan fallback ke IP client.
"""

from __future__ import annotations

import math
import os
import threading
import time
from typing import Dict, List

from fastapi import HTTPException, Request


def _get_bool_env(name: str, default: bool = True) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _get_int_env(name: str, default: int) -> int:
    val = os.getenv(name)
    if not val:
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


class InMemoryRateLimiter:
    """Sliding-window in-memory rate limiter per client IP."""

    def __init__(self):
        self._lock = threading.Lock()
        self._history: Dict[str, List[float]] = {}

    @property
    def enabled(self) -> bool:
        return _get_bool_env("RATE_LIMIT_ENABLED", default=True)

    @property
    def limit(self) -> int:
        return _get_int_env("RATE_LIMIT_PER_MINUTE", default=30)

    @property
    def window(self) -> int:
        return _get_int_env("RATE_LIMIT_WINDOW_SECONDS", default=60)

    def get_client_ip(self, request: Request) -> str:
        """Deteksi IP client dengan dukungan reverse proxy header."""
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            # Ambil IP pertama jika terdapat rantai proxy (client, proxy1, proxy2)
            ip = forwarded.split(",")[0].strip()
            if ip:
                return ip

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()

        if request.client and request.client.host:
            return request.client.host

        return "127.0.0.1"

    def check(self, request: Request) -> None:
        """
        Validasi batas request. Jika terlampaui, lempar HTTPException 429.
        """
        if not self.enabled:
            return

        ip = self.get_client_ip(request)
        now = time.time()
        window_start = now - self.window

        with self._lock:
            # Bersihkan riwayat lama di luar sliding window
            timestamps = [ts for ts in self._history.get(ip, []) if ts > window_start]
            
            if len(timestamps) >= self.limit:
                oldest = timestamps[0]
                retry_after = max(1, math.ceil(oldest + self.window - now))
                self._history[ip] = timestamps
                raise HTTPException(
                    status_code=429,
                    detail=(
                        f"Batas laju permintaan terlampaui. Maksimal {self.limit} request "
                        f"per {self.window} detik per IP. Coba lagi dalam {retry_after} detik."
                    ),
                    headers={"Retry-After": str(retry_after)},
                )

            timestamps.append(now)
            self._history[ip] = timestamps


# Instance singleton
limiter = InMemoryRateLimiter()


def rate_limit_dependency(request: Request) -> None:
    """FastAPI Depends dependency untuk endpoint sensitif."""
    limiter.check(request)
