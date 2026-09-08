# 📑 PRD — SnatchVid

> **Status:** Versi 1.0 (Draft untuk review & redesign UI)
> **Penulis:** RaflyLabs (Chatbot Hermes)
> **Tanggal:** 8 September 2026
> **Repositori:** `D:\Github\SnatchVid`
> **Workspace:** `D:\Stellochron\SnatchVid`

---

## 1. Ringkasan Eksekutif

**SnatchVid** adalah tool downloader video dari 3 platform — **TikTok, Instagram, YouTube** — tersedia dalam 2 bentuk: **CLI** (`cli.py`) dan **API + Frontend web** (`api/main.py` + `static/index.html`).

Aplikasi sudah berfungsi penuh di backend (engine downloader + konversi output) dan sudah diuji untuk 3 platform. **Gap utama saat ini adalah UX frontend**: alur masih bertele-tele (paste → Cek → pilih kualitas → pilih format → pilih durasi → download = 4-5 klik sebelum file terdownload), serta informasi teknis (HEVC/H.264, codec, dll) yang membingungkan user awam.

Tujuan iterasi ini: **memperbaiki frontend agar lebih user-friendly**, dengan 3 varian mockup yang sudah disiapkan (lihat folder `mockup/`), menunggu keputusan desain.

### Status Fitur

| Fitur | Status |
|-------|:---:|
| Engine downloader (TikTok / IG / YouTube) | ✅ Berfungsi |
| Konversi output (Original / WA Status / MP3) | ✅ Berfungsi |
| Kualitas fleksibel (auto-detect dari video) | ✅ Berfungsi |
| Penanganan ffmpeg (fast-fail + pesan ramah) | ✅ Berfungsi |
| CLI | ✅ Berfungsi |
| API (FastAPI) | ✅ Berfungsi |
| Frontend demo | ⚠️ Berfungsi tapi UX belum optimal |
| Redesign UI sesuai mockup | ⏳ **In progress** |

---

## 2. Tujuan Produk & Non-Tujuan

### Tujuan
- Menyediakan cara **paling cepat & mudah** untuk mendownload video TikTok, Instagram, dan YouTube.
- Menghasilkan file yang **kompatibel** — termasuk siap di-post ke status WhatsApp (via konversi H.264+AAC).
- Menjadi produk yang **user-friendly** untuk user awam, bukan cuma developer (target redesign ini).

### Non-Tujuan
- Bukan untuk mendownload konten berhak cipta / pribadi secara ilegal.
- Belum menyediakan akun, login, atau riwayat download.
- Belum mendukung konten TikTok **private** / Instagram **story** yang butuh cookie (tercatat sebagai gap P1).
- Belum ada resumable upload / job queue.

---

## 3. Target Pengguna & Persona

| Persona | Kebutuhan |
|---------|-----------|
| **Pengguna harian TikTok** (remaja/dewasa muda) | Download video lucu / tren tanpa watermark untuk simpan & share. Ingin **cepat**, tanpa paham teknis. |
| **Content creator / admin WA** | Download video buat di-post ulang ke status WhatsApp. Butuh **format WA-ready** (H.264+AAC). |
| **Pengguna non-teknis** (keluarga, teman) | Paste link → download. **Nggak mau pilih-pilih opsi teknis**. |

**Prinsip desain (dari gap saat ini):**
- Satu tombol aksi dominan (mendukung flow "paste → langsung download").
- Hapus istilah teknis dari tampilan (codec, DASH, HEVC) → ganti dengan bahasa sehari-hari.
- Semua opsi punya default yang masuk akal (kualitas best, format original) — user tinggal klik download.
- Feedback status jelas (progress + toast sukses).

---

## 4. Sitemap / Struktur Tampilan

```
SnatchVid Web (single page — /)
├── Header: Logo + tagline + badge platform
├── Input bar: tempel link + tombol aksi
│   └── (saat ketik) hint deteksi platform otomatis
├── Preview card (muncul setelah info diambil)
│   ├── Thumbnail + platform badge + judul + uploader + durasi
│   ├── Kualitas (pill: Best / 360p / 720p / 1080p… auto-detect)
│   ├── Format output (pill: Original / WhatsApp / Musik)
│   │   └── (jika WhatsApp) Durasi (15 / 30 / 60 dtk)
│   └── Tombol Download + progress bar
└── Footer: kredit
```

