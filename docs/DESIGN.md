# SnatchVid — Design System & UI Specification

Version: 1.0  
Status: Ready for frontend implementation  
Date: 8 September 2026  
Product: SnatchVid  
Owner: RaflyLabs / Rafly Anggara

## 1. Design direction

SnatchVid bukan landing page marketing dan bukan dashboard analitik. Ia adalah
utilitas kecil yang membantu pengguna menyelesaikan satu pekerjaan: tempel URL,
periksa video, pilih output bila perlu, lalu download.

Arah visual v1 disebut **Quiet Utility**: antarmuka yang tenang, konkret, dan
sedikit editorial. Desain sengaja memakai bidang paper yang hangat, teks
charcoal, garis hairline, serta satu aksen vermilion. Hasilnya terasa seperti
tool yang dibuat dengan pertimbangan, bukan komposisi SaaS generik.

Mockup referensi v1 memperlihatkan dua viewport:

- desktop: workbench utama dengan preview video dan opsi output;
- mobile: urutan konten yang sama, ditumpuk tanpa kehilangan konteks.

### 1.1 Anti-AI-slop rules

Aturan ini bersifat wajib untuk semua layar SnatchVid:

- Jangan gunakan gradient dekoratif, neon glow, glassmorphism, atau blob 3D.
- Jangan tambahkan kartu statistik, testimonial, logo cloud, atau section
  marketing yang tidak membantu proses download.
- Jangan memakai headline hiperbolik seperti “the future of downloading”.
- Jangan memenuhi layar dengan hero typography; input URL harus terlihat pada
  first viewport.
- Gunakan satu tombol aksi dominan pada satu waktu.
- Gunakan icon yang fungsional dan konsisten; jangan memakai emoji sebagai
  struktur navigasi utama.
- Rounded corner dipakai secukupnya, bukan setiap elemen dibuat kapsul.
- Informasi teknis hanya muncul ketika membantu mengambil keputusan.
- Setiap elemen visual harus punya hubungan langsung dengan URL, preview,
  kualitas, format, status, atau hasil download.

## 2. Product promise

**Primary copy:**

> Paste a link. Get the file.

**Supporting copy:**

> Download videos from YouTube, TikTok, and Instagram — quickly and locally.

Bahasa utama UI tetap English agar konsisten dengan nama endpoint dan tool,
namun copy error harus menggunakan bahasa sehari-hari yang mudah dipahami.
Hindari istilah seperti DASH, HEVC, AV1, dan codec pada UI utama.

## 3. Information architecture

Single page, tanpa login dan tanpa navigasi kompleks.

```text
SnatchVid
├── Header
│   ├── Brand mark + wordmark
│   ├── “local media utility”
│   └── Version
├── Main workbench
│   ├── Product promise
│   ├── URL input
│   │   ├── Video URL label
│   │   ├── URL field
│   │   ├── Detected platform status
│   │   └── Inspect link action
│   ├── Media preview (after /api/info succeeds)
│   │   ├── Thumbnail
│   │   ├── Platform
│   │   ├── Title
│   │   ├── Uploader
│   │   └── Duration
│   ├── Output controls
│   │   ├── Quality
│   │   ├── Output
│   │   ├── WhatsApp duration (conditional)
│   │   └── Advanced (secondary)
│   └── Download video action
└── Footer status
    ├── Backend / ffmpeg readiness
    └── Supported platforms
```

Tidak ada preview card ketika URL belum berhasil diperiksa. Ini membuat halaman
awal tetap ringan dan menjaga perhatian pada input.

## 4. Layout

### 4.1 Desktop: 1024px ke atas

- App shell memenuhi viewport dengan background `--color-paper`.
- Header tinggi sekitar 56px, memakai border bottom hairline.
- Workbench memiliki lebar maksimum 760px dan berada di tengah area aplikasi.
- Padding horizontal viewport: 40–64px.
- Jarak dari header ke headline: 52–72px.
- Headline maksimal dua baris; targetnya satu baris pada layar lebar.
- URL input dan tombol Inspect berada pada satu baris visual, namun tombol boleh
  turun di bawah input pada lebar yang lebih kecil.
- Preview memakai layout dua kolom: thumbnail di kiri, metadata di kanan.
- Quality dan Output berada berdampingan; Advanced menjadi action sekunder di
  sisi kanan.
- Tombol Download memiliki lebar penuh workbench agar menjadi penutup alur yang
  jelas.

### 4.2 Tablet: 721–1023px

- Pertahankan single-column workbench.
- Kurangi padding shell menjadi 24–40px.
- Preview tetap dua kolom jika lebar cukup; pindah menjadi satu kolom ketika
  thumbnail tidak lagi nyaman dibaca.
