#!/usr/bin/env python3
"""The Passport Page of a Country That Isn't There.

Draws one invented passport spread (Republic of Leonida) and writes it to
/output/entry.png (or ./entry.png when /output does not exist, e.g. local runs).
Deterministic: fixed seed, no timestamps, no network. Stdlib + PIL only.
"""
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(BASE, "fonts")
W, H = 1024, 1024

# ---------------------------------------------------------------- palette
NAVY = (22, 35, 63)
NAVY_DARK = (14, 23, 42)
INK = (18, 18, 22)
LABEL = (96, 104, 116)
PAGE_L = (248, 245, 237)
PAGE_R = (246, 242, 232)
RULE = (180, 176, 160)
RED_INK = (178, 44, 38)
BLUE_INK = (36, 72, 140)
GREEN_INK = (32, 104, 88)
PURPLE_INK = (96, 54, 128)

# ---------------------------------------------------------------- holder data
SURNAME = "MARLOWE"
GIVEN = "ELENA R."
DOC_NO = "LN4829137"          # 9 chars
NATIONALITY = "LND"
DOB = "980512"                # 12 MAY 1998 -> YYMMDD
SEX = "F"
EXPIRY = "340313"             # 13 MAR 2034
PERSONAL = "<" * 14           # no personal number on record
ISSUE_DATE = "14 MAR 2024"
EXPIRY_DATE = "13 MAR 2034"
BIRTH_DATE = "12 MAY 1998"

# ---------------------------------------------------------------- MRZ (ICAO 9303 TD3)
# Line 1: P< + country(3) + surname + << + given names, padded with < to 44.
# Line 2: doc(9) + CD + nat(3) + dob(6) + CD + sex(1) + exp(6) + CD
#         + personal(14) + CD + composite CD = 44.
_VALUES = {c: i for i, c in enumerate("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")}
_VALUES["<"] = 0


def _check_digit(text):
    total = 0
    for i, ch in enumerate(text):
        total += _VALUES[ch] * (7, 3, 1)[i % 3]
    return str(total % 10)


def mrz_line1():
    # MRZ allows only A-Z, 0-9 and <: "ELENA R." -> "ELENA<R".
    given = "<".join(GIVEN.replace(".", "").split())
    body = "P<" + NATIONALITY + SURNAME + "<<" + given
    assert len(body) <= 44, body
    return body + "<" * (44 - len(body))


def mrz_line2(doc=DOC_NO, nat=NATIONALITY, dob=DOB, sex=SEX, exp=EXPIRY,
              personal=PERSONAL):
    part = doc + _check_digit(doc)
    part += nat
    part += dob + _check_digit(dob)
    part += sex
    part += exp + _check_digit(exp)
    part += personal + _check_digit(personal)
    composite_src = part[:10] + part[13:20] + part[21:28] + part[28:43]
    part += _check_digit(composite_src)
    assert len(part) == 44, (part, len(part))
    return part


def _self_test_mrz():
    # Canonical ICAO Doc 9303 example: must reproduce exactly.
    line2 = mrz_line2(doc="L898902C3", nat="UTO", dob="740812", sex="F",
                      exp="120415", personal="ZE184226B<<<<<")
    assert line2 == "L898902C36UTO7408122F1204159ZE184226B<<<<<10", line2
    assert mrz_line1() == "P<LNDMARLOWE<<ELENA<R" + "<" * 23
    assert mrz_line2() == "LN48291374LND9805127F3403130" + "<" * 14 + "08"


