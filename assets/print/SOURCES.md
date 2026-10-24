# Plates

Illustrations generated with Google Gemini (gemini.google.com, image mode / Nano Banana),
October 2026, from the account demirciberk.db@gmail.com. hero and fly came from the 3.1 Pro
model; koku, cv, medical, portrait and contact came from 3.6 Flash.

Every prompt ended with this shared style block:

> Style: two-colour risograph print. Inks: fluorescent vermilion red and deep warm black only,
> no other colours. Visible riso grain, fine halftone dot shading, slight ink misregistration
> between the two layers. Precise scientific-illustration linework meets editorial print.
> Composition: flat full-bleed scan, the warm off-white uncoated paper fills the entire image
> edge to edge. NOT a photograph of a print: no table, no mockup, no paper edges, no frame,
> no border, no shadow. Subject centred with generous empty paper around it. No text, no
> letters, no numbers.

| plate   | subject prompt (abridged) |
|---------|---------------------------|
| hero    | distillation apparatus; big flask full of neural-network threads, droplet into a tiny vial |
| fly     | fruit fly plate, wings spread, scent wisp from a perfume atomiser |
| koku    | faceted perfume bottle, vapour breaking into ranked dots, rose / fig / bergamot sprigs |
| cv      | paper letters and envelopes flying in an arc like migrating birds |
| medical | one anatomical heart engraving with a regression curve and data points, stethoscope |
| portrait | Berk's own ID photo uploaded as reference; abstract scribble portrait, face half buried under a red scribble knot, broken black and red lines, 4:3 |
| contact | paper airplane folded from a letter, dotted looping trail |

`sep.py` splits each PNG into a black-ink layer (`*-k.webp`) and a red-ink layer
(`*-r.webp`); the page multiplies both onto the paper colour and moves the red layer to
print "out of register" on hover and pointer move.

    python sep.py source.png name 1600