- Quality dan Output dapat tetap berdampingan selama masing-masing minimal
  220px.

### 4.3 Mobile: 320–720px

- Padding horizontal: 16px.
- Header tetap satu baris; tagline boleh mengecil atau disembunyikan di bawah
  380px, tetapi wordmark tidak boleh hilang.
- URL field selalu full width.
- Inspect link full width di baris berikutnya.
- Platform detected pill berada di bawah URL field, bukan menimpa isi input.
- Preview menjadi satu kolom: thumbnail di atas, metadata di bawah.
- Quality, Output, dan WhatsApp duration ditumpuk vertikal.
- Download video full width dengan tinggi minimal 48px.
- Footer status boleh membungkus menjadi dua baris.
- Tidak boleh ada horizontal scrolling.

## 5. Visual system

### 5.1 Color tokens

```css
:root {
  --color-paper: #F4F1EA;
  --color-surface: #FBF9F5;
  --color-surface-muted: #ECE8DF;
  --color-ink: #171714;
  --color-ink-soft: #5D5A54;
  --color-ink-faint: #8B867D;
  --color-line: #D7D1C6;
  --color-line-strong: #B8B1A5;
  --color-accent: #C8553D;
  --color-accent-soft: #F2D8D0;
  --color-success: #2E8B57;
  --color-warning: #B7791F;
  --color-danger: #B7463B;
}
```

Warna aksen hanya untuk platform detection, status penting, focus ring, dan
brand mark. Jangan mengubah seluruh tombol atau seluruh layar menjadi merah.

### 5.2 Typography

- UI font: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
  "Segoe UI", sans-serif`.
- Monospace untuk URL dan status teknis pendek:
  `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`.
- Headline desktop: 32px, weight 700, line-height 1.1, letter-spacing -0.03em.
- Headline mobile: 25px, weight 700, line-height 1.15, letter-spacing -0.02em.
- Body: 15px, line-height 1.5.
- Label: 13px, weight 600.
- Metadata: 13–14px, warna `--color-ink-soft`.
- Version dan status: 12px; boleh memakai monospace agar terasa utilitarian.

Hindari kombinasi display font dekoratif + gradient text. Kontras dan spacing
harus menjadi sumber karakter visual.

### 5.3 Shape, border, dan shadow

- Default radius: 8px.
- Radius tombol dan input: 8px.
- Radius thumbnail: 6px.
- Radius pill status: 999px hanya untuk status platform atau state kecil.
- Border standar: 1px solid `--color-line`.
- Border focus: 1px solid `--color-ink` dengan ring 3px
  `rgba(200, 85, 61, 0.18)`.
- Shadow hanya digunakan pada app shell/mockup window, bukan pada setiap card:
  `0 16px 40px rgba(23, 23, 20, 0.08)`.

## 6. Component specification

### 6.1 Header

Anatomi:

- mark vermilion berbentuk square 16×16px;
- wordmark `SnatchVid`, 17px / 700;
- separator vertical hairline;
- tagline `local media utility`;
- version `v0.1` di sisi kanan.

Header tidak memakai navigation menu karena halaman ini tidak punya destination
sekunder.

### 6.2 URL input

Label: `Video URL`  
Placeholder: `Paste a YouTube, TikTok, or Instagram link`  
Contoh value pada mockup: `https://youtube.com/watch?v=demo123`

Behavior:

- Field menerima URL lengkap dan dapat di-paste langsung.
- Deteksi platform dilakukan dari URL melalui pola yang sama dengan backend.
- Ketika URL dikenali, tampilkan status inline `YouTube detected`,
  `TikTok detected`, atau `Instagram detected`.
- Tombol clear berada di sisi kanan field ketika ada isi.
- Tombol `Inspect link` nonaktif ketika field kosong.
- Submit dengan Enter harus memiliki behavior yang sama dengan klik tombol.

### 6.3 Platform detected status

Status memakai pill kecil dengan icon platform dan label teks. Warna status
boleh mengikuti warna platform secara tipis, tetapi background tetap muted.

Contoh:

```text
[ YouTube icon ] YouTube detected
```

Jangan menjadikan badge platform sebagai dekorasi besar atau sebagai logo hero.

### 6.4 Media preview

Preview hanya muncul setelah `/api/info` mengembalikan data valid.

Konten wajib:

- thumbnail dari response `thumbnail`;
- platform display;
- title;
- uploader;
- duration.

Fallback thumbnail:

- background charcoal;
- satu play icon sederhana;
- garis waveform atau frame line sangat halus;
- tidak boleh memakai stock photo acak.

