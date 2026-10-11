"""Derive the animation layers from the two supplied sign plates.

Run from the repo root:  python3 endcard/prep.py

The two plates are separate renders, so they differ slightly everywhere (brush
texture, the portrait, the border). Rectangular masks would therefore seam. So:

  * an ink matte is cut from the places where the plates genuinely disagree
    (the lettering), grown and closed so it swallows every outline and shadow;
  * the base plate is card_final with that matte filled from card_clean, which
    leaves final's portrait/border/ornaments untouched;
  * each ink layer is card_final carrying that matte as its alpha.

Base + the three ink layers at identity therefore reconstructs card_final
exactly, so the last frame of the animation is the finished sign.

The painted steam is cloned out of the base as well, because the animation
redraws it as moving SVG wisps.
"""
import json
import pathlib

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
ASSETS = ROOT / "assets"
W, H = 1920, 1080

# Where each element lives, in final-plate pixels. The cuts sit in the bare
# maroon gaps between the three elements and must not overlap: a layer that
# reached into its neighbour would paint a sliver of it ahead of its own cue.
BANDS = {"ustaad": (0, 505), "samosay": (505, 694), "ribbon": (694, H)}
STEAM_BOX = (630, 815, 110, 372)          # x0, x1, y0, y1
ORNAMENT_BOTTOM = (1072, 1545, 820)       # x0, x1, y_top
PANEL = (812, 1824, 252, 884)
FEATHER = 16                              # the matte fades out at the panel limits   # right edge stops short of the border foliage             # x0, x1, y0, y1


def load():
    ASSETS.mkdir(exist_ok=True)
    out = []
    for name in ("card_clean", "card_final"):
        im = Image.open(SRC / f"{name}_src.png").convert("RGB").resize((W, H), Image.LANCZOS)
        out.append(np.asarray(im).astype(np.float32))
    return out


def ramp(n, lo, hi, width):
    """1 inside [lo, hi], falling smoothly to 0 over `width` outside it."""
    i = np.arange(n, dtype=np.float32)
    up = np.clip((i - (lo - width)) / width, 0, 1)
    down = np.clip(((hi + width) - i) / width, 0, 1)
    v = np.minimum(up, down)
    return v * v * (3 - 2 * v)


def ink_matte(clean, final):
    d = np.abs(clean - final).max(axis=2)
    d = np.asarray(Image.fromarray(d.astype(np.uint8)).filter(ImageFilter.MedianFilter(5))).astype(np.float32)

    px0, px1, py0, py1 = PANEL
    panel = np.zeros((H, W), bool)
    panel[py0:py1, px0:px1] = True
    ox0, ox1, oy = ORNAMENT_BOTTOM
    panel[oy:, ox0:ox1] = False     # the lower floral ornament is in both plates

    strong = ndi.binary_opening((d > 55) & panel, ndi.generate_binary_structure(2, 2), iterations=2)
    lab, n = ndi.label(strong, np.ones((3, 3)))
    sizes = ndi.sum(strong, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:][sizes > 1200] = True
    core = keep[lab]

    near = ndi.binary_dilation(core, ndi.generate_binary_structure(2, 2), iterations=16)
    matte = (((d > 22) & near) | core) & panel
    matte = ndi.binary_closing(matte, ndi.generate_binary_structure(2, 2), iterations=6)
    matte = ndi.binary_dilation(matte, ndi.generate_binary_structure(2, 2), iterations=6)
    matte = ndi.binary_fill_holes(matte) & panel
    soft = Image.fromarray((matte * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))
    alpha = np.asarray(soft).astype(np.float32) / 255.0

    # Cutting the matte dead at the panel limits leaves a hairline where the two
    # plates disagree, so fade it out instead.
    edge = (ramp(W, px0, px1, FEATHER)[None, :] * ramp(H, py0, py1, FEATHER)[:, None])
    skirt = 1.0 - (ramp(W, ox0, ox1, FEATHER) [None, :] * ramp(H, oy, H + FEATHER, FEATHER)[:, None])
    return alpha * edge * skirt


