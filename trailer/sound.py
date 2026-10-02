"""Temp score for the trailer, synthesised and locked to the beat timings.

Writes trailer/audio/temp-score.wav (48 kHz stereo). Every cue sits on the
same whole-second grid as the picture in trailer/src.html, so it can be laid
straight under a render of muneeb-trailer.html. It is a timing and dynamics
guide: swap the synthesised hits and whooshes for library sounds in the edit.

The background score lives in trailer/music.py and is mixed in under the
effects, ducking under each hit. Also writes audio/stem-fx.wav and
audio/stem-music.wav, level-matched, for the edit.

Run from the repo root: python3 trailer/sound.py   (needs numpy and scipy)

Cue sheet
  0.0   big impact + sub: the film opens on the cold open line slamming in;
        the drone bed starts
  1.0   two pulls with paper tears, left then right: frames come off the wall
  2.12  heavy slide to both sides and a low boom: the frame splits on the hero
  3,4   impacts: "I direct" / "stories."
  5.3   three hits at 5.30, 5.40, 5.52: "made", "with", "AI." land one by one
  6.0   whoosh right to left into the crowd; 7.0 softer whoosh into the stall
  8.0   nothing but the drone: "You bring the brief."
  9-12  impacts, with a push whoosh at 11 and a scatter whoosh at 12.38
  13    two seconds on the Video page: a swell and a whoosh from the right as the
        card slides in, hits at 13.45, 13.70, 13.95 as the words land, then a
        soft glide of air while the page scrolls through the films
  15    three panel whooshes
  16    letters rise with an upward sweep, soft hit at 16.32
  17    two words fly in from both edges, collide at 17.16
  18    a tick per letter as "Directed," flips in, punch at 18.52
  19    the heaviest impact and a sub drop on "not generated."
  20    impact, then a two second riser; 21 a pass per card as the three rows run,
        panned with each row, over beds of air that speed up into the cut
  22.0  hard cut to silence (the exhale)
  23    low boom, warm pad begins; 24 soft hit on the cut
  25    deal whoosh, five hover ticks
  26    dive riser
  27    end card chime, the pad resolves and rings out
"""
import pathlib
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
DUR = 30.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)
send_L = np.zeros(N)
send_R = np.zeros(N)


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def place(sig, at, gain=1.0, pan=0.0, verb=0.0):
    """Mix a mono signal in at time `at`, equal power pan -1..1, reverb send."""
    i = int(at * SR)
    sig = sig[: max(0, N - i)]
    a = (pan + 1) * np.pi / 4
    gl, gr = np.cos(a) * gain, np.sin(a) * gain
    L[i:i + len(sig)] += sig * gl
    R[i:i + len(sig)] += sig * gr
    if verb:
        send_L[i:i + len(sig)] += sig * gl * verb
        send_R[i:i + len(sig)] += sig * gr * verb


def filt(x, kind, f):
    sos = butter(4, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x)


def impact(size=1.0):
    d = 1.6 + size
    t = t_axis(d)
    f = 45 + 110 * np.exp(-t / 0.045)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.28 + 0.25 * size))
    thump = filt(rng.standard_normal(len(t)), "lowpass", 380) * np.exp(-t / 0.05) * 0.9
    click = filt(rng.standard_normal(len(t)), "highpass", 2500) * np.exp(-t / 0.004) * 0.35
    sub = np.sin(2 * np.pi * 38 * t) * np.exp(-t / (0.5 + 0.6 * size)) * 0.6 * size
    return (body + thump + click + sub) * (0.55 + 0.45 * size)


def whoosh(d, f0, f1, shape=0.5):
    """Band of noise whose centre glides f0 -> f1, peaking at `shape` of its length."""
    n = int(d * SR)
    x = rng.standard_normal(n)
    out = np.zeros(n)
    block = 240
    zi = np.zeros((2, 2))
    for s in range(0, n, block):
        p = s / n
        fc = f0 * (f1 / f0) ** p
        sos = butter(2, [fc / 1.6, min(fc * 1.6, SR / 2 - 100)], btype="bandpass", fs=SR, output="sos")
        out[s:s + block], zi = sosfilt(sos, x[s:s + block], zi=zi)
    t = np.arange(n) / n
    env = np.where(t < shape, (t / shape) ** 2, ((1 - t) / (1 - shape)) ** 1.5)
    return out * env * 1.4