Thumbnail menggunakan `object-fit: cover` dan rasio 16:9. Judul maksimal dua
baris, lalu ellipsis bila lebih panjang.

### 6.5 Quality control

Label: `Quality`  
Default: `Best available`

Behavior:

- YouTube: isi dari format/resolusi yang tersedia di `/api/info`.
- TikTok dan Instagram: tetap `Best available`, karena engine mengambil
  kualitas terbaik platform.
- Jika user memilih angka, kirim angka piksel sebagai `quality` ke endpoint.
- Jangan menampilkan peringatan codec atau DASH di kontrol ini.

### 6.6 Output control

Label: `Output`  
Default: `Original`

Pilihan:

| UI label | API value | Keterangan user-facing |
|---|---|---|
| Original | `original` | File video sesuai sumber |
| WhatsApp Status | `wa_status` | Portrait, siap dipost ke status |
| MP3 Audio | `mp3` | Audio saja |

Saat `WhatsApp Status` dipilih, munculkan kontrol conditional:

```text
Duration: 15 sec   30 sec   60 sec
```

Default duration adalah 30 detik. Catatan cukup berupa `Portrait · ready to
post`; jangan menampilkan `H.264 + AAC` pada UI utama.

Jika `ffmpeg` tidak tersedia:

- opsi WhatsApp Status dan MP3 tetap terlihat agar user tahu fitur tersedia;
- opsi diberi disabled state;
- tampilkan alasan singkat: `Available after ffmpeg is installed`;
- tombol Original tetap aktif untuk platform yang dapat berjalan tanpa ffmpeg.

### 6.7 Advanced

`Advanced` adalah text link, bukan tombol besar. Versi pertama hanya boleh
membuka opsi yang benar-benar sudah didukung backend. Jangan membuat panel
kosong atau opsi fiktif demi terlihat lengkap.

### 6.8 Primary actions

Ada dua action dalam alur, tetapi hanya satu yang menjadi fokus per state:

| State | Primary action | Label |
|---|---|---|
| URL kosong / belum diperiksa | inspect | `Inspect link` |
| Preview siap | download | `Download video` |
| Loading | progress | `Inspecting…` / `Preparing download…` |
| Berhasil | follow-up | `Download another` |

Button style:

- background `--color-ink`;
- text `--color-paper`;
- tinggi minimal 48px;
- hover sedikit lebih terang, tanpa glow;
- disabled memakai opacity dan cursor yang jelas;
- icon download hanya dipakai pada `Download video`, bukan di semua tombol.

## 7. Interaction states

### State A — Empty

Tampilkan headline, supporting copy, input URL, tombol Inspect nonaktif, dan
footer status. Preview dan output controls belum terlihat.

### State B — URL detected

Setelah user mengisi URL yang valid secara lokal, tampilkan platform detected
status. Tombol Inspect menjadi aktif.

### State C — Inspecting

- Tombol menampilkan `Inspecting…`.
- Input dan clear button boleh dinonaktifkan selama request.
- Jangan menampilkan spinner besar di tengah layar; gunakan spinner kecil pada
  tombol atau progress line pendek.

### State D — Preview ready

Preview, quality, output, Advanced, dan Download video muncul. Fokus keyboard
berpindah ke area preview atau tombol Download tanpa memaksa scroll yang
mengejutkan.

### State E — Downloading

- Tombol berubah menjadi `Preparing download…` lalu `Downloading…` bila progress
  tersedia.
- Tampilkan progress bar tipis di bawah tombol atau di dalam tombol.
- Disable perubahan opsi selama download.

### State F — Success

Toast atau inline confirmation:

```text
Downloaded successfully
filename.mp4
```

Sediakan `Download another` untuk mengembalikan halaman ke state input tanpa
reload penuh.

### State G — Error

Pesan harus actionable dan tidak bocor sebagai stack trace.

| Kondisi | Copy |
|---|---|
| Platform tidak didukung | `That link is not supported yet. Try YouTube, TikTok, or Instagram.` |
| Info gagal diambil | `We couldn't read this link. Check the URL and try again.` |
| TikTok rate-limit | `TikTok is taking a moment. Retrying the link…` |
| ffmpeg hilang | `This format needs ffmpeg. Install it, then check again.` |
| Download gagal | `Download failed. Try again or choose Original output.` |

Untuk TikTok, frontend mengikuti retry maksimal 3 kali seperti yang dijelaskan
di dokumentasi teknis. Setelah retry habis, tampilkan error yang tenang dan
actionable.

## 8. Accessibility

