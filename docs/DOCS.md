# 🛠️ Dokumentasi Teknis — SnatchVid

Dokumentasi teknis lengkap: arsitektur, API reference, cara kerja engine, dan panduan.

---

## 1. Arsitektur

```
                        ┌─────────────────────────────┐
                        │        frontend/index       │
                        │  (HTML/CSS/JS single page)  │
                        └──────────┬──────────────────┘
                                   │  HTTP (fetch)
                        ┌──────────▼──────────────────┐
                        │     FastAPI  (api/main.py)  │
                        │  /api/health /api/info      │
                        │  /api/download /api/platforms│
                        │  /api/output-types          │
                        └──────────┬──────────────────┘
                                   │
        ┌──────────────────────────▼──────────────────────────┐
        │               core/downloader.py  (shared engine)   │
        │   detect_platform · get_info · download · normalize  │
        │                                                      │
        │   ┌──────────────┐   ┌──────────────────────────┐    │
        │   │ yt-dlp       │   │  core/convert.py         │    │
        │   │ (download)   │   │  to_wa_status / to_mp3   │    │
        │   └──────────────┘   └──────────────────────────┘    │
        └──────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────▼──────────────────────────┐
        │  ffmpeg (merge DASH / re-encode) · curl_cffi        │
        │  (impersonate) · Node.js (js runtime yt-dlp)        │
        └─────────────────────────────────────────────────────┘
```

### Principle: Shared Engine
CLI (`cli.py`) dan API (`api/main.py`) **dua-duanya memakai `core/downloader.py`** — satu sumber logika, tidak ada duplikasi. Konversi output dipisah di `core/convert.py`.

### Alur download (end-to-end)
1. **Deteksi platform** dari URL (`detect_platform`) → kalau bukan YouTube/TikTok/Instagram → error ramah.
2. **Validasi kualitas** (`normalize_quality`) → `best` atau angka tinggi.
3. **Validasi output & ffmpeg** → kalau output butuh ffmpeg tapi nggak ada → fast-fail dengan pesan install.
4. **YouTube + tanpa ffmpeg** → fast-fail (semua DASH, wajib merge).
5. **Download** via yt-dlp dengan `platform_opts()` (flag per-platform).
6. **Konversi output** (optional): `wa_status` → re-encode H.264+AAC 9:16; `mp3` → ekstrak audio.
7. **API**: simpan di temp dir unik per request → kirim `FileResponse` → `BackgroundTask` cleanup folder.

---

## 2. Struktur Folder

```
SnatchVid/
├── cli.py                     # CLI entry (argparse, progress bar, quality_type)
├── core/
│   ├── downloader.py          # Shared engine: platform, get_info, download, normalize_quality, ffmpeg_available
│   └── convert.py             # Konversi: to_wa_status, to_mp3, OUTPUT_TYPES
├── api/
│   ├── main.py                # FastAPI backend + serve static
│   └── static/
│       └── index.html         # Frontend demo (target: ganti dengan mockup terpilih)
├── requirements.txt
├── setup.bat                  # Setup Windows sekali jalan
├── run_cli.bat                # Launcher CLI Windows
└── run_api.bat                # Launcher API Windows
```

---

## 3. API Reference (FastAPI)

Base URL: `http://localhost:8000` (default). Docs interaktif: `/docs` (Swagger UI).

### 3.1 `GET /`
Serve frontend demo.

### 3.2 `GET /api/health`
Cek status service + ffmpeg.

```json
{ "status": "ok", "service": "snatchvid", "ffmpeg": true }
```

### 3.3 `GET /api/platforms`
Daftar platform didukung.

```json
{
  "youtube": { "name": "YouTube", "emoji": "▶️" },
  "tiktok":  { "name": "TikTok",  "emoji": "🎵" },
  "instagram":{ "name": "Instagram","emoji": "📸" }
}
```

### 3.4 `GET /api/output-types`
Daftar format output.