# ---------------------------------------------------------------- fonts
def font(size, bold=False, mono=False):
    name = "DejaVuSansMono.ttf" if mono else (
        "LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf")
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def draw_spaced(draw, xy, text, fnt, fill, spacing=2):
    """Draw text with letter-spacing (official header look)."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + spacing
    return x


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


# ---------------------------------------------------------------- emblem
def draw_emblem(draw, cx, cy, r, color):
    """Restrained shield: sun over a palm. Line art only."""
    # shield outline
    pts = [(cx - r, cy - r), (cx + r, cy - r), (cx + r, cy + r * 0.25),
           (cx, cy + r + 6), (cx - r, cy + r * 0.25)]
    draw.line(pts + [pts[0]], fill=color, width=2)
    # sun
    sx, sy, sr = cx, cy - r * 0.35, r * 0.30
    draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], outline=color, width=2)
    for a in range(0, 360, 45):
        import math
        x0 = sx + (sr + 2) * math.cos(math.radians(a))
        y0 = sy + (sr + 2) * math.sin(math.radians(a))
        x1 = sx + (sr + 7) * math.cos(math.radians(a))
        y1 = sy + (sr + 7) * math.sin(math.radians(a))
        draw.line([(x0, y0), (x1, y1)], fill=color, width=2)
    # palm: trunk + 4 fronds
    tx, ty0, ty1 = cx, cy + r * 0.15, cy + r * 0.62
    draw.line([(tx, ty0), (tx, ty1)], fill=color, width=2)
    for dx, dy in [(-14, -8), (-8, -12), (8, -12), (14, -8)]:
        draw.arc([tx + dx - 8, ty0 + dy - 4, tx + dx + 8, ty0 + dy + 8],
                 start=180, end=360, fill=color, width=2)


# ---------------------------------------------------------------- portrait
SKIN = (198, 138, 94)
SKIN_SH = (178, 118, 76)
HAIR = (58, 35, 20)
HAIR_HI = (86, 56, 32)
BLOUSE = (46, 110, 106)
LIP = (158, 74, 66)


def draw_portrait(size=(150, 190)):
    """Flat-illustration passport photo: sun-tanned Leonida citizen, female."""
    w, h = size
    img = Image.new("RGB", (w, h), (232, 238, 240))
    d = ImageDraw.Draw(img)
    cx = w // 2
    # shoulders / blouse
    d.pieslice([cx - 62, h - 78, cx + 62, h + 40], start=180, end=360,
               fill=BLOUSE)
    d.rectangle([0, h - 22, w, h], fill=BLOUSE)
    # collar V
    d.polygon([(cx - 16, h - 30), (cx + 16, h - 30), (cx, h - 8)],
              fill=(232, 238, 240))
    # neck (wide, so the jaw reads as skin, not hair)
    d.rectangle([cx - 16, h - 78, cx + 16, h - 34], fill=SKIN_SH)
    d.rectangle([cx - 16, h - 78, cx + 16, h - 58], fill=SKIN)
    # hair back mass (shoulder length, ends above the blouse line)
    d.rounded_rectangle([cx - 46, 18, cx + 46, 132], radius=38, fill=HAIR)
    # face
    d.ellipse([cx - 34, 26, cx + 34, 108], fill=SKIN)
    # ears
    d.ellipse([cx - 42, 62, cx - 31, 82], fill=SKIN)
    d.ellipse([cx + 31, 62, cx + 42, 82], fill=SKIN)
    d.ellipse([cx - 39, 76, cx - 36, 79], fill=(212, 175, 55))  # earring
    d.ellipse([cx + 36, 76, cx + 39, 79], fill=(212, 175, 55))
    # hair top + short side sweep (ends above the chin: no beard read)
    d.pieslice([cx - 36, 18, cx + 36, 82], start=180, end=360, fill=HAIR)
    d.polygon([(cx - 36, 44), (cx - 31, 78), (cx - 26, 78), (cx - 29, 44)],
              fill=HAIR)
    d.polygon([(cx + 36, 44), (cx + 31, 78), (cx + 26, 78), (cx + 29, 44)],
              fill=HAIR)
    # chin shadow separates jaw from neck
    d.arc([cx - 16, 96, cx + 16, 112], start=0, end=180, fill=SKIN_SH,
          width=2)
    # hair highlight
    d.arc([cx - 30, 22, cx + 6, 52], start=200, end=330, fill=HAIR_HI, width=4)
    # brows
    d.arc([cx - 24, 58, cx - 6, 68], start=200, end=340, fill=HAIR, width=2)
    d.arc([cx + 6, 58, cx + 24, 68], start=200, end=340, fill=HAIR, width=2)
    # eyes
    for ex in (cx - 15, cx + 15):
        d.ellipse([ex - 6, 68, ex + 6, 76], fill=(255, 255, 255))
        d.ellipse([ex - 3, 69, ex + 3, 75], fill=(42, 26, 16))
        d.ellipse([ex - 1, 70, ex + 1, 72], fill=(255, 255, 255))
        d.line([(ex - 6, 68), (ex + 6, 68)], fill=INK, width=1)
    # nose (minimal)
    d.line([(cx, 76), (cx - 1, 86)], fill=SKIN_SH, width=2)
    d.arc([cx - 4, 84, cx + 4, 90], start=0, end=180, fill=SKIN_SH, width=2)
    # lips
    d.pieslice([cx - 9, 92, cx + 9, 100], start=0, end=180, fill=LIP)
    d.line([(cx - 9, 95), (cx + 9, 95)], fill=(120, 52, 46), width=1)
    return img


# ---------------------------------------------------------------- stamps
def worn(layer, rng, density=0.10):
    """Erase a deterministic scatter of ink pixels -> worn rubber-stamp look."""
    px = layer.load()
    w, h = layer.size
    n = int(w * h * density)
    for _ in range(n):
        x = rng.randrange(w)
        y = rng.randrange(h)
        if px[x, y][3] > 0:
            px[x, y] = (px[x, y][0], px[x, y][1], px[x, y][2], 0)
    return layer


def make_rect_stamp(place, action, date, color, rng, angle, w=208, h=118):
    layer = Image.new("RGBA", (w + 40, h + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = 20, 20, 20 + w, 20 + h
    d.rectangle([x0, y0, x1, y1], outline=color, width=3)
    d.rectangle([x0 + 5, y0 + 5, x1 - 5, y1 - 5], outline=color, width=1)
    f_small = font(11, bold=True)
    f_place = font(16, bold=True)
    f_action = font(20, bold=True)
    f_date = font(14, bold=True)
    d.text(((x0 + x1) / 2, y0 + 8), "LEONIDA  •  IMMIGRATION",
           font=f_small, fill=color, anchor="ma")
    d.line([(x0 + 10, y0 + 26), (x1 - 10, y0 + 26)], fill=color, width=1)
    d.text(((x0 + x1) / 2, y0 + 30), place, font=f_place, fill=color,
           anchor="ma")
    d.text(((x0 + x1) / 2, y0 + 52), action, font=f_action, fill=color,
           anchor="ma")
    d.text(((x0 + x1) / 2, y0 + 80), date, font=f_date, fill=color,
           anchor="ma")
    layer = worn(layer, rng)
    return layer.rotate(angle, resample=Image.BICUBIC, expand=True)


def make_round_stamp(place, action, date, color, rng, angle, r=66):
    s = 2 * r + 44
    layer = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    c = s // 2
    d.ellipse([c - r, c - r, c + r, c + r], outline=color, width=3)
    d.ellipse([c - r + 6, c - r + 6, c + r - 6, c + r - 6], outline=color,
              width=1)
    f_place = font(12, bold=True)
    f_action = font(16, bold=True)
    f_date = font(13, bold=True)
    # straight lines inside the circle: curved text collided with the action
    d.text((c, c - 42), place, font=f_place, fill=color, anchor="mm")
    d.text((c, c - 12), action, font=f_action, fill=color, anchor="mm")
    d.line([(c - 34, c + 8), (c + 34, c + 8)], fill=color, width=1)
    d.text((c, c + 20), date, font=f_date, fill=color, anchor="mm")
    d.text((c, c + 38), "LEONIDA", font=font(10, bold=True), fill=color,
           anchor="mm")
    layer = worn(layer, rng)
    return layer.rotate(angle, resample=Image.BICUBIC, expand=True)


def make_fee_stamp(rng, angle):
    layer = Image.new("RGBA", (260, 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rectangle([4, 4, 255, 85], outline=GREEN_INK, width=3)
    d.text((130, 12), "ALLIGATOR CROSSING FEE", font=font(13, bold=True),
           fill=GREEN_INK, anchor="ma")
    d.text((130, 34), "PAID  $5", font=font(20, bold=True), fill=GREEN_INK,
           anchor="ma")
    d.text((130, 62), "02 JUN 2024  •  PORT GELLHORN", font=font(11, bold=True),
           fill=GREEN_INK, anchor="ma")
    layer = worn(layer, rng, density=0.08)
    return layer.rotate(angle, resample=Image.BICUBIC, expand=True)


# ---------------------------------------------------------------- page build
def field(draw, x, y, label, value, value_size=15, width=None):
    draw.text((x, y), label, font=font(10), fill=LABEL)
    draw.text((x, y + 13), value, font=font(value_size, bold=True), fill=INK)
    return y + 13 + value_size + 8


def build():
    _self_test_mrz()
    rng = random.Random(20261121)
    img = Image.new("RGB", (W, H), NAVY_DARK)
    d = ImageDraw.Draw(img)

    # --- spread pages ------------------------------------------------------
    # soft shadow under the open book
    d.rectangle([34, 34, 1002, 1002], fill=(8, 12, 24))
    d.rectangle([28, 28, 510, 996], fill=PAGE_L)     # data page
    d.rectangle([514, 28, 996, 996], fill=PAGE_R)    # stamps page
    # gutter shadow
    for i in range(10):
        a = 26 - i * 2
        d.line([(510 - i, 28), (510 - i, 996)], fill=(200, 196, 180))
        d.line([(514 + i, 28), (514 + i, 996)], fill=(200, 196, 180))
    d.line([(512, 28), (512, 996)], fill=(160, 156, 138), width=2)

    # faint diagonal watermark on the data page
    wm = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wm)
    wf = font(20, bold=True)
    for yy in range(-40, H + 40, 90):
        wd.text((40, yy), "REPUBLIC OF LEONIDA  •  ", font=wf,
                fill=(22, 35, 63, 10))
    wm = wm.rotate(-28, resample=Image.BICUBIC, center=(256, 512))
    img.paste(Image.alpha_composite(img.convert("RGBA"), wm).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)

    # --- LEFT: data page ---------------------------------------------------
    # header
    draw_emblem(d, 78, 78, 26, NAVY)
    draw_spaced(d, (118, 52), "REPUBLIC OF LEONIDA", font(20, bold=True), NAVY,
                spacing=2)
    draw_spaced(d, (118, 80), "PASSPORT", font(14, bold=True), NAVY,
                spacing=8)
    d.text((492, 80), "No. LN 4829137", font=font(13, bold=True), fill=NAVY,
           anchor="ra")
    d.line([(48, 118), (492, 118)], fill=NAVY, width=2)
    d.line([(48, 122), (492, 122)], fill=NAVY, width=1)

    # portrait
    portrait = draw_portrait()
    img.paste(portrait, (48, 140))
    d.rectangle([48, 140, 198, 330], outline=NAVY, width=2)
    d.text((48, 336), "PHOTOGRAPH", font=font(9), fill=LABEL)

    # fields beside portrait
    x = 216
    y = 140
    y = field(d, x, y, "TYPE / CODE", "P   /   LND")
    y = field(d, x, y, "SURNAME", "MARLOWE")
    y = field(d, x, y, "GIVEN NAMES", "ELENA R.")
    y = field(d, x, y, "NATIONALITY", "LEONIDIAN")
    y = field(d, x, y, "DATE OF BIRTH", BIRTH_DATE)
    y = field(d, x, y, "PLACE OF BIRTH", "VICE CITY, LEONIDA")
    y = field(d, x, y, "SEX", "F")

    # second field block
    y = 372
    d.line([(48, y), (492, y)], fill=RULE, width=1)
    y += 12
    y1 = field(d, 48, y, "DATE OF ISSUE", ISSUE_DATE)
    y2 = field(d, 280, y, "DATE OF EXPIRY", EXPIRY_DATE)
    y = max(y1, y2)
    y = field(d, 48, y, "AUTHORITY",
              "LEONIDA DEPARTMENT OF STATE — VICE CITY", value_size=13)

    # signature
    y += 4
    d.line([(48, y + 26), (300, y + 26)], fill=INK, width=1)
    sig = Image.new("RGBA", (252, 30), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sig)
    pts = [(8, 20), (30, 8), (52, 22), (74, 10), (96, 20), (120, 6),
           (144, 20), (168, 12), (196, 20), (224, 10), (244, 18)]
    sd.line(pts, fill=(30, 30, 60, 220), width=2, joint="curve")
    img.paste(sig, (48, y), sig)
    d.text((48, y + 30), "SIGNATURE OF BEARER", font=font(9), fill=LABEL)
    d.text((330, y + 30), "PASSPORT No.", font=font(9), fill=LABEL)
    d.text((330, y + 42), "LN 4829137", font=font(13, bold=True), fill=INK)

    # the telling detail: No Paws Clause notice (sized to its text)
    ny = 540
    d.rectangle([48, ny, 492, ny + 70], outline=NAVY, width=1)
    d.rectangle([48, ny, 492, ny + 22], fill=NAVY)
    d.text((58, ny + 4), "NOTICE", font=font(12, bold=True), fill=(255, 255, 255))
    notice = ("Furry activity is prohibited in Leonida under the No Paws "
              "Clause (2026). Report sightings to the Anti-Furry "
              "Association. Licensed hunters are authorised to act.")
    # wrap to box width
    nf = font(12)
    words, lines, cur = notice.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if text_w(d, trial, nf) <= 424:
            cur = trial
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    for i, ln in enumerate(lines):
        d.text((58, ny + 28 + i * 17), ln, font=nf, fill=INK)

    # observations box (fills the data page like a real passport)
    oy = 626
    d.rectangle([48, oy, 492, oy + 84], outline=RULE, width=1)
    d.text((58, oy + 8), "OBSERVATIONS", font=font(10, bold=True), fill=NAVY)
    d.text((58, oy + 26), "1. Holder is a registered resident of Vice City, "
           "Leonida.", font=font(11), fill=INK)
    d.text((58, oy + 44), "2. Valid for travel to all territories of the "
           "Republic of Leonida.", font=font(11), fill=INK)
    d.text((58, oy + 62), "3. Emergency assistance: Leonida Department of "
           "State, Vice City.", font=font(11), fill=INK)

    # property line
    d.text((270, 748), "THIS PASSPORT IS THE PROPERTY OF THE REPUBLIC OF "
           "LEONIDA", font=font(10, bold=True), fill=LABEL, anchor="ma")
    d.text((270, 764), "IF FOUND, PLEASE RETURN IT TO THE NEAREST LEONIDA "
           "CONSULATE", font=font(10), fill=LABEL, anchor="ma")

    # MRZ strip
    mz = 840
    d.rectangle([28, mz, 510, 996], fill=(255, 255, 255))
    d.line([(28, mz), (510, mz)], fill=NAVY, width=2)
    mf = font(15, mono=True)
    d.text((48, mz + 22), mrz_line1(), font=mf, fill=INK)
    d.text((48, mz + 56), mrz_line2(), font=mf, fill=INK)
    d.text((492, 972), "1", font=font(11), fill=LABEL, anchor="ra")

    # --- RIGHT: stamps page ------------------------------------------------
    d.text((755, 48), "VISAS", font=font(15, bold=True), fill=NAVY,
           anchor="ma")
    d.line([(534, 76), (976, 76)], fill=NAVY, width=1)

    stamps = [
        ("VICE CITY INTL", "DEPARTED", "02 JUN 2024", BLUE_INK, "rect", -6),
        ("PORT GELLHORN", "ARRIVED", "02 JUN 2024", RED_INK, "rect", 5),
        ("PORT GELLHORN", "DEPARTED", "09 JUN 2024", PURPLE_INK, "round", 7),
        ("LEONIDA KEYS", "ARRIVED", "09 JUN 2024", GREEN_INK, "rect", -5),
        ("LEONIDA KEYS", "DEPARTED", "16 JUN 2024", RED_INK, "round", -7),
        ("VICE CITY INTL", "ARRIVED", "16 JUN 2024", BLUE_INK, "rect", 4),
    ]
    # 2 cols x 3 rows; rect stamps 208x118, round ~176 diameter
    cells = [(534, 100), (758, 100), (534, 340), (758, 340), (534, 580),
             (758, 580)]
    for (place, action, date, color, kind, angle), (cx0, cy0) in zip(stamps,
                                                                     cells):
        if kind == "rect":
            st = make_rect_stamp(place, action, date, color, rng, angle)
        else:
            st = make_round_stamp(place, action, date, color, rng, angle)
        img.paste(st, (cx0, cy0), st)

    # fee stamp, bottom of the stamps page
    fee = make_fee_stamp(rng, -9)
    img.paste(fee, (600, 830), fee)
    d = ImageDraw.Draw(img)
    d.text((976, 972), "2", font=font(11), fill=LABEL, anchor="ra")
    return img


def main():
    out = "/output/entry.png" if os.path.isdir("/output") else os.path.join(
        BASE, "entry.png")
    img = build()
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} {img.size} {os.path.getsize(out)} bytes")


if __name__ == "__main__":
    main()
