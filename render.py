#!/usr/bin/env python3
"""Render an invented passport spread (Republic of Kestrelia) to entry.png.

Everything is drawn from scratch with PIL: no downloaded images.
All layout numbers are in FINAL pixels (1024x1024); the canvas is
rendered at 2x and downscaled for crisp text.
"""
import math
from PIL import Image, ImageDraw, ImageFont

S = 2
W = H = 1024 * S
OUT = "entry.png"

DJ = "/usr/share/fonts/truetype/dejavu/"
SERIF = DJ + "DejaVuSerif.ttf"
SERIF_B = DJ + "DejaVuSerif-Bold.ttf"
SANS = DJ + "DejaVuSans.ttf"
SANS_B = DJ + "DejaVuSans-Bold.ttf"
MONO = DJ + "DejaVuSansMono.ttf"
MONO_B = DJ + "DejaVuSansMono-Bold.ttf"


def px(v):
    """Final-pixel value -> canvas pixels."""
    return int(round(v * S))


def font(path, size):
    """size in final pixels."""
    return ImageFont.truetype(path, px(size))


CREAM = (242, 234, 216)
PAPER = (247, 241, 226)
GREEN = (29, 74, 51)
GREEN_D = (18, 52, 35)
GOLD = (176, 141, 58)
INK = (32, 32, 34)
BLUE_INK = (38, 74, 138)
RED_INK = (150, 48, 40)
PURPLE_INK = (96, 58, 128)
MUTED = (110, 96, 70)


def check_digit(s):
    weights = [7, 3, 1]
    vals = {}
    for c in "0123456789":
        vals[c] = int(c)
    for i, c in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        vals[c] = 10 + i
    vals["<"] = 0
    return str(sum(vals[ch] * weights[i % 3] for i, ch in enumerate(s)) % 10)


def mrz_lines():
    name = "VOSS<<MIRA<ALDEN"
    line1 = ("P<KES" + name).ljust(44, "<")
    doc = "KV482917<"
    doc_cd = check_digit(doc)
    dob, dob_cd = "910414", check_digit("910414")
    exp, exp_cd = "330312", check_digit("330312")
    personal = "<" * 14
    personal_cd = check_digit(personal)
    composite = check_digit(doc + doc_cd + dob + dob_cd + exp + exp_cd
                            + personal + personal_cd)
    line2 = (doc + doc_cd + "KES" + dob + dob_cd + "F" + exp + exp_cd
             + personal + personal_cd + composite)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


def guilloche(d):
    for k in range(46):
        y0 = px(30 + k * 21)
        pts = []
        for x in range(0, W + px(10), px(10)):
            y = y0 + px(7) * math.sin(x / px(85) + k * 0.7)
            pts.append((x, y))
        d.line(pts, fill=(205, 194, 158), width=2)


def draw_coat_of_arms(d, cx, cy, r):
    # cx, cy, r in final pixels; convert inside
    cx, cy, r = px(cx), px(cy), px(r)
    shield = [(cx - r, cy - int(r * 0.9)), (cx + r, cy - int(r * 0.9)),
              (cx + r, cy + int(r * 0.1)),
              (cx + int(r * 0.55), cy + int(r * 0.75)), (cx, cy + int(r * 1.05)),
              (cx - int(r * 0.55), cy + int(r * 0.75)),
              (cx - r, cy + int(r * 0.1))]
    d.polygon(shield, fill=(244, 238, 222), outline=GREEN, width=6)
    inner = [(cx - int(r * 0.82), cy - int(r * 0.72)),
             (cx + int(r * 0.82), cy - int(r * 0.72)),
             (cx + int(r * 0.82), cy + int(r * 0.05)),
             (cx + int(r * 0.45), cy + int(r * 0.6)), (cx, cy + int(r * 0.85)),
             (cx - int(r * 0.45), cy + int(r * 0.6)),
             (cx - int(r * 0.82), cy + int(r * 0.05))]
    d.polygon(inner, fill=(214, 230, 222), outline=GOLD, width=4)
    mtn = [(cx - int(r * 0.78), cy + int(r * 0.55)),
           (cx - int(r * 0.35), cy - int(r * 0.25)),
           (cx - int(r * 0.05), cy + int(r * 0.18)),
           (cx + int(r * 0.28), cy - int(r * 0.42)),
           (cx + int(r * 0.78), cy + int(r * 0.55))]
    d.polygon(mtn, fill=GREEN)
    d.polygon([(cx - int(r * 0.35), cy - int(r * 0.25)),
               (cx - int(r * 0.22), cy - int(r * 0.02)),
               (cx - int(r * 0.48), cy - int(r * 0.02))], fill=(250, 250, 248))
    d.polygon([(cx + int(r * 0.28), cy - int(r * 0.42)),
               (cx + int(r * 0.14), cy - int(r * 0.16)),
               (cx + int(r * 0.42), cy - int(r * 0.16))], fill=(250, 250, 248))
    sx, sy, sr = cx, cy - int(r * 0.62), int(r * 0.16)
    star = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = sr if i % 2 == 0 else int(sr * 0.42)
        star.append((sx + rr * math.cos(ang), sy + rr * math.sin(ang)))
    d.polygon(star, fill=GOLD)


