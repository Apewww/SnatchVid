#!/usr/bin/env python3
"""
SnatchVid CLI — download video YouTube/TikTok/Instagram dari terminal.

Usage:
    python cli.py <URL> [--quality 720] [--output downloads] [--info]
    python cli.py <URL1> <URL2> ...          # batch download
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Biar import core/ bisa jalan dari mana pun
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Pastikan output utf-8 aman di terminal Windows
if sys.platform == "win32":
    try:
        sys.stdin.reconfigure(encoding="utf-8-sig", errors="replace")
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from core.downloader import (  # noqa: E402
    PLATFORMS,
    detect_platform,
    download,
    get_info,
    normalize_quality,
)
from core.metrics import record_download, record_inspection  # noqa: E402


def quality_type(value: str) -> str:
    """Argparse type: validasi kualitas (best atau angka piksel berapa pun)."""
    try:
        return normalize_quality(value)
    except ValueError as e:
        raise argparse.ArgumentTypeError(str(e))


class Color:
    """ANSI colors — auto-disable kalau bukan TTY."""
    enabled = sys.stdout.isatty()

    @classmethod
    def _wrap(cls, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if cls.enabled else text

    @classmethod
    def green(cls, t): return cls._wrap("32", t)
    @classmethod
    def red(cls, t): return cls._wrap("31", t)
    @classmethod
    def yellow(cls, t): return cls._wrap("33", t)
    @classmethod
    def cyan(cls, t): return cls._wrap("36", t)
    @classmethod
    def bold(cls, t): return cls._wrap("1", t)
    @classmethod
    def dim(cls, t): return cls._wrap("2", t)


def print_banner():
    print(Color.bold(Color.cyan("""
   ╔══════════════════════════════╗
   ║   S N A T C H V I D          ║
   ║   TikTok · Instagram · YT    ║
   ╚══════════════════════════════╝""")))
    print(Color.dim("   by RaflyLabs — demo build\n"))


def progress_hook(d):
    """Callback progress yt-dlp → print bar sederhana."""
    if d.get("status") == "downloading":
        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
        done = d.get("downloaded_bytes", 0)
        pct = (done / total * 100) if total else 0
        speed = d.get("speed") or 0
        eta = d.get("eta") or 0
        bar_len = 24
        filled = int(bar_len * pct / 100)
        bar = "█" * filled + "░" * (bar_len - filled)
        speed_s = f"{speed/1e6:.1f}" if speed else "?"
        print(
            f"\r  {Color.cyan(bar)} {pct:5.1f}%  "
            f"{done/1e6:6.2f}/{total/1e6:6.2f} MB  "
            f"{Color.dim(speed_s + ' MB/s')}  ETA {eta}s",
            end="", flush=True,
        )
    elif d.get("status") == "finished":
        print()


def handle_url(url: str, args) -> int:
    platform = detect_platform(url)
    if not platform:
        print(Color.red(f"  ✗ URL tidak didukung: {url}"))
        print(Color.dim("    Support: YouTube, TikTok, Instagram."))
        return 1

    conf = PLATFORMS[platform]
    print(f"\n  {conf['emoji']} {Color.bold(conf['name'])} — {Color.dim(url[:80])}")

    if args.info:
        try:
            info = get_info(url)
            record_inspection(platform)
        except Exception as e:
            print(Color.red(f"  ✗ Gagal ambil info: {e}"))
            return 1
        print(f"  {'─' * 56}")
        print(f"  {Color.bold(info.title)}")
        print(f"  Uploader : {info.uploader or '-'}")
        print(f"  Durasi   : {info.duration}")
        print(f"  Thumbnail: {info.thumbnail or '-'}")
        if info.formats:
            qs = ", ".join(f"{f['height']}p" for f in info.formats[:6])
            print(f"  Resolusi : {qs}")
        return 0

    try:
        result = download(
            url,
            outdir=args.output,
            quality=args.quality,
            progress_hook=progress_hook,
            output_type=args.output_type,
            wa_duration=args.wa_duration,
        )
        record_download(
            platform=result.get("platform", platform),
            duration_sec=result.get("duration_sec", 0),
            output_type=args.output_type,
            success=True,
        )
    except Exception as e:
        record_download(
            platform=platform,
            duration_sec=0,
            output_type=args.output_type,
            success=False,
        )
        print(Color.red(f"  ✗ Download gagal: {e}"))
        return 1

    converted = {
        "wa_status": "📱 WhatsApp Status (H.264+AAC)",
        "mp3": "🎵 MP3 Audio",
    }.get(result.get("converted"))
    suffix = f"  {Color.green(converted)}" if converted else ""
    size = result["size"] / 1e6
    print(
        f"  {Color.green('✔ Selesai!')} {result['title']}.{result['ext']} "
        f"{Color.dim(f'({size:.1f} MB)')}{suffix}"
    )
    print(Color.dim(f"  → {result['path']}"))
    return 0


def interactive_wizard() -> int:
    """Mode interaktif TUI: jalankan download tanpa perlu menghafal parameter."""
    print(Color.bold("  === MODE INTERAKTIF ==="))
    print(Color.dim("  Ketik 'q' atau 'exit' kapan saja untuk keluar.\n"))

    while True:
        try:
            url = input(Color.bold("[?] Masukkan URL video (YouTube / TikTok / Instagram): ")).strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nSelesai. Sampai jumpa!")
            return 0

        if not url:
            continue
        if url.lower() in ("q", "exit", "quit"):
            print("\nSampai jumpa!")
            return 0

        platform = detect_platform(url)
        if not platform:
            print(Color.red("  ✗ URL tidak didukung. Coba link YouTube, TikTok, atau Instagram."))
            continue

        conf = PLATFORMS[platform]
        print(f"  {conf['emoji']} Terdeteksi: {Color.bold(conf['name'])}")
        print(Color.dim("  [*] Mengambil informasi video..."))

        try:
            info = get_info(url)
            record_inspection(platform)
        except Exception as e:
            print(Color.red(f"  ✗ Gagal membaca link: {e}"))
            continue

        print(f"\n  {'─' * 50}")
        print(f"  {Color.bold('Judul')}   : {info.title}")
        print(f"  {Color.bold('Creator')} : {info.uploader or '-'}")
        print(f"  {Color.bold('Durasi')}  : {info.duration}")
        print(f"  {'─' * 50}")

        # Menu Format
        print(Color.bold("\n[?] Pilih Format Output:"))
        print("  [1] Original - Kualitas Terbaik (Best Quality)")
        print("  [2] Pilih Resolusi Khusus (1080p, 720p, 480p, 360p)")
        print("  [3] WhatsApp Status - 9:16 Portrait (H.264 + AAC)")
        print("  [4] MP3 Audio - Hanya Suara")

        fmt_choice = input(Color.bold("Pilihan [1-4, default: 1]: ")).strip() or "1"
        quality = "best"
        output_type = "original"
        wa_duration = 30

        if fmt_choice == "2":
            output_type = "original"
            formats = info.formats or []
            heights = [str(f.get("height")) for f in formats if f.get("height")]
            unique_h = list(dict.fromkeys(heights))
            if not unique_h:
                unique_h = ["1080", "720", "480", "360"]
            print(Color.bold("\nPilih resolusi yang diinginkan:"))
            for idx, h in enumerate(unique_h[:6], 1):
                print(f"  [{idx}] {h}p")
            q_choice = input(Color.bold(f"Pilihan [1-{len(unique_h[:6])}, default: 1]: ")).strip() or "1"
            try:
                q_idx = int(q_choice) - 1
                if 0 <= q_idx < len(unique_h):
                    quality = unique_h[q_idx]
            except ValueError:
                quality = "best"
        elif fmt_choice == "3":
            output_type = "wa_status"
            print(Color.bold("\nPilih batas durasi WhatsApp Status:"))
            print("  [1] 30 detik (Standar status WA)")
            print("  [2] 15 detik (Story singkat)")
            print("  [3] 60 detik (Panjang)")
            wa_choice = input(Color.bold("Pilihan [1-3, default: 1]: ")).strip() or "1"
            wa_map = {"1": 30, "2": 15, "3": 60}
            wa_duration = wa_map.get(wa_choice, 30)
        elif fmt_choice == "4":
            output_type = "mp3"

        # Folder tujuan
        out_dir = input(Color.bold("\n[?] Simpan ke folder [default: downloads/]: ")).strip() or "downloads"
        Path(out_dir).mkdir(parents=True, exist_ok=True)

        print(Color.dim("\n  [*] Mengunduh media..."))
        try:
            result = download(
                url,
                outdir=out_dir,
                quality=quality,
                progress_hook=progress_hook,
                output_type=output_type,
                wa_duration=wa_duration,
            )
            record_download(
                platform=result.get("platform", platform),
                duration_sec=result.get("duration_sec", info.duration_sec or 0),
                output_type=output_type,
                success=True,
            )
            converted = {
                "wa_status": "📱 WhatsApp Status (H.264+AAC)",
                "mp3": "🎵 MP3 Audio",
            }.get(result.get("converted"))
            suffix = f"  {Color.green(converted)}" if converted else ""
            size = result["size"] / 1e6
            print(
                f"\n  {Color.green('✔ Selesai!')} {result['title']}.{result['ext']} "
                f"{Color.dim(f'({size:.1f} MB)')}{suffix}"
            )
            print(Color.dim(f"  → {result['path']}"))
        except Exception as e:
            record_download(
                platform=platform,
                duration_sec=0,
                output_type=output_type,
                success=False,
            )
            print(Color.red(f"\n  ✗ Download gagal: {e}"))

        # Loop question
        try:
            lagi = input(Color.bold("\n[?] Ingin download video lain? (Y/n): ")).strip().lower()
            if lagi in ("n", "no", "tidak"):
                print("\nSelesai. File tersimpan di folder " + Color.bold(out_dir))
                return 0
        except (KeyboardInterrupt, EOFError):
            print("\n\nSampai jumpa!")
            return 0


def main():
    print_banner()

    # Jika dijalankan tanpa parameter (misal klik run_cli.bat), masuk mode interaktif
    if len(sys.argv) == 1:
        return interactive_wizard()

    parser = argparse.ArgumentParser(
        description="SnatchVid — download video TikTok/Instagram/YouTube",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Contoh:\n"
               "  python cli.py https://www.tiktok.com/@user/video/123\n"
               "  python cli.py \"https://youtu.be/abc\" -q 1080\n"
               "  python cli.py https://www.instagram.com/reel/xyz/ --info\n",
    )
    parser.add_argument("urls", nargs="+", help="URL video (satu atau banyak)")
    parser.add_argument(
        "-q", "--quality", default="720", type=quality_type,
        help="Kualitas video: 'best' atau tinggi piksel berapa pun (default: 720). Hanya dipakai untuk YouTube.",
    )
    parser.add_argument(
        "-o", "--output", default="downloads",
        help="Folder output (default: downloads/)",
    )
    parser.add_argument(
        "-i", "--info", action="store_true",
        help="Hanya tampilkan info video, tanpa download",
    )
    parser.add_argument(
        "-t", "--output-type", default="original",
        choices=["original", "wa_status", "mp3"],
        help="Format output: original | wa_status (siap post WA) | mp3 (audio)",
    )
    parser.add_argument(
        "--wa-duration", type=int, default=30,
        help="Max durasi detik untuk --output-type wa_status (default: 30 = batas status WA)",
    )
    args = parser.parse_args()

    Path(args.output).mkdir(parents=True, exist_ok=True)

    failed = 0
    for url in args.urls:
        failed += handle_url(url, args)

    print(f"\n  {Color.bold('Ringkasan:')} {len(args.urls) - failed}/{len(args.urls)} berhasil")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())