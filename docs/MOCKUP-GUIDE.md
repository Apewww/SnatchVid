# 🎨 Panduan Mockup UI SnatchVid

Panduan ini buat kamu (Kak Ivoni) yang mau lanjut bikin / modif desain UI SnatchVid. Ada 3 varian mockup siap pakai yang bisa langsung dibuka & dicoba.

---

## 📂 Letak File Mockup

```
D:\Stellochron\SnatchVid\mockup\
├── 01-linear-clean\     # Dark minimal (Linear style)
│   ├── index.html
│   └── README.md        # penjelasan design stance
├── 02-warm-friendly\    # Warm friendly (Airbnb style)
│   ├── index.html
│   └── README.md
└── 03-vercel-bold\      # Bold action-first (Vercel style)
    ├── index.html
    └── README.md
```

---

## ▶️ Cara Membuka Mockup

**Cara 1 — Langsung di browser (visu alah):**
- Double-click `index.html` (buka via browser). Ini menampilkan **halaman statis**.

**Cara 2 — Full interaktif (dengan data asli):**
- Mockup butuh backend `/api/*` biar coba download. Jadi jalankan server SnatchVid dulu:
  ```cmd
  cd D:\Github\SnatchVid
  run_api.bat
  ```
- Lalu buka mockup-nya di browser. **Catatan:** mockup di folder `mockup/` memanggil `/api/...` (relative path) — biar berfungsi penuh, file `index.html` mockup yang dipilih perlu ditempatkan di `D:\Github\SnatchVid\api\static\index.html`.

---

## 🔍 Ringkasan 3 Varian

| Varian | Gaya | Warna | Font | Vibes |
|--------|------|-------|------|-------|
| `01-linear-clean` | Dark minimal | Hitam `#08090a` + ungu `#7170ff` | Inter | Pro tool, sleek, presisi |
| `02-warm-friendly` | Terang ramah | Off-white + coral `#ff385c` | DM Sans | Hangat, personal, nggak intimidasi |
| `03-vercel-bold` | Hitam-putih tegas | Monokrom + putih | Sora | Action-first, tegas, cepat |

## Semua mockup sudah punya (behavior yang sama & lebih user-friendly dari versi live):
- ✅ **Satu tombol aksi dominan** — paste link → klik → preview muncul → download. (Versi live butuh 4-5 klik.)
- ✅ **Auto-detect platform** saat ngetik URL (badge muncul).
- ✅ **Kualitas auto** — pill dari format yang tersedia (`⭐ Best` / `720p` / dst).
- ✅ **Format output** — Original / WhatsApp / Musik + durasi (15/30/60s) utk WA.
- ✅ **Progress bar** ketika mendownload.
- ✅ **Toast sukses/error** yang jelas.

---

## 🎯 Yang Perlu Kamu Perhatiin Kalau Bikin Sendiri / Modif

1. **Alur ≥ 3 klik dari halaman kosong sampai file terunduh.**
   - Kosong → (1) paste link → (2) klik aksi → (3) klik download. Ideal.
   - Tombol aksi utama harus dominan (warna kontras, besar).

2. **Hilangkan istilah teknis dari UI.**
   - Jangan tampilkan "HEVC", "H.264", "DASH", "codec", "re-encode" di tombol/label utama.
   - Ganti dengan bahasa sehari-hari: "WhatsApp Status", "Siap post status", "Musik saja".
   - Detail teknis boleh di tooltip / halaman bantuan, bukan di UI utama.

3. **Setiap opsi punya default yang masuk akal.**
   - Kualitas: `⭐ Best` (paling aman).
   - Format: `Original` — tapi mungkin `WhatsApp` lebih cocok kalau mayoritas user mau post status? Tergantung tujuan. Biar user yang milih.

4. **Nonaktifkan opsi yang nggak bisa dipakai.**
   - Kalau ffmpeg nggak terdeteksi, tombol "WhatsApp Status" & "Musik" harus **nonaktif** (grey + tooltip "Butuh ffmpeg, install dulu"), biar user nggak bingung kenapa error.

5. **Responsif di mobile.**
   - Banyak user buka dari HP. Test di viewport sempit: pill-wrap rapi, tombol gede, nggak ke-slice.

6. **Feedback selalu jelas.**
   - Loading state (spinner + teks progress), success (ukuran file), error (pesan manusiawi).
   - Jangan biarkan user nunggu tanpa indikasi.

---

## 🧪 Cara Test Mockup

1. Jalankan backend: `run_api.bat` (atau `uvicorn api.main:app --port 8000`).
2. Salin mockup pilihan ke `D:\Github\SnatchVid\api\static\index.html`.
3. Buka `http://localhost:8000/`.
4. Paste URL uji:
   - TikTok: `https://www.tiktok.com/@sukma48_/video/7675680578292698388`
   - YouTube: `https://www.youtube.com/watch?v=d4FAjc-wCaI`
   - Instagram: `https://www.instagram.com/reel/Dc_ArXbR7eC/`
5. Test alur: paste → klik → pilih format → download.
6. Cek output:
   - Format `WhatsApp` → file `.mp4` H.264+AAC portrait → **pastikan bisa di-post ke status WA**.
   - Format `Musik` → file `.mp3`.

---

## ✍️ Cara Kontribusi / Simpan Desain Kamu

- Simpan mockup baru di `D:\Stellochron\SnatchVid\mockup\<nama>\`.
- Update `PRD.md` bagian "Frontend Redesign" & "Metrik" kalau ada perubahan.
- Setelah desain final, terapkan ke `D:\Github\SnatchVid\api\static\index.html`.