def draw_portrait(d, box):
    # box in final pixels
    x0, y0, x1, y1 = [px(v) for v in box]
    w, h = x1 - x0, y1 - y0
    for i in range(h):
        t = i / h
        c = tuple(int(a + (b - a) * t) for a, b in zip((196, 209, 220),
                                                      (158, 176, 194)))
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=c)
    cx = (x0 + x1) // 2
    hair = (94, 58, 40)
    # back hair mass behind shoulders
    d.pieslice([cx - int(w * 0.27), y0 + int(h * 0.02),
                cx + int(w * 0.27), y0 + int(h * 0.70)], 0, 360, fill=hair)
    # shoulders / jacket (teal)
    d.polygon([(x0, y1), (x0, y1 - int(h * 0.16)),
               (cx - int(w * 0.26), y0 + int(h * 0.74)),
               (cx - int(w * 0.10), y0 + int(h * 0.70)),
               (cx, y0 + int(h * 0.78)),
               (cx + int(w * 0.10), y0 + int(h * 0.70)),
               (cx + int(w * 0.26), y0 + int(h * 0.74)),
               (x1, y1 - int(h * 0.16)), (x1, y1)], fill=(46, 96, 88))
    # shirt V + collar
    d.polygon([(cx - int(w * 0.10), y0 + int(h * 0.70)),
               (cx, y0 + int(h * 0.94)),
               (cx + int(w * 0.10), y0 + int(h * 0.70)),
               (cx, y0 + int(h * 0.78))], fill=(245, 244, 238))
    d.polygon([(cx - int(w * 0.10), y0 + int(h * 0.70)),
               (cx - int(w * 0.02), y0 + int(h * 0.80)),
               (cx, y0 + int(h * 0.78))], fill=(225, 222, 210))
    d.polygon([(cx + int(w * 0.10), y0 + int(h * 0.70)),
               (cx + int(w * 0.02), y0 + int(h * 0.80)),
               (cx, y0 + int(h * 0.78))], fill=(225, 222, 210))
    # neck
    d.rectangle([cx - int(w * 0.075), y0 + int(h * 0.60),
                 cx + int(w * 0.075), y0 + int(h * 0.74)], fill=(214, 164, 122))
    # ears
    d.ellipse([cx - int(w * 0.235), y0 + int(h * 0.30),
               cx - int(w * 0.155), y0 + int(h * 0.44)], fill=(226, 178, 134))
    d.ellipse([cx + int(w * 0.155), y0 + int(h * 0.30),
               cx + int(w * 0.235), y0 + int(h * 0.44)], fill=(226, 178, 134))
    # face
    d.ellipse([cx - int(w * 0.20), y0 + int(h * 0.10),
               cx + int(w * 0.20), y0 + int(h * 0.60)], fill=(232, 184, 140))
    # hair: dome over the top of the head
    d.pieslice([cx - int(w * 0.235), y0 + int(h * 0.02),
                cx + int(w * 0.235), y0 + int(h * 0.52)], 180, 360, fill=hair)
    # fringe: shallow curved band across the forehead, higher in the middle
    fringe = [(cx - int(w * 0.235), y0 + int(h * 0.24)),
              (cx - int(w * 0.20), y0 + int(h * 0.05)),
              (cx + int(w * 0.20), y0 + int(h * 0.05)),
              (cx + int(w * 0.235), y0 + int(h * 0.24)),
              (cx + int(w * 0.17), y0 + int(h * 0.17)),
              (cx + int(w * 0.06), y0 + int(h * 0.12)),
              (cx - int(w * 0.06), y0 + int(h * 0.15)),
              (cx - int(w * 0.17), y0 + int(h * 0.13))]
    d.polygon(fringe, fill=hair)
    # side strands
    d.polygon([(cx - int(w * 0.235), y0 + int(h * 0.20)),
               (cx - int(w * 0.20), y0 + int(h * 0.28)),
               (cx - int(w * 0.19), y0 + int(h * 0.60)),
               (cx - int(w * 0.26), y0 + int(h * 0.64)),
               (cx - int(w * 0.27), y0 + int(h * 0.30))], fill=hair)
    d.polygon([(cx + int(w * 0.235), y0 + int(h * 0.20)),
               (cx + int(w * 0.20), y0 + int(h * 0.28)),
               (cx + int(w * 0.19), y0 + int(h * 0.60)),
               (cx + int(w * 0.26), y0 + int(h * 0.64)),
               (cx + int(w * 0.27), y0 + int(h * 0.30))], fill=hair)
    # brows
    d.line([(cx - int(w * 0.135), y0 + int(h * 0.315)),
            (cx - int(w * 0.055), y0 + int(h * 0.305))],
           fill=(70, 44, 30), width=px(3))
    d.line([(cx + int(w * 0.055), y0 + int(h * 0.305)),
            (cx + int(w * 0.135), y0 + int(h * 0.315))],
           fill=(70, 44, 30), width=px(3))
    # eyes
    for ex in (cx - int(w * 0.095), cx + int(w * 0.095)):
        d.ellipse([ex - int(w * 0.038), y0 + int(h * 0.335),
                   ex + int(w * 0.038), y0 + int(h * 0.375)],
                  fill=(250, 250, 248), outline=(90, 60, 40), width=px(1.5))
        d.ellipse([ex - int(w * 0.018), y0 + int(h * 0.345),
                   ex + int(w * 0.018), y0 + int(h * 0.372)], fill=(58, 42, 28))
    # nose
    d.line([(cx, y0 + int(h * 0.38)), (cx - int(w * 0.012), y0 + int(h * 0.46)),
            (cx + int(w * 0.018), y0 + int(h * 0.465))],
           fill=(190, 140, 100), width=px(2.5))
    # lips
    d.polygon([(cx - int(w * 0.055), y0 + int(h * 0.51)),
               (cx, y0 + int(h * 0.50)),
               (cx + int(w * 0.055), y0 + int(h * 0.51)),
               (cx, y0 + int(h * 0.535))], fill=(168, 92, 82))
    # cheeks
    d.ellipse([cx - int(w * 0.17), y0 + int(h * 0.42),
               cx - int(w * 0.09), y0 + int(h * 0.48)], fill=(226, 168, 128))
    d.ellipse([cx + int(w * 0.09), y0 + int(h * 0.42),
               cx + int(w * 0.17), y0 + int(h * 0.48)], fill=(226, 168, 128))


