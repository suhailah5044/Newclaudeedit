"""Synthesised sound effects (no copyright): pop, whoosh, shutter, sparkle, ding, tick.

usage: python3 sfx2.py OUTDIR
"""
import numpy as np, wave, sys, os

SR = 48000
OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(3)


def save(name, x, peak=0.85):
    x = np.asarray(x, dtype=float)
    x = x / (abs(x).max() + 1e-9) * peak
    st = np.stack([x, x], 1)
    w = wave.open(f"{OUT}/{name}.wav", "wb")
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())


def t_(d):
    return np.arange(int(d * SR)) / SR


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, "same")


# pop: bubbly pitch-drop blip
t = t_(0.14)
f = 1100 * np.exp(-t * 18) + 380
save("pop", np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.002) * np.exp(-t / 0.04))

# whoosh: band-passed noise sweeping up then down
t = t_(0.45)
n = rng.standard_normal(len(t))
lo = lp(n, 6) - lp(n, 60)
env = np.sin(np.pi * t / t[-1]) ** 3
save("whoosh", lo * env, 0.7)

# shutter: two mechanical clicks
t = t_(0.18)
x = np.zeros(len(t))
for at, g in ((0.0, 1.0), (0.075, 0.7)):
    i = int(at * SR); k = int(0.025 * SR)
    c = rng.standard_normal(k) * np.exp(-np.arange(k) / SR / 0.005)
    x[i:i + k] += lp(c, 2) * g
save("shutter", x, 0.8)

# sparkle: quick bright bell arpeggio
t = t_(0.9)
x = np.zeros(len(t))
for k, fr in enumerate((2093, 2637, 3136, 4186)):
    i = int(k * 0.06 * SR); tt = t[: len(t) - i]
    x[i:] += (np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(2 * np.pi * fr * 2.01 * tt)) * np.exp(-tt / 0.18)
save("sparkle", x, 0.6)

# ding: two-tone bell (price / stock moments)
t = t_(1.0)
x = np.zeros(len(t))
for at, fr in ((0.0, 1318.5), (0.11, 1975.5)):
    i = int(at * SR); tt = t[: len(t) - i]
    x[i:] += sum(np.sin(2 * np.pi * fr * h * tt) * a for h, a in ((1, 1), (2.76, 0.25), (5.4, 0.08))) * np.exp(-tt / 0.3)
save("ding", x, 0.7)

# tick: soft UI tap for text appearing
t = t_(0.06)
save("tick", np.sin(2 * np.pi * 2400 * t) * np.exp(-t / 0.008), 0.6)
print("sfx ok")
