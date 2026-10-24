"""Split a two-ink riso image (red + black on paper) into two multiply layers.

usage: python sep.py in.png out_prefix [width] [red_gamma]
writes out_prefix-k.webp (black ink) and out_prefix-r.webp (red ink); white = no ink.
Stacked with mix-blend-mode: multiply over the paper colour they rebuild the print.
"""
import sys
import numpy as np
from PIL import Image

src, prefix = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 1800
im = Image.open(src).convert('RGB')
a = np.asarray(im).astype(np.float32) / 255
h, w, _ = a.shape
paper = np.median(a[:h // 8, :w // 8].reshape(-1, 3), axis=0)
# normalise against paper, so paper -> 1.0; lift near-paper tones to pure paper
# so the sheet's own texture/tint never shows as a rectangle on the page
n = np.clip(a / paper / 0.93, 0, 1)
# red ink barely darkens R; black darkens all. R channel = black coverage.
k = n[..., 0:1]
red = np.clip(n / np.maximum(k, 0.05), 0, 1)
red[..., 0] = 1.0
# optional 4th arg: >1 deepens pale red tints so light halftone reads stronger
if len(sys.argv) > 4:
    red = red ** float(sys.argv[4])
# fade the outer 4% to paper: no hard plate edge, kills edge artefacts
yy = np.minimum(np.arange(h), np.arange(h)[::-1])[:, None] / (h * 0.04)
xx = np.minimum(np.arange(w), np.arange(w)[::-1])[None, :] / (w * 0.04)
fade = np.clip(np.minimum(yy, xx), 0, 1)[..., None]
k = 1 - (1 - k) * fade
red = 1 - (1 - red) * fade
black = np.repeat(k, 3, axis=2)
for arr, tag in ((black, 'k'), (red, 'r')):
    out = Image.fromarray((arr * 255).astype(np.uint8))
    out = out.resize((width, round(width * h / w)), Image.LANCZOS)
    out.save(f'{prefix}-{tag}.webp', quality=82, method=6)
print('paper', (paper * 255).round().astype(int).tolist())
