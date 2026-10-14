"""Synthesize the gen-z cut's soundtrack, timed to genz.html (cuts, slams, sticker pops).

One continuous 140 BPM groove (no breaks, no per-slam hits) so the music sits under the cuts.
The drop starts on the name slam at 0.9 s and the track tape-stops into the final fade.
Run: python music.py  -> music.wav (44.1 kHz stereo, 26 s)
"""
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR, DUR = 44100, 26.0
N = int(SR * DUR)
L, R = np.zeros(N), np.zeros(N)
rng = np.random.default_rng(7)


def hz(note):  # MIDI -> Hz
    return 440 * 2 ** ((note - 69) / 12)


def filt(x, kind, f):
    return sosfilt(butter(2, f, kind, fs=SR, output="sos"), x)


def add(t, x, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i + len(x) <= 0:
        return
    x = x[: N - i] * gain
    L[i:i + len(x)] += x * (1 - max(pan, 0))
    R[i:i + len(x)] += x * (1 + min(pan, 0))


def env(n, a, d):  # attack/exp-decay envelope, seconds
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def kick(punch=1.0):
    n = int(.45 * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .16 * punch)
    x[:120] += rng.uniform(-1, 1, 120) * .6
    return np.tanh(x * 2.2)


def b808(note, dur, slide_to=None):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.full(n, hz(note))
    if slide_to is not None:
        f = hz(note) + (hz(slide_to) - hz(note)) * np.clip((t - dur * .9) / .06, 0, 1)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .004, dur * .8)
    return np.tanh(x * 3.5) * .8  # distorted sub: audible on laptop speakers


def snare():
    n = int(.22 * SR)
    nz = filt(rng.uniform(-1, 1, n), "highpass", 1800) * env(n, .001, .07)
    tone = np.sin(2 * np.pi * 190 * np.arange(n) / SR) * env(n, .001, .04)
    return np.tanh((nz + tone * .7) * 1.8)


def hat(open_=False):
    n = int((.18 if open_ else .05) * SR)
    return filt(rng.uniform(-1, 1, n), "highpass", 8000) * env(n, .0005, .06 if open_ else .012)


def riser(t0, t1, gain=.3):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR; p = tt / (t1 - t0)
    nz = rng.uniform(-1, 1, n)
    nz = filt(nz, "highpass", 600) * p ** 2
    sw = np.sin(2 * np.pi * np.cumsum(200 * 2 ** (p * 3.5)) / SR) * p ** 2 * .5
    add(t0, (nz + sw), gain)


def lead(t, note, dur=.12, gain=.12, pan=0.0):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = sum(2 * ((tt * hz(note) * d) % 1) - 1 for d in (1, 1.007, .993)) / 3  # detuned saws
    add(t, filt(x, "lowpass", 5000) * env(n, .002, dur * .4), gain, pan)


def pad(t, notes, dur, gain=.07):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = sum(2 * ((tt * hz(m) * d) % 1) - 1 for m in notes for d in (1, 1.004, .996))
    fade = np.minimum(1, tt / .06) * np.minimum(1, (dur - tt) / .06)
    add(t, filt(x, "lowpass", 1600) * fade, gain)


# ---- score: one continuous 140 BPM track, Fm - Db - Ab - Eb, drop on the name slam at 0.9 s ----
BEAT = 60 / 140; BAR = BEAT * 4; DROP = .9
CHORDS = [(29, (53, 56, 60)), (25, (49, 53, 56)), (32, (56, 60, 63)), (27, (51, 55, 58))]  # (808 root, pad notes)

pad(0, CHORDS[0][1], DROP, .05)  # intro: pad + soft riser into the drop
riser(.1, DROP, .18)
bar = 0
while DROP + bar * BAR < 25.4:
    t0 = DROP + bar * BAR
    root, notes = CHORDS[bar % 4]
    nxt = CHORDS[(bar + 1) % 4][0]
    pad(t0, notes, BAR)
    add(t0, b808(root, BAR, slide_to=nxt), .42)  # one sustained 808 per bar, gliding into the next chord
    for s16 in range(16):
        t = t0 + s16 * BEAT / 4
        if s16 in (0, 6, 10): add(t, kick(), .7)
        if s16 in (4, 12): add(t, snare(), .38)
        if s16 % 2 == 0 or bar >= 6: add(t, hat(), .1 if s16 % 4 else .14, pan=.3)
        if s16 == 14 and bar % 4 == 3: [add(t + i * BEAT / 16, hat(), .09, pan=.3) for i in range(4)]
        if s16 % 2 == 0: lead(t, notes[(s16 // 2) % 3] + (12 if s16 % 8 >= 4 else 0), BEAT / 2, .06, pan=-.4 if s16 % 4 else .4)
    bar += 1

# ---- master ----
mix = np.stack([L, R], 1)
mix = filt(mix.T, "highpass", 28).T  # keep sub, drop DC rumble
# tape stop on the last 0.6 s: resample with a slowing playhead
ts = int(25.4 * SR); tail = mix[ts:].copy(); m = len(tail)
pos = np.cumsum(np.linspace(1, 0, m)); pos = pos[pos < m - 1]
stop = np.stack([np.interp(pos, np.arange(m), tail[:, c]) for c in (0, 1)], 1) * np.linspace(1, 0, len(pos))[:, None]
mix[ts:] = 0; mix[ts:ts + len(stop)] = stop
mix /= np.percentile(np.abs(mix), 99.5)  # put loud peaks near 1, then soft-clip only the transients
mix = np.tanh(mix * 1.1)
mix *= .7 / np.abs(mix).max()  # about -3 dBFS peak, leaves headroom for AAC

with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("music.wav", round(len(mix) / SR, 2), "s")
