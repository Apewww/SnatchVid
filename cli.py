#!/usr/bin/env python3
"""
SnatchVid CLI — download video YouTube/TikTok/Instagram/Twitter/Facebook dari terminal.

Usage:
    python cli.py <URL> [--quality 720] [--output downloads] [--info]
    python cli.py <URL1> <URL2> ...          # batch download
"""

from __future__ import annotations

import argparse
import os
import subprocess
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
   ║   Universal Media Downloader ║
   ╚══════════════════════════════╝""")))
    print(Color.dim("   by Rafly Anggara Putra — demo build\n"))


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
        print(Color.dim("    Support: YouTube, TikTok, Instagram, Twitter / X, Facebook."))
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


def read_key() -> str:
    """
    Membaca satu event tombol keyboard (cross-platform).
    Returns: 'UP', 'DOWN', 'LEFT', 'RIGHT', 'ENTER', 'ESC', atau karakter string.
    """
    if sys.platform == "win32":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):
            ch2 = msvcrt.getwch()
            if ch2 == "H":
                return "UP"
            if ch2 == "P":
                return "DOWN"
            if ch2 == "K":
                return "LEFT"
            if ch2 == "M":
                return "RIGHT"
            return "UNKNOWN"
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x1b":
            return "ESC"
        if ch == "\x03":
            raise KeyboardInterrupt
        if ch in ("k", "w", "K", "W"):
            return "UP"
        if ch in ("j", "s", "J", "S"):
            return "DOWN"
        return ch
    else:
        import termios
        import tty
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch1 = sys.stdin.read(1)
            if ch1 == "\x1b":
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "A":
                        return "UP"
                    if ch3 == "B":
                        return "DOWN"
                    if ch3 == "C":
                        return "RIGHT"
                    if ch3 == "D":
                        return "LEFT"
                return "ESC"
            if ch1 in ("\r", "\n"):
                return "ENTER"
            if ch1 == "\x03":
                raise KeyboardInterrupt
            if ch1 in ("k", "w", "K", "W"):
                return "UP"
            if ch1 in ("j", "s", "J", "S"):
                return "DOWN"
            return ch1
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def select_menu(prompt: str, options: list[str], default_index: int = 0) -> int:
    """
    Menu interaktif panah Atas/Bawah (↑ / ↓) + Enter (gaya OpenCode CLI / Gemini CLI).
    Fallback otomatis ke input nomor jika bukan interactive terminal (TTY).
    """
    if not options:
        return 0

    if not sys.stdout.isatty() or not sys.stdin.isatty():
        print(f"\n{Color.bold('[?]')} {Color.bold(prompt)}:")
        for idx, opt in enumerate(options, 1):
            print(f"  [{idx}] {opt}")
        choice = input(Color.bold(f"Pilihan [1-{len(options)}, default: {default_index+1}]: ")).strip()
        try:
            i = int(choice) - 1
            if 0 <= i < len(options):
                return i
        except ValueError:
            pass
        return default_index

    selected = default_index % len(options)
    total = len(options)

    # Cetak prompt header
    print(f"\n{Color.bold(Color.cyan('?'))} {Color.bold(prompt)} {Color.dim('(Gunakan ↑/↓ lalu tekan Enter)')}")

    # Sembunyikan cursor teks
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    def print_options():
        for i, opt in enumerate(options):
            if i == selected:
                sys.stdout.write(f"\033[2K  {Color.bold(Color.cyan('❯ ●'))} {Color.bold(Color.cyan(opt))}\n")
            else:
                sys.stdout.write(f"\033[2K    {Color.dim('○')} {Color.dim(opt)}\n")
        sys.stdout.flush()

    print_options()

    try:
        while True:
            try:
                k = read_key()
            except KeyboardInterrupt:
                sys.stdout.write(f"\033[{total}A\r")
                for _ in range(total):
                    sys.stdout.write("\033[2K\n")
                sys.stdout.write(f"\033[{total}A\r")
                sys.stdout.flush()
                raise

            if k == "UP":
                selected = (selected - 1) % total
            elif k == "DOWN":
                selected = (selected + 1) % total
            elif k == "ENTER":
                break
            elif k in ("ESC", "q"):
                break

            # Naik kembali ke awal baris opsi lalu render ulang
            sys.stdout.write(f"\033[{total}A\r")
            print_options()

        # Setelah Enter: ganti prompt dan daftar opsi dengan 1 baris ringkasan bersih
        sys.stdout.write(f"\033[{total + 1}A\r\033[2K")
        sys.stdout.write(f"{Color.bold(Color.green('✔'))} {Color.bold(prompt)}: {Color.cyan(options[selected])}\n")
        for _ in range(total):
            sys.stdout.write("\033[2K\n")
        sys.stdout.write(f"\033[{total}A\r")
        sys.stdout.flush()

    finally:
        # Kembalikan text cursor
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    return selected


def interactive_wizard() -> int:
    """Mode interaktif TUI: jalankan download tanpa perlu mengetik opsi (navigasi ↑ / ↓ + Enter)."""
    print(Color.bold("  === MODE INTERAKTIF ==="))
    print(Color.dim("  Navigasi opsi dengan tombol panah [↑ / ↓] dan tekan [Enter]."))
    print(Color.dim("  Ketik 'q' pada input URL kapan saja untuk keluar.\n"))

    while True:
        try:
            url = input(f"{Color.bold(Color.cyan('[?]'))} {Color.bold('Masukkan URL video')} {Color.dim('(YouTube / TikTok / IG / X / FB)')}: ").strip()
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
            print(Color.red("  ✗ URL tidak didukung. Coba link YouTube, TikTok, Instagram, Twitter/X, atau Facebook.\n"))
            continue

        conf = PLATFORMS[platform]
        print(f"  {conf['emoji']} Terdeteksi: {Color.bold(conf['name'])}")
        print(Color.dim("  [*] Mengambil informasi video..."))

        try:
            info = get_info(url)
            record_inspection(platform)
        except Exception as e:
            print(Color.red(f"  ✗ Gagal membaca link: {e}\n"))
            continue

        print(f"\n  {'─' * 52}")
        print(f"  {Color.bold('Judul')}   : {info.title}")
        print(f"  {Color.bold('Creator')} : {info.uploader or '-'}")
        print(f"  {Color.bold('Durasi')}  : {info.duration}")
        print(f"  {'─' * 52}")

        # Menu 1: Format Output (Navigasi Up/Down)
        format_options = [
            "Original — Kualitas Terbaik (Best Quality)",
            "Pilih Resolusi Khusus (1080p, 720p, 480p, 360p)",
            "WhatsApp Status — 9:16 Portrait (H.264 + AAC)",
            "MP3 Audio — Ekstrak Audio Saja",
        ]
        fmt_idx = select_menu("Pilih Format Output", format_options, default_index=0)

        quality = "best"
        output_type = "original"
        wa_duration = 30

        if fmt_idx == 1:
            # Resolusi Khusus
            output_type = "original"
            formats = info.formats or []
            heights = [str(f.get("height")) for f in formats if f.get("height")]
            unique_h = list(dict.fromkeys(heights))
            if not unique_h:
                unique_h = ["1080", "720", "480", "360"]
            res_options = [f"{h}p" for h in unique_h[:6]]
            res_idx = select_menu("Pilih Resolusi yang Diinginkan", res_options, default_index=0)
            quality = unique_h[res_idx]

        elif fmt_idx == 2:
            # WhatsApp Status
            output_type = "wa_status"
            wa_options = [
                "30 detik (Standar batas status WhatsApp)",
                "15 detik (Story singkat)",
                "60 detik (Durasi penuh / panjang)",
            ]
            wa_idx = select_menu("Pilih Batas Durasi WhatsApp Status", wa_options, default_index=0)
            wa_duration = [30, 15, 60][wa_idx]

        elif fmt_idx == 3:
            # MP3 Audio
            output_type = "mp3"

        # Menu 2: Folder Tujuan (Navigasi Up/Down)
        folder_options = [
            "downloads/ (Folder Default)",
            "./ (Folder Saat Ini)",
            "Ketik folder kustom...",
        ]
        folder_idx = select_menu("Simpan ke Folder", folder_options, default_index=0)
        if folder_idx == 0:
            out_dir = "downloads"
        elif folder_idx == 1:
            out_dir = "."
        else:
            try:
                out_dir = input(Color.bold("  Masukkan nama folder tujuan: ")).strip() or "downloads"
            except (KeyboardInterrupt, EOFError):
                out_dir = "downloads"

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

        # Menu 3: Tindakan Selanjutnya (Navigasi Up/Down)
        next_actions = [
            "Download video lain",
            "Buka folder di File Explorer",
            "Keluar dari SnatchVid",
        ]
        action_idx = select_menu("Tindakan Selanjutnya", next_actions, default_index=0)

        if action_idx == 1:
            try:
                folder_full = str(Path(out_dir).resolve())
                if sys.platform == "win32":
                    os.startfile(folder_full)
                elif sys.platform == "darwin":
                    subprocess.run(["open", folder_full])
                else:
                    subprocess.run(["xdg-open", folder_full])
                print(f"  Folder terbuka: {Color.bold(out_dir)}")
            except Exception as e:
                print(Color.dim(f"  Tidak dapat membuka file manager: {e}"))

            sub_idx = select_menu("Lanjutkan", ["Download video lain", "Keluar dari SnatchVid"], default_index=0)
            if sub_idx == 1:
                print("\nSelesai. Sampai jumpa!")
                return 0

        elif action_idx == 2:
            print("\nSelesai. Sampai jumpa!")
            return 0


def main():
    print_banner()

    # Jika dijalankan tanpa parameter (misal klik run_cli.bat), masuk mode interaktif
    if len(sys.argv) == 1:
        return interactive_wizard()

    parser = argparse.ArgumentParser(
        description="SnatchVid — download video YouTube, TikTok, Instagram, Twitter/X, dan Facebook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Contoh:\n"
               "  python cli.py https://www.tiktok.com/@user/video/123\n"
               "  python cli.py \"https://youtu.be/abc\" -q 1080\n"
               "  python cli.py https://www.instagram.com/reel/xyz/ --info\n"
               "  python cli.py https://x.com/user/status/123456\n"
               "  python cli.py https://www.facebook.com/reel/123456\n",
    )
    parser.add_argument("urls", nargs="+", help="URL video (satu atau banyak)")
    parser.add_argument(
        "-q", "--quality", default="720", type=quality_type,
        help="Kualitas video: 'best' atau tinggi piksel berapa pun (default: 720). Dipakai untuk YouTube, Twitter/X, & Facebook.",
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