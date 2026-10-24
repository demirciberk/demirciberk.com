"""Turn a photo into a red ASCII / dot portrait in two ink layers (portrait-k / portrait-r).

usage: python ascii.py photo.jpg out_prefix [ascii|dots] [cols]
White = no ink; the page multiplies both layers onto the paper colour, like sep.py output.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

src, prefix = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else 'ascii'
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 92
W, H = 1400, 1045
RED, BLACK = (229, 67, 42), (27, 25, 22)
RAMP = " .:-=+*#%@"

photo = ImageOps.exif_transpose(Image.open(src)).convert('L')
m = round(min(photo.size) * 0.015)          # ID photos carry a thin border line
photo = photo.crop((m, m, photo.width - m, photo.height - m))
photo = ImageOps.autocontrast(photo, cutoff=1)
ph = H - 40                       # portrait height on the canvas
pw = round(photo.width * ph / photo.height)
x0, y0 = (W - pw) // 2, H - ph    # sit on the bottom edge, shoulders run off the page

cw = pw / cols                    # cell width
ch = cw / 0.56 if mode == 'ascii' else cw * 0.866
rows = int(ph / ch)
lum = np.asarray(photo.resize((cols, rows), Image.BOX), dtype=np.float32) / 255
# light skin stays sparse, hair and features carry the ink
dark = np.clip((1 - lum - 0.18) / 0.7, 0, 1) ** 1.25

red = Image.new('RGB', (W, H), 'white')
blk = Image.new('RGB', (W, H), 'white')
dr, db = ImageDraw.Draw(red), ImageDraw.Draw(blk)
rng = np.random.default_rng(7)
font = ImageFont.truetype('C:/Windows/Fonts/consolab.ttf', round(ch * 0.98)) if mode == 'ascii' else None

for r in range(rows):
    for c in range(cols):
        d = float(dark[r, c])
        if d < 0.06:
            continue
        x = x0 + c * cw + (cw / 2 if mode == 'dots' and r % 2 else 0)
        y = y0 + r * ch
        if mode == 'ascii':
            dr.text((x, y), RAMP[min(len(RAMP) - 1, int(d * len(RAMP)))], font=font, fill=RED)
            # a sparse black pass on the darkest cells (eyes, hair) for the second ink
            if d > 0.8 and rng.random() < 0.3:
                db.text((x, y), RAMP[-1 - int(rng.random() * 3)], font=font, fill=BLACK)
        else:
            rad = cw * 0.5 * d ** 0.6
            dr.ellipse((x - rad, y - rad, x + rad, y + rad), fill=RED)
            if d > 0.8 and rng.random() < 0.35:
                rb = rad * 0.45
                db.ellipse((x - rb, y - rb, x + rb, y + rb), fill=BLACK)

red.save(f'{prefix}-r.webp', quality=88, method=6)
blk.save(f'{prefix}-k.webp', quality=88, method=6)
print(mode, cols, 'x', rows)