```json
{
  "original":  { "label": "Original", "emoji": "📦", "desc": "...", "needs_ffmpeg": false },
  "wa_status": { "label": "WhatsApp Status", "emoji": "📱", "desc": "...", "needs_ffmpeg": true },
  "mp3":       { "label": "MP3 Audio", "emoji": "🎵", "desc": "...", "needs_ffmpeg": true }
}
```

### 3.5 `GET /api/info?url=<URL>`
Ambil metadata video **tanpa download**.

**Param:** `url` (wajib).

**Response:**
```json
{
  "platform": "youtube",
  "platform_display": "▶️ YouTube",
  "title": "Judul Video",
  "duration": "4:32",
  "duration_sec": 272.5,
  "thumbnail": "https://...",
  "uploader": "Channel Name",
  "formats": [ {"height": 1080, "ext": "mp4", "size": null}, ... ],
  "ffmpeg": true,
  "quality_note": null
}
```

**Error:** `400` URL tidak didukung; `422` gagal ekstrak (termasuk TikTok rate-limit).

### 3.6 `GET /api/download?url=<URL>&quality=<Q>&output=<O>&wa_duration=<D>`
Download video, kirim sebagai attachment file, auto-cleanup temp.

**Params:**
| Param | Default | Deskripsi |
|-------|---------|-----------|
| `url` | (wajib) | URL video |
| `quality` | `best` | `best` atau tinggi piksel (360, 720, 1080, 1920…) |
| `output` | `original` | `original` \| `wa_status` \| `mp3` |
| `wa_duration` | `30` | Max detik untuk `wa_status` |

**Response:** binary file (`video/mp4`, `audio/mpeg`, dst), `Content-Disposition` berisi filename aman.

**Error:** `400` URL tidak didukung / kualitas invalid / output invalid; `422` download gagal (incl. ffmpeg absent, rate-limit).

---

## 4. Cara Kerja Engine (`core/downloader.py`)

### Konstanta
- `PLATFORMS`: dict {youtube, tiktok, instagram} dengan name/emoji/color/regex.
- `QUALITIES`: `["360","480","720","1080","best"]` (legacy — sekarang dipakai `normalize_quality`).

### Fungsi inti
- **`normalize_quality(quality) -> str`** — terima `best` atau angka positif; raise `ValueError` untuk invalid.
- **`detect_platform(url) -> str|None`** — deteksi dari regex.
- **`default_opts()`** — opsi aman: quiet, noplaylist, retries 3, socket_timeout 30, restrictfilenames.
- **`ffmpeg_available() -> bool`** — cek `shutil.which("ffmpeg")`.
- **`platform_opts(platform, quality)`** — flag spesifik platform:
  - **YouTube:** `format="bestvideo[height<=Q]+bestaudio/best"`, `merge_output_format="mp4"`, `js_runtimes={node:{}}`.
  - **TikTok:** `impersonate=chrome`, `extractor_args app_info=com.ss.android.ugc.trill`, `js_runtimes`.
  - **Instagram:** `impersonate=chrome`, `js_runtimes`.
- **`get_info(url) -> MediaInfo`** — ekstrak metadata + list format/resolusi (dedup, sort desc).
- **`download(url, ...) -> dict`** — download + optional convert. Detail di bawah.

### Alur `download()` (validasi berlapis)
```
1. normalize_quality(quality)
2. detect_platform(url) → None? raise
3. validasi output_type di OUTPUT_TYPES
4. kalau output butuh ffmpeg & ffmpeg absent → raise (install instruksi)
5. YouTube & ffmpeg absent → raise (wajib merge DASH)
6. platform_opts + outtmpl ke outdir
7. ydl.extract_info(download=True) — tangkap DownloadError, beri pesan ramah utk kasus tertentu
8. cari file hasil; bangun result dict
9. kalau output wa_status → to_wa_status; mp3 → to_mp3; hapus file asli
10. keep_metadata → simpan .json
```

