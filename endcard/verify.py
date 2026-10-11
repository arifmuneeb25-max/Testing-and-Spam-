"""Step through the rendered frames and check the things that can go wrong.

Run from the repo root:  python3 endcard/verify.py
Needs endcard/frames, i.e. render.py run with --keep-frames.
"""
import json
import pathlib

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent
FRAMES = ROOT / "frames"
ASSETS = ROOT / "assets"
FPS, W, H = 30, 1920, 1080
CAM_TO = 1.04
LAYOUT = json.loads((ASSETS / "layers.json").read_text())
BEATS = {"ustaad": 0.60, "samosay": 1.30, "ribbon": 2.30}
BANDS = {"ustaad": (0, 505), "samosay": (505, 694), "ribbon": (694, H)}


def frame(t):
    return np.asarray(Image.open(FRAMES / f"f{round(t * FPS):04d}.png").convert("RGB")).astype(np.float32)


def camera(img, scale):
    """What the frame should look like at this camera scale."""
    cw, ch = W / scale, H / scale
    box = ((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2)
    return np.asarray(Image.fromarray(img.astype(np.uint8)).resize((W, H), Image.LANCZOS, box=box)).astype(np.float32)


def through_the_same_browser(png, scale):
    """card_final put through the identical CSS transform, so the comparison is
    not measuring the difference between Chromium's resampler and Pillow's."""
    from playwright.sync_api import sync_playwright
    out = ROOT / "frames" / "_reference.png"
    html = ROOT / "frames" / "_reference.html"
    html.write_text(
        "<style>html,body{margin:0;background:#000}"
        f"#s{{width:{W}px;height:{H}px;overflow:hidden;position:relative}}"
        f"img{{position:absolute;inset:0;width:{W}px;height:{H}px;"
        f"transform:scale({scale});transform-origin:{W // 2}px {H // 2}px}}</style>"
        f'<div id="s"><img src="{png.as_uri()}"></div>')
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                              args=["--no-sandbox", "--force-color-profile=srgb", "--disable-gpu",
                                    "--hide-scrollbars"])
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto(html.as_uri())
        pg.wait_for_timeout(400)
        pg.locator("#s").screenshot(path=str(out))
        b.close()
    return np.asarray(Image.open(out).convert("RGB")).astype(np.float32)


def report(label, err, tol):
    bad = int((err > tol).sum())
    flag = "ok  " if bad < 4000 else "FAIL"
    print(f"  {flag} {label}: mean {err.mean():.2f}, p99.9 {np.percentile(err, 99.9):.0f}, "
          f"{bad} px over {tol}")
    return bad < 4000


ok = True
final = np.asarray(Image.open(ROOT / "src" / "card_final_src.png").convert("RGB")
                   .resize((W, H), Image.LANCZOS)).astype(np.float32)
plate = np.asarray(Image.open(ASSETS / "plate_base.png").convert("RGB")).astype(np.float32)

print("last frame vs card_final at 1.04")
ref_png = ROOT / "frames" / "_card_final_1080.png"
Image.fromarray(final.astype(np.uint8)).save(ref_png)
ref = through_the_same_browser(ref_png, CAM_TO)
err = np.abs(frame(149 / FPS) - ref).max(axis=2)
report("whole frame (the steam was redrawn, so it differs here by design)", err, 26)
steam = np.zeros((H, W), bool)
steam[int((110 - H / 2) / CAM_TO + H / 2) - 8:int((372 - H / 2) / CAM_TO + H / 2) + 8,
      int((630 - W / 2) / CAM_TO + W / 2) - 8:int((815 - W / 2) / CAM_TO + W / 2) + 8] = True
e2 = err.copy(); e2[steam] = 0
ok &= report("everything but the steam", e2, 26)

print("\nnothing is painted before its cue")
for name, cue in BEATS.items():
    m = LAYOUT["layers"][name]
    y0, y1 = BANDS[name]                      # the element's own rows, not its sprite box
    sl = (slice(max(m["y"], y0), min(m["y"] + m["h"], y1)), slice(m["x"], m["x"] + m["w"]))
    t = cue - 1 / FPS
    err = np.abs(frame(t) - camera(plate, 1 + 0.04 * (-(np.cos(np.pi * t / 5) - 1) / 2)))[sl].max(axis=2)
    ok &= report(f"{name} region at t={t:.2f} is still bare", err, 30)

print("\nthe reveals are continuous (no jump between neighbouring frames)")
prev, worst = frame(0), []
for i in range(1, 150):
    cur = frame(i / FPS)
    worst.append((np.abs(cur - prev).mean(), i))
    prev = cur
worst.sort(reverse=True)
for d, i in worst[:3]:
    print(f"  frame {i - 1}->{i} (t={i / FPS:.2f}s): mean step {d:.2f}")
ok &= worst[0][0] < 9.0
print(f"  {'ok  ' if worst[0][0] < 9.0 else 'FAIL'} largest frame-to-frame step {worst[0][0]:.2f}")

print("\nmask edges: no hard vertical seam inside a half-revealed word")
for name, t in (("ustaad", 1.05), ("samosay", 1.80), ("ribbon", 2.70)):
    m = LAYOUT["layers"][name]
    band = frame(t)[m["y"]:m["y"] + m["h"], m["x"]:m["x"] + m["w"]].mean(axis=2)
    col = np.abs(np.diff(band, axis=1)).mean(axis=0)
    print(f"  {name} t={t}: sharpest column step {col.max():.1f} "
          f"(painted lettering itself steps ~{np.percentile(col, 99):.1f})")

print("\nresult:", "PASS" if ok else "FAIL")