def tear(d=0.32):
    n = int(d * SR)
    x = filt(rng.standard_normal(n), "bandpass", [900, 6000])
    grain = (rng.random(n // 240 + 1) ** 3).repeat(240)[:n]
    t = np.arange(n) / n
    return x * grain * np.minimum(1, t * 12) * (1 - t) ** 0.6 * 1.6


def riser(d, f0=120, f1=900):
    n = int(d * SR)
    t = np.arange(n) / SR
    p = t / d
    tone = sum(np.sin(2 * np.pi * np.cumsum(f0 * k * (f1 / f0) ** p) / SR) / k for k in (1, 2, 3))
    noise = whoosh(d, 300, 6000, shape=0.98)
    return (tone * 0.25 + noise * 0.8) * p ** 2


def tick():
    t = t_axis(0.12)
    return (np.sin(2 * np.pi * 2400 * t) + 0.4 * np.sin(2 * np.pi * 3600 * t)) * np.exp(-t / 0.018) * 0.35


def chime():
    t = t_axis(3.0)
    tones = [(880, 1.0), (1318.5, 0.5), (1760, 0.25), (2637, 0.12)]
    return sum(np.sin(2 * np.pi * f * t) * a * np.exp(-t / (1.4 / (1 + i))) for i, (f, a) in enumerate(tones)) * 0.22


def pad(d, notes, attack=1.2):
    t = t_axis(d)
    sig = np.zeros(len(t))
    for f in notes:
        for det in (-0.12, 0.0, 0.13):
            ph = rng.random() * 2 * np.pi
            sig += np.sin(2 * np.pi * (f + det) * t + ph) + 0.3 * np.sin(4 * np.pi * (f + det) * t + ph)
    sig = filt(sig, "lowpass", 1800) / (len(notes) * 3)
    env = np.minimum(1, t / attack)
    return sig * env


# ---- drone bed, 0.0 to 22.0, building, then cut dead ----
bed_d = 22.0
t = t_axis(bed_d)
bed = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 1) + 0.35 * np.sin(2 * np.pi * 110.3 * t + 2))
bed += 0.25 * filt(rng.standard_normal(len(t)), "lowpass", 160)
bed *= 10 ** ((-26 + 12 * (t / bed_d) ** 1.5) / 20) * np.minimum(1, t / 0.05)
place(bed, 0.0, gain=0.5)  # halved: the score's pad carries the low end now

# ---- cold open: the film starts on the slam ----
place(impact(1.3), 0.0, 1.0, 0, verb=0.5)
# two frames pulled off the wall, top left then bottom right, each with a paper tear
place(whoosh(0.4, 600, 2600, shape=0.7), 1.0, 0.5, -0.6, verb=0.2)
place(tear(), 1.12, 0.6, -0.6, verb=0.3)
place(whoosh(0.4, 600, 2600, shape=0.7), 1.1, 0.5, 0.6, verb=0.2)
place(tear(), 1.22, 0.6, 0.6, verb=0.3)
# the frame splits through the line: a heavy slide opening out to both sides, a low boom
# two independent noise layers, one per side, so the opening reads wide
place(whoosh(0.8, 1800, 160, shape=0.25), 2.12, 0.6, -0.5, verb=0.3)
place(whoosh(0.8, 1800, 160, shape=0.25), 2.12, 0.6, 0.5, verb=0.3)
t = t_axis(1.6)
place(np.sin(2 * np.pi * np.cumsum(70 * (36 / 70) ** (t / 1.6)) / SR) * np.exp(-t / 0.6), 2.12, 0.8, verb=0.3)

