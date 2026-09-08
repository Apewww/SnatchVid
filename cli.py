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

from core.downloader import (  # noqa: E402
    PLATFORMS,
    detect_platform,
    download,
    get_info,
    normalize_quality,
)


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
    except Exception as e:
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


def main():
    print_banner()

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