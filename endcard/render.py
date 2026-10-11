"""Render ustaad-endcard.html to an MP4, one frame at a time.

Run from the repo root:  python3 endcard/render.py
Every frame is a pure function of t, so the output is deterministic.
"""
import pathlib
import shutil
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
PAGE = ROOT.parent / "ustaad-endcard.html"
FRAMES = ROOT / "frames"
OUT = ROOT.parent / "renders" / "ustaad-endcard-1080p.mp4"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
W, H, FPS, DUR = 1920, 1080, 30, 5.0


def frames():
    FRAMES.exists() and shutil.rmtree(FRAMES)
    FRAMES.mkdir(parents=True)
    total = round(DUR * FPS)
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=[
            "--no-sandbox", "--force-color-profile=srgb", "--disable-lcd-text",
            "--hide-scrollbars", "--disable-gpu",
        ])
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        page.goto(PAGE.as_uri() + "?static=1")
        page.wait_for_function("window.READY !== undefined")
        page.evaluate("window.READY")
        for i in range(total):
            page.evaluate("t => window.renderFrame(t)", i / FPS)
            page.locator("#stage").screenshot(path=str(FRAMES / f"f{i:04d}.png"))
            if i % 30 == 0:
                print(f"  frame {i}/{total}", flush=True)
        browser.close()
    return total


def encode(total):
    OUT.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", str(FRAMES / "f%04d.png"),
        "-frames:v", str(total),
        "-c:v", "libx264", "-preset", "slow", "-crf", "16",
        "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
        "-colorspace", "bt709", "-movflags", "+faststart", "-an", str(OUT),
    ], check=True)
    print(f"wrote {OUT} ({OUT.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    n = frames()
    encode(n)
    if "--keep-frames" not in sys.argv:
        shutil.rmtree(FRAMES)