### `core/convert.py`
- **`to_wa_status(src, dst, max_sec=30)`** — `scale=1080:1920:force_original_aspect_ratio=decrease, pad=1080:1920` → portrait 9:16; `libx264` crf23 `yuv420p` + AAC 128k + `+faststart`; potong `-t max_sec`.
- **`to_mp3(src, dst, bitrate=192)`** — `-vn -c:a libmp3lame -b:a 192k`.
- **`_run(args)`** — jalankan `ffmpeg -y -hide_banner -loglevel error`, raise kalau returncode != 0.
- **`OUTPUT_TYPES`** — registry format output + flag `needs_ffmpeg`.

---

## 5. Platform-Specific Quirks & Pitfalls

| Platform | Quirk | Mitigasi |
|----------|-------|----------|
| **YouTube** | Semua video modern DASH-only (0 progressive) → wajib merge ffmpeg | Fast-fail tanpa ffmpeg + pesan install |
| **YouTube** | Format lengkap butuh JS runtime | `js_runtimes: {node: {}}` — butuh Node.js |
| **TikTok** | Rate-limit intermitten: `Unable to extract universal data for rehydration` (HTTP 422) | Frontend auto-retry 3x |
| **TikTok** | BUTUH impersonation biar tidak diblok | `impersonate chrome` (curl_cffi) + app_info extractor args |
| **TikTok/IG** | Kualitas terbatas → quality param diabaikan, selalu best | Documented |
| **Semua** | Platform sering berubah → yt-dlp error | `pip install -U yt-dlp` |
| **Impersonate** | API Python butuh `ImpersonateTarget(client="chrome")` (CLI terima string "chrome") | Pakai object di Python |

### Catatan ffmpeg (Windows)
- Install: `winget install ffmpeg` → **tutup & buka ulang terminal/CMD** biar PATH ke-rescan.
- TikTok & IG **tetap jalan tanpa ffmpeg**; hanya YouTube yang wajib.
- Status ffmpeg bisa dicek: `GET /api/health`.

---

## 6. Panduan Menjalankan

### Prasyarat
- Python **3.11+** (disarankan 3.12+/3.14 — yt-dlp deprecated 3.10)
- **ffmpeg** (WAJIB utk YouTube): `winget install ffmpeg`
- **Node.js** (JS runtime yt-dlp): `winget install OpenJS.NodeJS.LTS`

### Windows (via .bat)
```cmd
setup.bat     # install deps sekali
run_api.bat   # buka http://localhost:8000
run_cli.bat "URL"
```

### Manual
```bash
pip install -r requirements.txt

# CLI
python cli.py "https://www.tiktok.com/@user/video/123" -q 720
python cli.py "https://youtu.be/abc" --info
python cli.py "URL" -t wa_status --wa-duration 30
python cli.py "URL" -t mp3

# API
uvicorn api.main:app --reload --port 8000
```

### CLI flags
```
URL            satu atau lebih URL video
-q, --quality  best / angka piksel (default 720)
-t, --output-type original | wa_status | mp3 (default original)
--wa-duration  max detik utk wa_status (default 30)
--info         tampilkan info tanpa download
-o, --output   folder output (default downloads/)
```

---

## 7. Changelog

### v0.1.0 (8 Sep 2026) — Basic + Fitur Output
- ✅ Engine 3 platform (YouTube/TikTok/Instagram) via yt-dlp.
- ✅ CLI + API FastAPI + Frontend demo.
- ✅ Format output: original / wa_status (H.264+AAC 9:16) / mp3.
- ✅ Kualitas fleksibel (best / angka bebas) — `normalize_quality`.
- ✅ Penanganan ffmpeg graceful (fast-fail + pesan ramah + status di health/info).
- ✅ Auto-cleanup temp API, frontend auto-retry TikTok, progress bar.
- 📦 3 varian mockup UI (`mockup/`) siap untuk redesign.

---

## 8. Roadmap / Ideas

- **Cookie support** untuk konten private (TikTok private / IG story).
- **Batch URL** via web.
- **Job queue** untuk download async video panjang.
- **Riwayat download** di frontend (localStorage).
- **Deploy** ke RaflyLabs (opsional) + rate limiting.