def stamp(d, x, y, w, h, color, country, port, kind, date, angle):
    """A rotated rectangular immigration stamp; x,y,w,h in final pixels."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    x, y, w, h = px(x), px(y), px(w), px(h)
    sd.rounded_rectangle([x, y, x + w, y + h], radius=px(9),
                         outline=color + (255,), width=px(3.5))
    sd.rounded_rectangle([x + px(7), y + px(7), x + w - px(7), y + h - px(7)],
                         radius=px(6), outline=color + (255,), width=px(1.5))
    sd.text((x + w // 2, y + px(28)), country, font=font(SANS_B, 17),
            fill=color + (255,), anchor="mm")
    sd.text((x + w // 2, y + px(56)), port, font=font(SANS, 12),
            fill=color + (255,), anchor="mm")
    sd.text((x + w // 2, y + px(86)), kind, font=font(SANS_B, 15),
            fill=color + (255,), anchor="mm")
    sd.text((x + w // 2, y + px(116)), date, font=font(MONO_B, 15),
            fill=color + (255,), anchor="mm")
    cx, cy = x + px(39), y + px(86)
    sd.ellipse([cx - px(17), cy - px(17), cx + px(17), cy + px(17)],
               outline=color + (255,), width=px(2))
    star = []
    for i in range(8):
        ang = -math.pi / 2 + i * math.pi / 4
        rr = px(13) if i % 2 == 0 else px(5)
        star.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    sd.polygon(star, fill=color + (255,))
    layer = layer.rotate(angle, resample=Image.BICUBIC,
                         center=(x + w // 2, y + h // 2))
    base = img.convert("RGBA")
    img.paste(Image.alpha_composite(base, layer).convert("RGB"), (0, 0))


def centered(d, cx, y, text, f, fill):
    d.text((px(cx), px(y)), text, font=f, fill=fill, anchor="ma")


def field(d, x, y, label, value):
    d.text((px(x), px(y)), label, font=font(SANS_B, 10), fill=MUTED)
    d.text((px(x), px(y + 13)), value, font=font(SANS_B, 16), fill=INK)


img = Image.new("RGB", (W, H), CREAM)
d = ImageDraw.Draw(img, "RGBA")
guilloche(d)

# outer double frame
d.rectangle([px(11), px(11), W - px(11), H - px(11)], outline=GREEN, width=px(5))
d.rectangle([px(20), px(20), W - px(20), H - px(20)], outline=GOLD, width=px(2))
# centre gutter
d.line([(W // 2, px(20)), (W // 2, H - px(20))], fill=(190, 176, 140),
       width=px(3))
d.line([(W // 2 - px(4), px(20)), (W // 2 - px(4), H - px(20))],
       fill=(120, 106, 70), width=px(1))

# ================= LEFT PAGE : DATA PAGE =================
LX0, LX1 = 32, 488
lcx = (LX0 + LX1) // 2

draw_coat_of_arms(d, lcx, 108, 55)
centered(d, lcx, 178, "REPUBLIC OF KESTRELIA", font(SERIF_B, 25), GREEN_D)
centered(d, lcx, 210, "P A S S P O R T", font(SERIF, 23), GREEN)
centered(d, lcx, 242, "KESA · VUOR · VALO  —  FREEDOM · MOUNTAINS · LIGHT",
         font(SANS, 9), MUTED)
d.line([(px(LX0 + 30), px(262)), (px(LX1 - 30), px(262))], fill=GOLD,
       width=px(2))
centered(d, lcx, 272, "PASSPORT No.   KV 482 917", font(SANS_B, 13), GREEN_D)

# photo
px0, py0, px1, py1 = 40, 300, 190, 500
draw_portrait(d, (px0, py0, px1, py1))
d.rectangle([px(px0), px(py0), px(px1), px(py1)], outline=GREEN, width=px(3))
d.text((px(px0 + 4), px(py1 - 22)), "PHOTO  •  KUVA", font=font(SANS_B, 9),
       fill=(255, 255, 255))
d.text((px((px0 + px1) // 2), px(py1 + 20)), "Mira A. Voss",
       font=font(SERIF, 20), fill=INK, anchor="ma")
d.line([(px(px0), px(py1 + 48)), (px(px1), px(py1 + 48))], fill=INK,
       width=px(1.5))
centered(d, (px0 + px1) // 2, py1 + 54, "HOLDER'S SIGNATURE",
         font(SANS, 8), MUTED)

# data fields, right of photo
fx = 205
rows = [
    ("SURNAME / SUKUNIMI", "VOSS"),
    ("GIVEN NAMES / ETUNIMET", "MIRA ALDEN"),
    ("NATIONALITY / KANSALAISUUS", "KESTRELIAN"),
    ("DATE OF BIRTH / SYNTYMÄAIKA", "14 APR 1991"),
    ("PLACE OF BIRTH / SYNTYMÄPAIKKA", "TALVEN, KESTRELIA"),
    ("SEX / SUKUPUOLI", "F"),
    ("DATE OF ISSUE / MYÖNNETTY", "12 MAR 2023"),
    ("DATE OF EXPIRY / VOIMASSA", "12 MAR 2033"),
    ("AUTHORITY — TALVEN", "MINISTRY OF THE INTERIOR"),
]
y = 300
for label, value in rows:
    field(d, fx, y, label, value)
    y += 40

# validity note
d.line([(px(LX0 + 30), px(668)), (px(LX1 - 30), px(668))], fill=GOLD,
       width=px(1))
centered(d, lcx, 680,
         "THIS PASSPORT IS VALID FOR ALL COUNTRIES",
         font(SANS_B, 10), GREEN_D)
centered(d, lcx, 696,
         "EXCEPT THE NORTHERN MARCHES",
         font(SANS_B, 10), GREEN_D)
centered(d, lcx, 716,
         "KESTRELIA  •  EST. 1919  •  MEMBER OF THE ALDERMERE PACT",
         font(SANS, 9), MUTED)

# MRZ strip
line1, line2 = mrz_lines()
d.rectangle([px(LX0 + 8), px(760), px(LX1 - 8), px(992)],
            fill=(238, 234, 222), outline=GREEN, width=px(1.5))
d.text((px(lcx), px(800)), line1, font=font(MONO, 15), fill=INK, anchor="ma")
d.text((px(lcx), px(832)), line2, font=font(MONO, 15), fill=INK, anchor="ma")
centered(d, lcx, 880, "P<KESVOSS<<MIRA<ALDEN  •  KV482917  •  TALVEN",
         font(SANS, 9), MUTED)
centered(d, lcx, 912, "MACHINE-READABLE ZONE — DO NOT FOLD OR STAPLE",
         font(SANS, 8), MUTED)
centered(d, lcx, 944, "MINISTRY OF THE INTERIOR  •  TALVEN  •  KESTRELIA",
         font(SANS, 9), GREEN_D)

# ================= RIGHT PAGE : VISAS & STAMPS =================
RX0, RX1 = 536, 992
rcx = (RX0 + RX1) // 2
centered(d, rcx, 60, "VISAS", font(SERIF_B, 26), GREEN_D)
centered(d, rcx, 96, "STAMPS & ENDORSEMENTS  •  LEIMAT JA MERKINNÄT",
         font(SANS, 10), MUTED)
d.line([(px(RX0 + 30), px(118)), (px(RX1 - 30), px(118))], fill=GOLD,
       width=px(2))

stamp(d, RX0 + 12, 140, 440, 135, BLUE_INK, "MERIDIA",
      "PORT OF ALDERMERE", "ARRIVAL", "04 JUN 2024", -3)
stamp(d, RX0 + 12, 293, 440, 135, RED_INK, "MERIDIA",
      "PORT OF ALDERMERE", "DEPARTURE", "21 JUN 2024", 2)
stamp(d, RX0 + 12, 446, 440, 135, PURPLE_INK, "VALDORIA",
      "BORDER POST KARA", "ARRIVAL", "09 SEP 2024", -2)
stamp(d, RX0 + 12, 599, 440, 135, BLUE_INK, "OSTARA",
      "HARBOUR OF SELK", "ARRIVAL", "18 FEB 2025", 3)

# conditions of entry box — the telling paperwork detail
bx0, by0, bx1, by1 = RX0 + 12, 760, RX1 - 12, 940
d.rectangle([px(bx0), px(by0), px(bx1), px(by1)], fill=(250, 246, 234),
            outline=GREEN, width=px(2))
centered(d, rcx, by0 + 10, "CONDITIONS OF ENTRY  —  MERIDIA",
         font(SANS_B, 13), GREEN_D)
cond = [
    "Holder may take no paid employment in the",
    "Northern Marches. Stay limited to ninety (90)",
    "days. Fee of 40 KRD paid at Talven, 12 MAR 2023.",
    "A return ticket must be shown on departure.",
]
y = by0 + 38
for ln in cond:
    d.text((px(bx0 + 14), px(y)), ln, font=font(SANS, 12.5), fill=INK)
    y += 24
# fee stamp circle overlapping the box corner
fcx, fcy, fr = bx1 - 62, by1 - 46, 52
d.ellipse([px(fcx - fr), px(fcy - fr), px(fcx + fr), px(fcy + fr)],
          outline=RED_INK, width=px(3))
d.ellipse([px(fcx - fr + 7), px(fcy - fr + 7), px(fcx + fr - 7),
           px(fcy + fr - 7)], outline=RED_INK, width=px(1.5))
centered(d, fcx, fcy - 31, "EXIT TAX", font(SANS_B, 12), RED_INK)
centered(d, fcx, fcy - 13, "PAID", font(SANS_B, 12), RED_INK)
centered(d, fcx, fcy + 5, "40 KRD", font(MONO_B, 14), RED_INK)
centered(d, fcx, fcy + 24, "TALVEN", font(SANS_B, 10), RED_INK)

# fine print
centered(d, rcx, 958,
         "This passport is the property of the Republic of Kestrelia",
         font(SANS, 10), MUTED)
centered(d, rcx, 974,
         "and must be surrendered on demand. — Ministry of the Interior, Talven",
         font(SANS, 10), MUTED)

img = img.resize((1024, 1024), Image.LANCZOS)
img.save(OUT, optimize=True)
print("saved", OUT)
