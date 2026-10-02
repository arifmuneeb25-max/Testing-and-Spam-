"""Background score for the trailer, synthesised and locked to the edit.

120 BPM, so every whole-second cut lands on a beat; one bar is two seconds.

  0-22s  A minor build, Am F C G per bar, ending on E for tension:
         string pad (detuned saws) whose filter opens across the build,
         an eighth-note bass pulse, kick from the first frame, hats from 9s,
         a backbeat from 12s, a sixteenth-note arpeggio from 13s and a snare
         roll from 20s into the cut. Drums drop out at 8-9s under the brief.
  22-23s silence (the exhale).
  23-30s resolves to A major: a warm pad and a slow piano motif under the
         closing shots and the end card.

build_music(sr, n, seed) returns the left and right channels.
"""
import numpy as np
from scipy.signal import butter, sosfilt, sawtooth

BEAT = 0.5          # 120 BPM
BAR = 2.0
CUT = 22.0          # hard cut to silence
CLOSE = 23.0        # the close begins

# chords as MIDI notes, one per two-second bar
AM = [45, 48, 52, 57]
F = [41, 45, 48, 53]
C = [48, 52, 55, 60]
G = [43, 47, 50, 55]
E = [40, 44, 47, 52]
BARS = [AM, F, C, G, AM, F, C, G, AM, F, E]
ROOTS = [33, 29, 36, 31, 33, 29, 36, 31, 33, 29, 28]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def build_music(sr, n, seed=11):
    rng = np.random.default_rng(seed)
    L = np.zeros(n)
    R = np.zeros(n)

    def filt(x, kind, f, order=2):
        return sosfilt(butter(order, f, btype=kind, fs=sr, output="sos"), x)

    def tax(d):
        return np.arange(int(d * sr)) / sr

    def put(sig, at, gain=1.0, pan=0.0):
        i = int(round(at * sr))
        if i >= n:
            return
        sig = sig[: n - i]
        a = (pan + 1) * np.pi / 4
        L[i:i + len(sig)] += sig * np.cos(a) * gain
        R[i:i + len(sig)] += sig * np.sin(a) * gain

    # ---- string pad: one chord per bar, filter opening across the build ----
    for b, chord in enumerate(BARS):
        t0 = b * BAR
        d = BAR + 0.3
        t = tax(d)
        cutoff = 700 + 1500 * (b / (len(BARS) - 1)) ** 1.3
        for side, det in ((-0.6, -0.11), (0.6, 0.13)):
            sig = np.zeros(len(t))
            for m in chord:
                f = hz(m + 12)
                sig += sawtooth(2 * np.pi * (f + det * f / 100) * t + rng.random() * 6.28)
            sig = filt(sig / len(chord), "lowpass", cutoff)
            env = np.minimum(1, t / 0.12) * np.minimum(1, np.maximum(0, (d - t) / 0.3))
            put(sig * env, t0, 0.22 + 0.1 * b / len(BARS), side)

    # ---- bass: eighth-note pulse on the root, octave lift on the last eighth of each beat pair ----
    for b, root in enumerate(ROOTS):
        for k in range(8):
            at = b * BAR + k * BAR / 8
            if at >= CUT:
                break
            m = root + (12 if k % 4 == 3 else 0)
            t = tax(0.24)
            sig = sawtooth(2 * np.pi * hz(m) * t) + 0.5 * np.sin(2 * np.pi * hz(m) * t)
            sig = filt(sig, "lowpass", 320) * np.exp(-t / 0.13)
            build = 0.55 + 0.45 * at / CUT
            put(sig, at, 0.42 * build, 0)

    # ---- drums ----
    def kick():
        t = tax(0.32)
        f = 42 + 70 * np.exp(-t / 0.03)
        body = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-t / 0.12)
        click = filt(rng.standard_normal(len(t)), "highpass", 3000) * np.exp(-t / 0.003) * 0.25
        return body + click

    def hat(decay=0.03):
        t = tax(0.12)
        return filt(rng.standard_normal(len(t)), "highpass", 7000) * np.exp(-t / decay)

    def snare():
        t = tax(0.25)
        noise = filt(rng.standard_normal(len(t)), "bandpass", [1500, 6000]) * np.exp(-t / 0.09)
        body = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
        return noise * 0.8 + body * 0.5

    def drums_off(at):
        return 8.0 <= at < 9.0 or at >= CUT

    # kick: whole seconds for the first four, then every beat
    for i in range(int(CUT / BEAT)):
        at = i * BEAT
        if drums_off(at) or (at < 4.0 and i % 2):
            continue
        put(kick(), at, 0.55, 0)
    # hats on the off-eighths from 9s, sixteenths from 18s
    for i in range(int(CUT / 0.125)):
        at = i * 0.125
        if at < 9.0 or drums_off(at):
            continue
        if i % 2 == 1 and (i // 2) % 2 == 1:
            put(hat(), at, 0.12, 0.35)
        elif at >= 18.0 and i % 2 == 1:
            put(hat(0.02), at, 0.07, -0.35)
    # backbeat from 12s to the roll
    for i in range(int(12.0 / BEAT), int(20.0 / BEAT)):
        if i % 2 == 1:
            put(snare(), i * BEAT, 0.3, 0)
    # snare roll into the cut: sixteenths, then thirty-seconds for the last half second
    at = 20.0
    while at < CUT:
        step = 0.0625 if at >= 21.5 else 0.125
        put(snare(), at, 0.12 + 0.28 * (at - 20.0) / 2.0, 0)
        at += step

    # ---- arpeggio: sixteenths through the chord tones from 13s, filter opening ----
    i = 0
    at = 13.0
    while at < CUT:
        b = int(at // BAR)
        chord = BARS[min(b, len(BARS) - 1)]
        m = chord[1 + i % 3] + 24 + (12 if (i // 3) % 2 else 0)
        t = tax(0.16)
        sig = sawtooth(2 * np.pi * hz(m) * t, 0.5) * np.exp(-t / 0.07)
        sig = filt(sig, "lowpass", 1500 + 3500 * (at - 13.0) / (CUT - 13.0))
        put(sig, at, 0.1 + 0.06 * (at - 13.0) / (CUT - 13.0), -0.5 if i % 2 else 0.5)
        i += 1
        at += 0.125

    # ---- the close: A major, a warm pad and a slow piano motif ----
    d = 30.0 - CLOSE
    t = tax(d)
    pad = np.zeros(len(t))
    for m in (45, 52, 57, 61, 64, 71):
        for det in (-0.08, 0.09):
            pad += np.sin(2 * np.pi * (hz(m) + det) * t + rng.random() * 6.28)
            pad += 0.35 * np.sin(2 * np.pi * 2 * (hz(m) + det) * t)
    pad = filt(pad / 12, "lowpass", 1600) * np.minimum(1, t / 1.2)
    put(pad, CLOSE, 0.32, 0)

    def piano(m, d=3.0):
        t = tax(d)
        f = hz(m)
        sig = sum(np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (0.9 + 0.8 * k)) / k
                  for k in range(1, 7))
        return sig * np.minimum(1, t / 0.004)

    for m, at, g in ((76, 23.0, 0.5), (73, 23.5, 0.45), (69, 24.0, 0.45), (71, 25.0, 0.4),
                     (73, 25.5, 0.4), (76, 27.0, 0.5), (81, 27.0, 0.25), (69, 28.5, 0.35)):
        put(piano(m), at, g, 0.15)

    # hard cut at 22.0 with a 10ms fade, silence until the close
    i0, i1, f10 = int(CUT * sr), int(CLOSE * sr), int(0.01 * sr)
    for ch in (L, R):
        ch[i0 - f10:i0] *= np.linspace(1, 0, f10)
        ch[i0:i1] = 0
    return L, R