> Detail 3 varian visual: lihat `mockup/01-*, 02-*, 03-*`.

---

## 5. Fitur Utama

Prioritas: **P0** = wajib v1, **P1** = penting, **P2** = nice-to-have.

### 5.1 Download Video (3 platform) — P0 ✅
**Deskripsi:** Inti aplikasi. Tempel URL TikTok/Instagram/YouTube → dapat file video.
- Deteksi platform otomatis dari URL.
- Teknologi: `yt-dlp` + flag per platform (lihat dokumentasi teknis).

**Acceptance criteria:**
- [ ] YouTube up to 1080p (merge DASH via ffmpeg)
- [ ] TikTok tanpa watermark (format 720p via impersonate)
- [ ] Instagram Reels / feed video
- [ ] Error platform berubah (update yt-dlp) ditangani dengan pesan jelas

### 5.2 Format Output — P0 ✅
**Deskripsi:** Pilih bentuk file hasil.

| Output | Deskripsi | Butuh ffmpeg |
|--------|-----------|:---:|
| `original` | File asli sesuai platform | ❌ |
| `wa_status` | Re-encode H.264+AAC, portrait 9:16, siap post status WA | ✅ |
| `mp3` | Ekstrak audio saja | ✅ |

**Acceptance criteria:**
- [ ] Output `wa_status` menghasilkan file yang **bisa di-post ke WhatsApp** (H.264+AAC, 1080x1920).
- [ ] Output `mp3` menghasilkan audio 192kbps.
- [ ] Opsi yang butuh ffmpeg **dinonaktifkan** (dengan alasan jelas) kalau ffmpeg tidak terdeteksi.

### 5.3 Kualitas Fleksibel — P0 ✅
**Deskripsi:** Pengguna pilih kualitas; parameter menerima `best` atau angka tinggi piksel berapa pun (360, 720, 1080, 1920…), bukan list kaku.
- YouTube: kualitas = batas atas tinggi (`bestvideo[height<=N]`).
- TikTok/IG: selalu ambil terbaik (kualitas diabaikan, platform ini punya resolusi terbatas).

**Acceptance criteria:**
- [ ] `normalize_quality()` menerima `best` / 360 / 1080 / 1920 dst.
- [ ] Nilai invalid (`0`, `abc`, `-5`, `1.5`) ditolak dengan pesan jelas.

### 5.4 Penanganan ffmpeg (Graceful) — P0 ✅
**Deskripsi:** YouTube modern semuanya DASH (video+audio terpisah) → ffmpeg wajib. Tanpa ffmpeg, aplikasi **fast-fail sebelum download** dengan instruksi install, bukan error mentah dari yt-dlp.

**Acceptance criteria:**
- [ ] Tanpa ffmpeg + YouTube → pesan ramah + `winget install ffmpeg`.
- [ ] Tanpa ffmpeg + TikTok/IG → tetap jalan.
- [ ] Status ffmpeg terlihat via `/api/health` & preview card.

### 5.5 CLI — P0 ✅
**Deskripsi:** Gunakan dari terminal, support batch, `--info`, pilih kualitas/output.

```bash
python cli.py "URL" [-q 1080] [-t wa_status] [--wa-duration 30] [--info] [-o folder]
```

**Acceptance criteria:**
- [ ] Download single & batch
- [ ] `--info` tanpa download
- [ ] Progress bar

### 5.6 Frontend Redesign — P0 ⏳
**Deskripsi:** Menerapkan salah satu dari 3 mockup ke `api/static/index.html` agar user-friendly.
- Varian: `mockup/01-*` (Dark Linear), `02-*` (Warm Airbnb), `03-*` (Bold Vercel).
- Semua sudah menyederhanakan flow menjadi: **paste link → tombol aksi → pilih opsi → download** dengan 1 tombol dominan.

**Acceptance criteria (target redesign):**
- [ ] Flow download ≤ 3 klik dari halaman kosong.
- [ ] Tidak ada istilah teknis (codec/DASH) di UI utama.
- [ ] Responsif di mobile.
- [ ] Progress bar + toast sukses.