# ---- kinetic showcase ----
place(impact(0.9), 3.0, 0.9, verb=0.4)
place(impact(1.0), 4.0, 0.9, verb=0.5)
# 5: the banner pulls back under a soft swell; "made", "with", "AI." land one after another
place(whoosh(0.5, 900, 250, shape=0.2), 5.0, 0.35, verb=0.3)
place(impact(0.45), 5.30, 0.65, -0.3, verb=0.3)
place(impact(0.45), 5.40, 0.65, 0.0, verb=0.3)
place(impact(0.8), 5.52, 0.9, 0.3, verb=0.4)
place(whoosh(0.7, 2500, 400, shape=0.3), 6.0, 0.55, 0.6, verb=0.2)
place(whoosh(0.6, 1800, 300, shape=0.3), 7.0, 0.4, -0.5, verb=0.2)
place(impact(1.0), 9.0, 0.95, verb=0.5)
place(impact(0.7), 10.0, 0.8, verb=0.5)
place(impact(0.7), 11.0, 0.8, verb=0.4)
place(whoosh(0.8, 300, 1200, shape=0.4), 11.0, 0.4)
place(impact(0.8), 12.0, 0.85, verb=0.4)
place(whoosh(0.62, 600, 5000, shape=0.6), 12.38, 0.6, -0.4, verb=0.3)
# 13-15: two seconds on the Video page. The words land one after another with a
# hit each while the card slides in, then the page glides through the films.
place(whoosh(0.45, 5000, 600, shape=0.95), 13.0, 0.45, 0.4)
place(whoosh(0.6, 350, 1600, shape=0.45), 13.0, 0.35, 0.6, verb=0.2)
for k, at in enumerate((13.45, 13.70, 13.95)):
    place(impact(0.35 + 0.1 * k), at, 0.6 + 0.08 * k, -0.3, verb=0.35)
place(whoosh(0.95, 220, 900, shape=0.5), 14.05, 0.22, 0.4, verb=0.2)
for k in range(3):
    place(whoosh(0.4, 1500, 500, shape=0.35), 15.0 + k * 0.07, 0.4, -0.7 + 0.7 * k, verb=0.2)
# 16: "Cinematic" letters rise in sequence: an upward sweep, a soft hit as they settle
place(whoosh(0.45, 300, 2200, shape=0.8), 16.0, 0.45, verb=0.3)
place(impact(0.55), 16.32, 0.75, verb=0.4)
# 17: "brand" and "films." fly in from both edges and collide at 17.16
place(whoosh(0.16, 500, 2400, shape=0.97), 17.0, 0.55, -0.8)
place(whoosh(0.16, 500, 2400, shape=0.97), 17.0, 0.55, 0.8)
place(impact(1.05), 17.16, 1.0, verb=0.45)
# 18: "Directed," flips in letter by letter, then punches as the last letter lands
for i in range(9):
    place(tick(), 18.14 + i * 0.03, 0.45, -0.7 + 1.4 * i / 8, verb=0.2)
place(impact(1.1), 18.52, 1.0, verb=0.4)
place(impact(1.5), 19.0, 1.1, verb=0.6)
t = t_axis(1.4)
place(np.sin(2 * np.pi * np.cumsum(80 * (30 / 80) ** (t / 1.4)) / SR) * np.exp(-t / 0.7), 19.0, 0.8)
place(impact(1.1), 20.0, 1.0, verb=0.5)
place(riser(2.0), 20.0, 0.9, verb=0.2)
# 21s reel: three rows run left, right, left and accelerate into the cut.
# Same layout as REEL / REEL_ROWS in src.html: every card gets a pass whoosh at
# the moment its centre crosses the middle of the screen, panned the way its
# row travels; each row also carries a bed of air that speeds up with it.
REEL_H, REEL_GAP = 300, 30
REEL_ROWS = [  # (direction, distance, start x, cards: True = 4:5 portrait)
    (-1, 900, -140, [0, 1, 0, 1, 0, 1, 0]),
    (1, 1000, -1060, [0, 1, 0, 1, 0, 1, 0]),
    (-1, 1000, -100, [0, 1, 0, 1, 0, 1, 0]),
]
ramp = lambda u: 0.3 * u + 0.7 * u * u
row_pitch = [(2600, 900), (1900, 650), (1400, 450)]
for r, (d, dist, x0, cards) in enumerate(REEL_ROWS):
    # bed of air, louder and brighter as the row speeds up, swept across the field
    n_seg = 10
    for k in range(n_seg):
        u = (k + 0.5) / n_seg
        speed = 0.3 + 1.4 * u
        seg = whoosh(1.0 / n_seg + 0.04, 300 * speed + 200 * r, 900 * speed + 300, shape=0.5)
        place(seg, 21.0 + k / n_seg, 0.12 * speed, d * (-0.6 + 1.2 * u), verb=0.05)
    # one pass per card, timed to the frame
    x = x0
    for portrait in cards:
        w = REEL_H * 4 / 5 if portrait else REEL_H * 16 / 9
        c = x + w / 2
        for i in range(1000):
            u0, u1 = i / 1000, (i + 1) / 1000
            a = c + d * dist * ramp(u0) - 960
            b = c + d * dist * ramp(u1) - 960
            if a == 0 or (a < 0) != (b < 0):
                hi, lo = row_pitch[r]
                ws = whoosh(0.22, hi, lo, shape=0.45)
                place(ws, 21.0 + u0 - 0.22 * 0.45, 0.32 + 0.2 * u0, d * 0.35, verb=0.1)
                break
        x += w + REEL_GAP

