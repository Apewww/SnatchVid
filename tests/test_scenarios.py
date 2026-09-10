import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import core.downloader as dl
import core.convert as cv

def test_windows_filename_sanitization():
    print("=== TEST 1: Windows Filename Sanitization ===")
    t1 = dl._clean_title({'title': 'CON'})
    t2 = dl._clean_title({'title': 'Test video with trailing dots...'})
    t3 = dl._clean_title({'title': 'My: Awesome / Video ? * \\" < > | 🎵'})
    print("CON ->", t1)
    print("Trailing dots ->", t2)
    print("Illegal chars ->", t3)
    assert t1 == "CON_file", f"Expected CON_file, got {t1}"
    assert t2 == "Test video with trailing dots", f"Expected stripped dots, got {t2}"
    assert all(c not in t3 for c in [':', '/', '?', '*', '"', '<', '>', '|']), f"Illegal chars found in {t3}"
    print("TEST 1 PASSED")

def test_silent_video_conversion():
    print("\n=== TEST 2: Silent Video Conversion ===")
    tmp = Path(tempfile.mkdtemp())
    silent_mp4 = tmp / "silent.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=blue:s=320x240:d=1",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(silent_mp4)
    ], capture_output=True)

    # to_wa_status must succeed without crash
    wa_out = cv.to_wa_status(silent_mp4, tmp / "silent_wa.mp4")
    assert wa_out.exists() and wa_out.stat().st_size > 0, "WA status file was not created"
    print("Silent video to_wa_status: SUCCESS")

    # to_mp3 must raise clean ValueError
    try:
        cv.to_mp3(silent_mp4, tmp / "silent.mp3")
        assert False, "to_mp3 should have raised ValueError on silent video"
    except ValueError as e:
        print("Silent video to_mp3 clean error caught:", e)
    print("TEST 2 PASSED")
    shutil.rmtree(tmp, ignore_errors=True)

def test_friendly_error_translation():
    print("\n=== TEST 3: Friendly Error Translation ===")
    e_bot = RuntimeError("Sign in to confirm you're not a bot.")
    e_tt = RuntimeError("Unable to extract universal data for rehydration")
    e_ig = RuntimeError("Please log in to access this content")
    e_del = RuntimeError("This video has been removed by the user")

    msg_bot = dl._translate_error(e_bot, "youtube")
    msg_tt = dl._translate_error(e_tt, "tiktok")
    msg_ig = dl._translate_error(e_ig, "instagram")
    msg_del = dl._translate_error(e_del, "youtube")

    print("Bot ->", msg_bot)
    print("TikTok ->", msg_tt)
    print("Instagram ->", msg_ig)
    print("Removed ->", msg_del)

    assert "verifikasi login" in msg_bot or "anti-bot" in msg_bot
    assert "TikTok membatasi akses sementara" in msg_tt
    assert "Instagram membatasi akses" in msg_ig
    assert "tidak tersedia" in msg_del
    print("TEST 3 PASSED")

def test_default_opts():
    print("\n=== TEST 4: Default Opts & Fallbacks ===")
    opts = dl.default_opts()
    assert opts.get("retries") == 5
    assert opts.get("fragment_retries") == 10
    assert "ejs:github" in opts.get("remote_components", [])
    
    yt_opts = dl.platform_opts("youtube")
    assert "extractor_args" in yt_opts
    assert "player_client" in yt_opts["extractor_args"]["youtube"]
    assert "mweb" in yt_opts["extractor_args"]["youtube"]["player_client"]
    assert "android" in yt_opts["extractor_args"]["youtube"]["player_client"]
    print("TEST 4 PASSED")


def test_env_config():
    print("\n=== TEST 5: Environment Variables (.env) ===")
    from api.main import ROOT_DIR, ENV_FILE
    assert ROOT_DIR.exists()
    assert ENV_FILE.name == ".env"
    print("TEST 5 PASSED")

def test_twitter_facebook_support():
    print("\n=== TEST 6: Twitter / X & Facebook Platform Support ===")
    import core.metrics as mt

    # 1. URL Detection
    assert dl.detect_platform("https://twitter.com/OpenAI/status/123456789") == "twitter"
    assert dl.detect_platform("https://x.com/elonmusk/status/987654321") == "twitter"
    assert dl.detect_platform("https://www.facebook.com/reel/1234567890") == "facebook"
    assert dl.detect_platform("https://fb.watch/nXYZ12345/") == "facebook"
    assert dl.detect_platform("https://www.facebook.com/watch/?v=123456789") == "facebook"
    print("URL Detection: PASSED")

    # 2. Platform Opts
    tw_opts = dl.platform_opts("twitter", quality="720")
    fb_opts = dl.platform_opts("facebook", quality="1080")
    assert tw_opts.get("merge_output_format") == "mp4"
    assert fb_opts.get("merge_output_format") == "mp4"
    assert "height<=720" in tw_opts.get("format", "")
    assert "height<=1080" in fb_opts.get("format", "")
    print("Platform Opts: PASSED")

    # 3. Error Translation
    e_tw = RuntimeError("This tweet is from a private account.")
    e_fb = RuntimeError("You must log in to continue.")
    msg_tw = dl._translate_error(e_tw, "twitter")
    msg_fb = dl._translate_error(e_fb, "facebook")
    assert "Twitter / X membatasi akses" in msg_tw
    assert "Facebook membatasi akses" in msg_fb
    print("Error Translation: PASSED")

    # 4. Metrics Schema
    metrics = mt.get_metrics_summary()
    assert "twitter" in metrics.get("platforms", {})
    assert "facebook" in metrics.get("platforms", {})
    print("Metrics Platforms: PASSED")
    print("TEST 6 PASSED")


if __name__ == "__main__":
    test_windows_filename_sanitization()
    test_silent_video_conversion()
    test_friendly_error_translation()
    test_default_opts()
    test_env_config()
    test_twitter_facebook_support()
    print("\nALL SCENARIOS VERIFIED SUCCESSFULLY!")