### 5.7 Pilihan Lanjutan (Rencana) — P1
- **Cookie support**: konten TikTok private / IG story.
- **Batch URL via web**: paste banyak link sekaligus.
- **Job queue**: download async untuk video panjang.
- **Riwayat download** (localStorage).

---

## 6. Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Backend | Python 3.10+ / FastAPI + uvicorn |
| Engine download | yt-dlp (+ curl_cffi untuk impersonate) |
| Konversi media | ffmpeg (subprocess) |
| Frontend | HTML/CSS/JS vanilla (single page, dark theme) |
| JS runtime yt-dlp | Node.js |
| Deploy target | Lokal (Windows via `.bat`), opsional RaflyLabs |

### Dependensi (requirements.txt)
```
fastapi
uvicorn
yt-dlp
curl_cffi
```

---

## 7. Metrik Keberhasilan

| Metrik | Baseline (test) | Target setelah redesign |
|--------|:---:|:---:|
| Waktu sampai file terunduh (user baru) | ~5 klik, tebak-tebakan | ≤3 klik, jelas |
| Keberhasilan download TikTok | ✅ (882 KB, 16s, tanpa watermark) | Tetap ≥95% |
| Keberhasilan download IG | ✅ (6 MB, 18s) | Tetap ≥95% |
| Keberhasilan YouTube 1080p | ✅ (9.5 MB, 272s) | Tetap (butuh ffmpeg) |
| Output WA siap-post | ✅ (H.264 1080x1920) | Tetap |
| User bisa paham UI tanpa bantuan | Belum diukur | **>80%** (survey/feedback informal) |

---

## 8. Gap & Rekomendasi (urut prioritas)

1. **P0 — Frontend UX belum optimal** (ini iterasi saat ini). 3 mockup siap, tinggal pilih & terapkan.
2. **P1 — ffmpeg belum portable / tidak ada auto-check di frontend** yang benar-benar mencegah tombol WA aktif saat ffmpeg hilang. (Sudah ada notice, tapi bisa lebih kuat — nonaktifkan tombol + tooltip.)
3. **P1 — Tidak ada dukungan konten private** (TikTok private, IG story) karena belum ada cookie input.
4. **P2 — Frontend tidak support batch & tidak ada job queue** untuk video panjang / banyak.
5. **P2 — Tidak ada riwayat / manajemen hasil download** di web.

---

## 9. Roadmap

| Fase | Isi | Status |
|------|-----|:---:|
| **Fase 0 — Basic** | Engine 3 platform, CLI, API, frontend demo | ✅ Selesai |
| **Fase 1 — UX** | Pilih & terapkan mockup (redesign `index.html`), polish alur, responsif mobile, nonaktifkan opsi tanpa ffmpeg | ⏳ **In progress** |
| **Fase 2 — Fitur** | Cookie support, batch URL, job queue, riwayat | 🔜 Rencana |
| **Fase 3 — Deploy** | Deploy ke RaflyLabs (opsional), polisikan rate limit | 🔜 Rencana |

---

## 10. Lampiran — Catatan Teknis Penting

- **ffmpeg wajib untuk YouTube**: semua format YouTube modern adalah DASH (video & audio terpisah) → butuh merge. Tanpa ffmpeg, hanya TikTok & IG yang jalan. Install: `winget install ffmpeg` (Windows) / `sudo apt install ffmpeg` (Linux).
- **Codec hasil per platform** (alasan kenapa WA butuh konversi):
  - TikTok → HEVC/H.265 (⚠️ sering ditolak WA)
  - YouTube → AV1 + Opus (⚠️ kurang didukung)
  - Instagram → VP9 + AAC (⚠️ kadang bermasalah)
  - **WA butuh H.264 + AAC**
- **TikTok/IG rapuh terhadap perubahan platform** — kalau error, update: `pip install -U yt-dlp`.
- **TikTok rate-limit** intermitten ("Unable to extract universal data") — frontend pakai auto-retry 3x.
- **Kualitas**: `best` / angka berapa pun; TikTok & IG selalu best.
- **Filname aman** — title disanitasi & dipotong 100 char.

### Kontak / Info
- Developer: Rafly Anggara (Apewww), RaflyLabs
- Repo: `D:\Github\SnatchVid`
- Workspace: `D:\Stellochron\SnatchVid`