def declutter_steam(base):
    """Clone flat panel texture over the painted steam so it can be reanimated."""
    x0, x1, y0, y1 = STEAM_BOX
    box = base[y0:y1, x0:x1].copy()
    r, g, b = box[..., 0], box[..., 1], box[..., 2]
    h, w = r.shape
    yy = np.arange(h)[:, None] + y0
    xx = np.arange(w)[None, :] + x0

    orange = (r > 175) & (g > 110) & ((r - b) > 110)
    dark = (r + g + b) < 140
    hot = (orange | dark) & (yy >= 278)          # the samosa only ever sits below this
    samosa = ndi.binary_closing(hot, np.ones((9, 9)))
    lab, n = ndi.label(samosa, np.ones((3, 3)))
    if n:
        samosa = lab == int(np.argmax(ndi.sum(samosa, lab, range(1, n + 1)))) + 1
    samosa = ndi.binary_dilation(ndi.binary_fill_holes(samosa), np.ones((3, 3)), iterations=2)
    # Along the samosa's lit right edge the grown mask swallows real steam.
    tight = ndi.binary_dilation(hot, np.ones((3, 3)), iterations=1)
    samosa = np.where((xx >= 724) & (yy >= 288), tight, samosa)

    score = np.clip((ndi.median_filter(np.minimum(g, b), size=3) - 30.0) / 50.0, 0, 1)
    score[samosa] = 0
    sm = ndi.binary_opening(score > 0.09, np.ones((3, 3)))
    lab, n = ndi.label(sm, np.ones((3, 3)))
    sizes = ndi.sum(sm, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:][sizes > 60] = True
    sm = ndi.binary_closing(ndi.binary_dilation(keep[lab], np.ones((3, 3)), iterations=5), np.ones((9, 9)))
    sm = sm & ~samosa

    shift = 210                                   # empty panel to the right of the steam
    donor = base[y0:y1, x0 + shift:x1 + shift].copy()
    bg = ~sm & ~samosa
    donor += box[bg].mean(axis=0) - donor[bg].mean(axis=0)

    a = np.asarray(Image.fromarray((sm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4.0))).astype(np.float32) / 255.0
    a = np.clip((a - 0.12) / 0.5, 0, 1)
    a[samosa] = 0.0
    base[y0:y1, x0:x1] = box * (1 - a[..., None]) + donor * a[..., None]
    return base


def find_studs(final):
    mx, mn = final.max(axis=2), final.min(axis=2)
    cand = ndi.binary_fill_holes(
        ndi.binary_closing((mx - mn < 48) & (mx > 115) & (mn > 95), np.ones((3, 3)), iterations=2)
    )
    lab, n = ndi.label(cand, np.ones((3, 3)))
    sizes = ndi.sum(cand, lab, range(1, n + 1))
    studs = []
    for i, sl in enumerate(ndi.find_objects(lab)):
        area = sizes[i]
        bh, bw = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if not (160 < area < 2600) or not bw or not bh:
            continue
        if not (0.68 < bw / bh < 1.45) or area / (bw * bh) < 0.62 or not (16 < bw < 62):
            continue
        studs.append({
            "x": round((sl[1].start + sl[1].stop) / 2, 1),
            "y": round((sl[0].start + sl[0].stop) / 2, 1),
            "r": round(max(bw, bh) / 2, 1),
        })
    # clockwise, starting from the top-left corner
    corner = np.arctan2(40 - H / 2, 40 - W / 2)
    studs.sort(key=lambda s: (np.arctan2(s["y"] - H / 2, s["x"] - W / 2) - corner) % (2 * np.pi))
    return studs


def main():
    clean, final = load()
    alpha = ink_matte(clean, final)
    base = final * (1 - alpha[..., None]) + clean * alpha[..., None]
    base = declutter_steam(base)
    Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).save(ASSETS / "plate_base.png")

    layers = {}
    for name, (y0, y1) in BANDS.items():
        band = np.zeros((H, W), np.float32)
        band[y0:y1] = 1.0
        a = alpha * band
        ys, xs = np.where(a > 0.02)
        bx0, by0 = max(0, xs.min() - 3), max(0, ys.min() - 3)
        bx1, by1 = min(W - 1, xs.max() + 3), min(H - 1, ys.max() + 3)
        box = (slice(by0, by1 + 1), slice(bx0, bx1 + 1))
        aa = a[box][..., None]
        # Source-over with a partial alpha would leave a trace of the base plate
        # behind, so the colour is pre-corrected to land back on card_final:
        #   ink*a + base*(1-a) == final,  with base = final*(1-a) + clean*a.
        colour = final[box] * (2 - aa) - clean[box] * (1 - aa)
        rgba = np.zeros((by1 - by0 + 1, bx1 - bx0 + 1, 4), np.uint8)
        rgba[..., :3] = np.clip(colour, 0, 255).astype(np.uint8)
        rgba[..., 3] = np.clip(a[box] * 255, 0, 255).astype(np.uint8)
        Image.fromarray(rgba, "RGBA").save(ASSETS / f"ink_{name}.png")
        layers[name] = {"x": int(bx0), "y": int(by0), "w": int(bx1 - bx0 + 1), "h": int(by1 - by0 + 1)}

    studs = find_studs(final)
    (ASSETS / "layers.json").write_text(json.dumps({"layers": layers, "studs": studs}, indent=1))

    recon = base.copy()
    for name, m in layers.items():
        sp = np.asarray(Image.open(ASSETS / f"ink_{name}.png")).astype(np.float32)
        a = sp[..., 3:4] / 255.0
        sl = (slice(m["y"], m["y"] + m["h"]), slice(m["x"], m["x"] + m["w"]))
        recon[sl] = recon[sl] * (1 - a) + sp[..., :3] * a
    err = np.abs(recon - final).max(axis=2)
    print(f"layers: {', '.join(layers)}   studs: {len(studs)}")
    print(f"reconstruction vs card_final: mean {err.mean():.3f}, max {err.max():.0f}, "
          f"{int((err > 6).sum())} px off by more than 6")


if __name__ == "__main__":
    main()
