"""Temp score for the trailer, synthesised and locked to the beat timings.

Writes trailer/audio/temp-score.wav (48 kHz stereo). Every cue sits on the
same whole-second grid as the picture in trailer/src.html, so it can be laid
straight under a render of muneeb-trailer.html. It is a timing and dynamics
guide: swap the synthesised hits and whooshes for library sounds in the edit.

Run from the repo root: python3 trailer/sound.py   (needs numpy and scipy)

Cue sheet
  0.0   silence; 0.4 a low swell as the wall of work surfaces
  1.0   big impact + sub: the cold open line slams in; drone bed starts
  2.0   two pulls with paper tears, left then right: frames come off the wall
  3.12  heavy slide to both sides and a low boom: the frame splits on the hero
  4,5   impacts: "I direct" / "stories."
  6.3   snap hit: "made with AI." locks together
  7.0   whoosh right to left into the crowd; 8.0 softer whoosh into the stall
  9.0   nothing but the drone: "You bring the brief."
  10-13 impacts, with a push whoosh at 12 and a scatter whoosh at 13.38
  14    reverse swell into a small hit at 14.5: the letters reassemble
  15    three panel whooshes
  16-19 escalating impacts, sub drop on "not generated."
  20    impact, then a two second riser; 21 the cascade whooshes
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


# ---- drone bed, 1.0 to 22.0, building, then cut dead ----
bed_d = 21.0
t = t_axis(bed_d)
bed = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.4 * t + 1) + 0.35 * np.sin(2 * np.pi * 110.3 * t + 2))
bed += 0.25 * filt(rng.standard_normal(len(t)), "lowpass", 160)
bed *= 10 ** ((-26 + 12 * (t / bed_d) ** 1.5) / 20) * np.minimum(1, t / 0.4)
place(bed, 1.0, gain=1.0)

# ---- cold open ----
# the wall surfaces out of the dark: a low swell of air
place(whoosh(0.6, 120, 700, shape=0.95), 0.4, 0.45, verb=0.3)
place(impact(1.3), 1.0, 1.0, 0, verb=0.5)
# two frames pulled off the wall, top left then bottom right, each with a paper tear
place(whoosh(0.4, 600, 2600, shape=0.7), 2.0, 0.5, -0.6, verb=0.2)
place(tear(), 2.12, 0.6, -0.6, verb=0.3)
place(whoosh(0.4, 600, 2600, shape=0.7), 2.1, 0.5, 0.6, verb=0.2)
place(tear(), 2.22, 0.6, 0.6, verb=0.3)
# the frame splits through the line: a heavy slide opening out to both sides, a low boom
# two independent noise layers, one per side, so the opening reads wide
place(whoosh(0.8, 1800, 160, shape=0.25), 3.12, 0.6, -0.5, verb=0.3)
place(whoosh(0.8, 1800, 160, shape=0.25), 3.12, 0.6, 0.5, verb=0.3)
t = t_axis(1.6)
place(np.sin(2 * np.pi * np.cumsum(70 * (36 / 70) ** (t / 1.6)) / SR) * np.exp(-t / 0.6), 3.12, 0.8, verb=0.3)

# ---- kinetic showcase ----
place(impact(0.9), 4.0, 0.9, verb=0.4)
place(impact(1.0), 5.0, 0.9, verb=0.5)
place(whoosh(0.24, 200, 1500, shape=0.95), 6.06, 0.6)
place(impact(0.5), 6.30, 0.7, verb=0.3)
place(whoosh(0.7, 2500, 400, shape=0.3), 7.0, 0.55, 0.6, verb=0.2)
place(whoosh(0.6, 1800, 300, shape=0.3), 8.0, 0.4, -0.5, verb=0.2)
place(impact(1.0), 10.0, 0.95, verb=0.5)
place(impact(0.7), 11.0, 0.8, verb=0.5)
place(impact(0.7), 12.0, 0.8, verb=0.4)
place(whoosh(0.8, 300, 1200, shape=0.4), 12.0, 0.4)
place(impact(0.8), 13.0, 0.85, verb=0.4)
place(whoosh(0.62, 600, 5000, shape=0.6), 13.38, 0.6, -0.4, verb=0.3)
place(whoosh(0.5, 5000, 600, shape=0.95), 14.0, 0.5, 0.4)
place(impact(0.45), 14.5, 0.7, verb=0.4)
for k in range(3):
    place(whoosh(0.4, 1500, 500, shape=0.35), 15.0 + k * 0.07, 0.4, -0.7 + 0.7 * k, verb=0.2)
place(impact(0.8), 16.0, 0.85, verb=0.4)
place(impact(1.0), 17.0, 0.95, verb=0.4)
place(impact(1.1), 18.0, 1.0, verb=0.4)
place(impact(1.5), 19.0, 1.1, verb=0.6)
t = t_axis(1.4)
place(np.sin(2 * np.pi * np.cumsum(80 * (30 / 80) ** (t / 1.4)) / SR) * np.exp(-t / 0.7), 19.0, 0.8)
place(impact(1.1), 20.0, 1.0, verb=0.5)
place(riser(2.0), 20.0, 0.9, verb=0.2)
for k in range(8):
    place(whoosh(0.35, 2200, 500, shape=0.4), 21.0 + k * 0.075, 0.35, 0.8 - 0.2 * k, verb=0.1)

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

out = pathlib.Path(__file__).resolve().parent / "audio" / "temp-score.wav"
out.parent.mkdir(exist_ok=True)
pcm = (mix.T * 32767).astype("<i2")
with wave.open(str(out), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"wrote {out} ({DUR:.0f}s, {SR} Hz stereo)")
