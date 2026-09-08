# ⚡ SnatchVid

Download video dari **TikTok**, **Instagram**, dan **YouTube** — 2 versi: **CLI** & **API + Frontend demo**.

> Demo build oleh RaflyLabs. Untuk penggunaan pribadi / konten sendiri.

## ✨ Fitur

| Platform  | Status | Catatan |
|-----------|--------|---------|
| YouTube   | ✅ | Merge DASH (video+audio) via ffmpeg, pilih kualitas 360–1080p |
| TikTok    | ✅ | Impersonation + extractor args (tanpa watermark untuk format 720p) |
| Instagram | ✅ | Reels & feed video |

## 📁 Struktur

```
SnatchVid/
├── cli.py              # Versi CLI
├── core/downloader.py  # Engine shared (CLI + API pakai ini)
├── api/
│   ├── main.py         # Backend FastAPI
│   └── static/index.html  # Frontend demo (dark theme)
├── requirements.txt
├── setup.bat           # Setup Windows sekali jalan
├── run_cli.bat         # Launcher CLI Windows
└── run_api.bat         # Launcher API Windows
```

## 🚀 Setup

**Prasyarat:**
- Python 3.11+ (disarankan 3.12+/3.14 — yt-dlp deprecated Python 3.10)
- **ffmpeg** — **WAJIB untuk YouTube** (format DASH video+audio terpisah, perlu merge): `winget install ffmpeg`
- **Node.js** — buat JS runtime yt-dlp (`winget install OpenJS.NodeJS.LTS`)

> ⚠️ Tanpa ffmpeg: TikTok & Instagram tetap jalan, tapi **YouTube tidak bisa** (semua format YouTube sekarang DASH — butuh merge). Aplikasi akan menampilkan pesan error yang jelas + petunjuk install. Status ffmpeg juga terlihat di `/api/health` dan preview card.

```bash
pip install -r requirements.txt
# atau di Windows tinggal jalanin: setup.bat
```

## 🖥️ CLI

```bash
# Download satu video
python cli.py "https://www.tiktok.com/@user/video/123456"

# Pilih kualitas (YouTube)
python cli.py "https://youtu.be/abc" -q 1080

# Batch download
python cli.py "https://youtu.be/abc" "https://www.instagram.com/reel/xyz/"

# Cek info dulu tanpa download
python cli.py "https://youtu.be/abc" --info

# Folder output custom
python cli.py <URL> -o hasil_download/
```

Di Windows: `run_cli.bat "URL"` (bisa langsung dari Explorer/CMD).

## 🌐 API + Frontend

```bash
uvicorn api.main:app --reload --port 8000
# Windows: run_api.bat
```

Lalu buka **http://localhost:8000/** — tampilan web demo: tempel link → cek info → pilih kualitas → download.

### Endpoint

| Method | Path | Deskripsi |
|--------|------|-----------|
| GET | `/` | Frontend demo |
| GET | `/api/health` | Cek status |
| GET | `/api/platforms` | Daftar platform didukung |
| GET | `/api/info?url=<URL>` | Metadata: title, durasi, thumbnail, resolusi |
| GET | `/api/download?url=<URL>&quality=720` | Download file (auto-cleanup) |

Contoh:

```bash
curl "http://localhost:8000/api/info?url=https://youtu.be/d4FAjc-wCaI"
curl -OJ "http://localhost:8000/api/download?url=https://youtu.be/d4FAjc-wCaI&quality=720"
```

Dokumentasi interaktif: **http://localhost:8000/docs** (Swagger UI).

## ⚙️ Cara Kerja Engine

Semua lewat **yt-dlp** dengan flag yang sudah diuji:

| Platform | Flag khusus |
|----------|-------------|
| YouTube | `-f "bestvideo[height<=Q]+bestaudio" --merge-output-format mp4` + `--js-runtimes node` |
| TikTok | `--impersonate chrome --extractor-args "tiktok:app_info=com.ss.android.ugc.trill"` |
| Instagram | `--impersonate chrome --js-runtimes node` |

- **curl_cffi** wajib terinstall (dipakai `--impersonate`).
- TikTok/IG paling rapuh terhadap perubahan platform — kalau error, update yt-dlp: `pip install -U yt-dlp`.

## 📝 Catatan

- Video diproses on-the-fly, **tidak disimpan permanen** di server (API pakai temp dir + auto-cleanup).
- Buat konten TikTok private/story Instagram, butuh cookie (belum termasuk di demo ini).
- Hak cipta tetap milik pembuat konten — gunakan bijak ya~ 😉