- Semua input memiliki label yang terlihat, bukan hanya placeholder.
- Target sentuh minimal 44×44px; tombol utama minimal tinggi 48px.
- Kontras teks normal terhadap background minimal WCAG AA.
- Jangan menyampaikan status hanya lewat warna; gunakan label teks dan `aria-live`
  untuk status request/download.
- Thumbnail memiliki alt text dari title video.
- Focus ring harus terlihat pada keyboard navigation.
- Select controls memiliki label yang eksplisit dan urutan tab yang logis.
- Toast error tidak boleh hilang sebelum cukup lama untuk dibaca; sediakan
  fallback inline jika perlu.

## 9. Responsive behavior matrix

| Komponen | Desktop | Tablet | Mobile |
|---|---|---|---|
| Header | satu baris penuh | satu baris | tagline dapat disembunyikan |
| URL + Inspect | horizontal | horizontal bila muat | stack vertikal |
| Preview | thumbnail + metadata | dua kolom / fallback stack | satu kolom |
| Quality + Output | dua kolom | dua kolom bila muat | stack |
| Download | full workbench | full workbench | full width |
| Footer | satu baris | dapat wrap | dua baris |

Breakpoints bukan tujuan desain. Prioritasnya adalah menjaga label, URL,
preview, dan action tetap terbaca pada lebar aktual.

## 10. Backend integration notes

Frontend tetap vanilla HTML/CSS/JS dan tidak memerlukan perubahan arsitektur.

### On load

1. Panggil `GET /api/health`.
2. Tampilkan status singkat `Ready · ffmpeg available` atau status fallback.
3. Panggil `GET /api/platforms` dan `GET /api/output-types` bila data belum
   tersedia sebagai konfigurasi frontend.

### Inspect flow

1. Ambil value URL.
2. Jalankan `GET /api/info?url=<URL>`.
3. Render platform, title, uploader, duration, thumbnail, dan formats.
4. Set default quality ke `best` / `Best available`.
5. Aktifkan output controls dan Download video.

### Download flow

Gunakan:

```text
GET /api/download
  ?url=<URL>
  &quality=<best|pixel-height>
  &output=<original|wa_status|mp3>
  &wa_duration=<15|30|60>
```

Response binary diproses sebagai Blob dan dipicu sebagai download lokal.
Filename mengikuti `Content-Disposition` dari API. Jangan menampilkan technical
filename yang belum disanitasi di UI jika header tidak tersedia.

## 11. Implementation tokens

```css
:root {
  --shell-max: 1120px;
  --workbench-max: 760px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-7: 32px;
  --space-8: 40px;
  --space-9: 56px;
  --control-height: 48px;
  --radius-control: 8px;
  --radius-thumbnail: 6px;
  --transition-fast: 140ms ease;
  --transition-normal: 220ms ease;
}
```

Use spacing tokens for vertical rhythm. Jangan memperbaiki layout dengan
margin acak per komponen.

## 12. Definition of done

- [ ] First viewport langsung memperlihatkan tujuan dan URL input.
- [ ] User baru dapat menyelesaikan inspect + download dalam maksimal tiga klik
      setelah URL ditempel.
- [ ] Preview card hanya muncul setelah info valid.
- [ ] Tidak ada istilah codec/DASH/HEVC pada UI utama.
- [ ] Quality dan output memiliki default yang aman.
- [ ] Opsi yang membutuhkan ffmpeg memiliki disabled state dan alasan jelas.
- [ ] TikTok retry maksimal tiga kali dengan copy yang ramah.
- [ ] Progress dan success state terlihat tanpa membuka console.
- [ ] Error tidak menampilkan stack trace.
- [ ] Layout lolos uji pada 320px, 390px, 768px, 1024px, dan 1440px.
- [ ] Semua button, input, select, status, dan toast dapat diakses dengan
      keyboard dan screen reader.
- [ ] Tidak ada dekorasi yang tidak membantu tugas download.

## 13. Design rationale

Pilihan utama desain ini mengikuti karakter produk di PRD:

- **Single workbench:** mengurangi keputusan dan menjaga flow tetap pendek.
- **Preview sebelum download:** membuat user yakin file yang akan diambil sudah
  benar tanpa memaksa memahami metadata teknis.
- **Warm paper + charcoal:** membedakan SnatchVid dari dark/neon downloader
  generik, sambil tetap menjaga kontras dan kesan utilitas.
- **Satu aksen vermilion:** memberi identitas tanpa mengubah tool menjadi iklan.
- **Status system yang terlihat:** membantu user memahami readiness backend dan
  ffmpeg tanpa harus membuka terminal.
- **No fake completeness:** Advanced hanya muncul jika benar-benar punya fungsi;
  roadmap tidak dipaksakan masuk ke UI v1.