# hard cut to silence at 22.0: nothing from the first half rings past it
cut = int(22.0 * SR)
L[cut:] = 0
R[cut:] = 0
send_L[cut:] = 0
send_R[cut:] = 0

# ---- resolve ----
t = t_axis(1.8)
place(np.sin(2 * np.pi * 42 * t) * np.exp(-t / 0.6) * 0.8, 23.0, 0.9, verb=0.4)
place(pad(7.0, [110, 164.8, 220, 277.2, 329.6], attack=1.5), 23.0, 0.55)
place(impact(0.35), 24.0, 0.55, verb=0.5)
place(whoosh(0.6, 400, 2500, shape=0.6), 25.0, 0.45, -0.3, verb=0.2)
for k in range(5):
    place(tick(), 25.5 + k * 0.1, 0.5, -0.8 + 0.4 * k, verb=0.4)
place(riser(0.75, 160, 640), 26.0, 0.6, verb=0.3)
place(chime(), 27.0, 0.8, 0.1, verb=0.7)

# ---- reverb send: synthetic stereo hall ----
ir_t = t_axis(2.2)
ir_l = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.45)
ir_r = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.45)
ir_l, ir_r = filt(ir_l, "lowpass", 5000), filt(ir_r, "lowpass", 5000)
ir_l /= np.sqrt(np.sum(ir_l ** 2)); ir_r /= np.sqrt(np.sum(ir_r ** 2))
L += fftconvolve(send_L, ir_l)[:N] * 0.6
R += fftconvolve(send_R, ir_r)[:N] * 0.6
L[cut:int(23.0 * SR)] = 0  # keep the exhale truly silent
R[cut:int(23.0 * SR)] = 0

# ---- background score (trailer/music.py), ducked under the effects ----
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from music import build_music

ML, MR = build_music(SR, N)
mpeak = max(np.max(np.abs(ML)), np.max(np.abs(MR)))
ML, MR = ML / mpeak, MR / mpeak
win = int(0.04 * SR)
fx_env = np.convolve(np.abs(L) + np.abs(R), np.ones(win) / win, mode="same")
fx_env /= np.percentile(fx_env, 99.5)
duck = 1 - 0.45 * np.clip(fx_env, 0, 1)
fxpeak = max(np.max(np.abs(L)), np.max(np.abs(R)))
MUSIC = 0.85 * fxpeak  # the score sits a few dB under the hits
music_L, music_R = ML * duck * MUSIC, MR * duck * MUSIC


def write(path, stereo):
    path.parent.mkdir(exist_ok=True)
    pcm = (np.clip(stereo, -1, 1).T * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# stems for the edit, level-matched to each other
stem_scale = 10 ** (-1 / 20) / max(fxpeak, np.max(np.abs(music_L)), np.max(np.abs(music_R)))
audio_dir = pathlib.Path(__file__).resolve().parent / "audio"
write(audio_dir / "stem-fx.wav", np.stack([L, R]) * stem_scale)
write(audio_dir / "stem-music.wav", np.stack([music_L, music_R]) * stem_scale)
L = L + music_L
R = R + music_R

# ---- master: high-pass rumble, soft clip, normalise, fade the last 0.4s ----
mix = np.stack([filt(L, "highpass", 28), filt(R, "highpass", 28)])
mix = np.tanh(mix / (np.max(np.abs(mix)) * 0.7))
mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
fade = int(0.4 * SR)
mix[:, -fade:] *= np.linspace(1, 0, fade)
# the exhale: a 10ms fade into 22.0 so the hard cut doesn't click, then true silence
f10 = int(0.01 * SR)
mix[:, cut - f10:cut] *= np.linspace(1, 0, f10)
mix[:, cut:int(23.0 * SR)] = 0

out = audio_dir / "temp-score.wav"
write(out, mix)
print(f"wrote {out} ({DUR:.0f}s, {SR} Hz stereo) and the fx / music stems")
