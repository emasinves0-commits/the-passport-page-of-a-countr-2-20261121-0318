#!/usr/bin/env python3
"""Draw the Republic of Leonida passport spread (v3) to entry.png.

1024x1024 open passport spread: data page (left) + visas page (right).
Photographic portrait composited from portrait.png; all other art is drawn
in code. Deterministic: no randomness, no timestamps.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "fonts")

# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (26, 46, 43)
TEAL = (15, 76, 74)
TEAL_DARK = (13, 51, 47)
GREY = (110, 105, 90)
RED = (163, 51, 39)
BLUE = (43, 90, 166)
GREEN = (46, 125, 79)
FEE_RED = (156, 58, 46)
SIGN_BLUE = (35, 62, 120)

W, H = 1024, 1024


def F(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


# ---------------------------------------------------------------- MRZ (ICAO 9303)
WEIGHTS = (7, 3, 1)


def _val(ch):
    if ch == "<":
        return 0
    if ch.isdigit():
        return int(ch)
    return ord(ch) - 55  # A=10 .. Z=35


def check_digit(text):
    total = 0
    for i, ch in enumerate(text):
        total += _val(ch) * WEIGHTS[i % 3]
    return str(total % 10)


def mrz_lines():
    # TD3: two lines of 44 characters.
    line1 = "P<LEOMARLOWE<<ELENA<ROSA"
    line1 = line1 + "<" * (44 - len(line1))
    doc = "LEO482910"
    nat = "LEO"
    dob = "980512"
    sex = "F"
    exp = "340313"
    pers = "9805124821<<<<"
    c_doc = check_digit(doc)
    c_dob = check_digit(dob)
    c_exp = check_digit(exp)
    c_pers = check_digit(pers)
    # Composite covers line-2 positions 1-10, 14-20, 22-43: it includes the
    # individual check digits but EXCLUDES nationality and sex (ICAO 9303).
    comp = check_digit(doc + c_doc + dob + c_dob + exp + c_exp + pers + c_pers)
    line2 = (doc + c_doc + nat + dob + c_dob + sex + exp + c_exp
             + pers + c_pers + comp)
    assert len(line1) == 44 and len(line2) == 44, (len(line1), len(line2))
    return line1, line2


def _self_test_mrz():
    # Canonical ICAO 9303 TD3 specimen (Anna Maria Eriksson, Utopia):
    # L898902C3 -> 6, 740812 -> 2, 120415 -> 9, ZE184226B<<<<< -> 1,
    # composite -> 0; Part 4 appendix variant (expiry 340415) -> composite 6.
    assert check_digit("L898902C3") == "6"
    assert check_digit("740812") == "2"
    assert check_digit("120415") == "9"
    assert check_digit("ZE184226B<<<<<") == "1"
    comp = "L898902C36" + "7408122" + "1204159" + "ZE184226B<<<<<1"
    assert check_digit(comp) == "0"
    comp_b = "L898902C36" + "7408122" + "3404159" + "ZE184226B<<<<<1"
    assert check_digit(comp_b) == "6"
    l1, l2 = mrz_lines()
    assert l1.startswith("P<LEOMARLOWE<<ELENA<ROSA")
    assert l2.startswith("LEO482910")
    # re-verify every check digit of our own MRZ
    assert l2[9] == check_digit(l2[0:9])
    assert l2[19] == check_digit(l2[13:19])
    assert l2[27] == check_digit(l2[21:27])
    assert l2[42] == check_digit(l2[28:42])
    assert l2[43] == check_digit(l2[0:10] + l2[13:20] + l2[21:28] + l2[28:43])


# ---------------------------------------------------------------- helpers
def text_center(d, cx, y, s, font, fill):
    w = d.textlength(s, font=font)
    d.text((cx - w / 2, y), s, font=font, fill=fill)


def text_right(d, rx, y, s, font, fill):
    w = d.textlength(s, font=font)
    d.text((rx - w, y), s, font=font, fill=fill)


def spaced(s, n=2):
    return (" " * n).join(list(s))


def field(d, x, y, label, value, vsize=17, label_size=10):
    d.text((x, y), label, font=F("LiberationSans-Regular.ttf", label_size), fill=GREY)
    d.text((x, y + label_size + 3), value,
           font=F("LiberationSans-Bold.ttf", vsize), fill=INK)


def guilloche(base):
    """Faint wavy security lines + watermark rings over the whole spread."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for yy in range(24, H - 12, 15):
        pts = []
        for xx in range(14, W - 14, 16):
            pts.append((xx, yy + 3 * math.sin(xx / 47.0 + yy / 23.0)))
        od.line(pts, fill=(188, 176, 132, 42), width=1)
    for cx, cy in ((256, 780), (768, 470)):
        for r in (58, 86, 114):
            od.ellipse([cx - r, cy - r, cx + r, cy + r],
                       outline=(15, 76, 74, 24), width=2)
    base.alpha_composite(ov)


def emblem(d, cx, cy, r, color):
    """Circular seal: palm tree over waves with a small sun."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
    d.ellipse([cx - r + 4, cy - r + 4, cx + r - 4, cy + r - 4],
              outline=color, width=1)
    d.ellipse([cx + r * 0.34, cy - r * 0.72, cx + r * 0.62, cy - r * 0.44],
              fill=color)
    d.line([(cx - 2, cy + r * 0.62), (cx + 1, cy + r * 0.1),
            (cx + 4, cy - r * 0.28)], fill=color, width=3)
    for a0, a1 in ((195, 260), (225, 290), (255, 320), (285, 350), (315, 20)):
        d.arc([cx - r * 0.62, cy - r * 0.78, cx + r * 0.62, cy + r * 0.02],
              a0, a1, fill=color, width=2)
    for wy in (cy + r * 0.42, cy + r * 0.60):
        d.arc([cx - r * 0.55, wy - 7, cx - r * 0.05, wy + 7],
              200, 340, fill=color, width=2)
        d.arc([cx + r * 0.05, wy - 7, cx + r * 0.55, wy + 7],
              200, 340, fill=color, width=2)


def curved_text(base, cx, cy, radius, text, font, fill, start_deg, end_deg,
                flip=False):
    """Draw text along a circular arc (for round stamps)."""
    n = len(text)
    if n == 0:
        return
    span = end_deg - start_deg
    for i, ch in enumerate(text):
        ang = math.radians(start_deg + span * (i / max(n - 1, 1)))
        x = cx + radius * math.cos(ang)
        y = cy + radius * math.sin(ang)
        tile = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.text((20, 20), ch, font=font, fill=fill, anchor="mm")
        rot = math.degrees(ang) + (90 if not flip else -90)
        tile = tile.rotate(-rot, resample=Image.BICUBIC, center=(20, 20))
        base.alpha_composite(tile, (int(x - 20), int(y - 20)))


def rect_stamp(base, x, y, w, h, color, country, action, date, place, angle):
    """Rectangular entry/exit stamp, slightly rotated, on its own layer."""
    pad = 24
    layer = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([pad + 2, pad + 2, pad + w - 2, pad + h - 2],
                        radius=10, outline=color + (235,), width=3)
    d.rounded_rectangle([pad + 7, pad + 7, pad + w - 7, pad + h - 7],
                        radius=7, outline=color + (200,), width=1)
    cx = pad + w / 2
    text_center(d, cx, pad + 8, country,
                F("LiberationSans-Bold.ttf", 17), color + (235,))
    d.line([(pad + 14, pad + 32), (pad + w - 14, pad + 32)],
           fill=color + (200,), width=1)
    text_center(d, cx, pad + 37, action,
                F("LiberationSans-Bold.ttf", 15), color + (235,))
    text_center(d, cx, pad + 57, date,
                F("LiberationSans-Bold.ttf", 15), color + (235,))
    text_center(d, cx, pad + 76, place,
                F("LiberationSans-Regular.ttf", 10), color + (210,))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (x - pad, y - pad))


def round_fee_stamp(base, cx, cy, r, color, top_text, mid_text, bot_text,
                    angle):
    """Circular fee stamp with curved text, rotated as a whole."""
    pad = 14
    size = 2 * (r + pad)
    layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cc = r + pad
    d.ellipse([pad, pad, size - pad, size - pad],
              outline=color + (235,), width=3)
    d.ellipse([pad + 6, pad + 6, size - pad - 6, size - pad - 6],
              outline=color + (200,), width=1)
    curved_text(layer, cc, cc, r - 10, top_text,
                F("LiberationSans-Bold.ttf", 11), color + (235,),
                -168, -12)
    curved_text(layer, cc, cc, r - 10, bot_text,
                F("LiberationSans-Bold.ttf", 10), color + (235,),
                168, 12, flip=True)
    text_center(d, cc, cc - 24, mid_text.split(" ")[0],
                F("LiberationSans-Bold.ttf", 16), color + (235,))
    text_center(d, cc, cc - 2, " ".join(mid_text.split(" ")[1:]) or mid_text,
                F("LiberationSans-Bold.ttf", 20), color + (235,))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=False)
    base.alpha_composite(layer, (cx - cc, cy - cc))


def draw_data_page(img, portrait):
    d = ImageDraw.Draw(img)
    # passport number, top right
    text_right(d, 498, 22, "LEO482910",
               F("LiberationSans-Bold.ttf", 15), TEAL)
    # emblem + headers
    emblem(d, 256, 56, 26, TEAL)
    text_center(d, 256, 92, "REPÚBLICA DE LEÓNIDA",
                F("LiberationSerif-Bold.ttf", 27), TEAL_DARK)
    text_center(d, 256, 124, spaced("REPUBLIC OF LEONIDA", 1),
                F("LiberationSerif-Regular.ttf", 13), INK)
    text_center(d, 256, 143, spaced("PASAPORTE · PASSPORT", 1),
                F("LiberationSans-Bold.ttf", 11), TEAL)
    d.line([(24, 162), (500, 162)], fill=TEAL, width=2)

    # photo (3:4 crop, centred on the face)
    pw, ph = 148, 196
    px, py = 28, 176
    crop = portrait.crop((86, 60, 426, 513)).resize((pw, ph), Image.LANCZOS)
    img.paste(crop, (px, py))
    d.rectangle([px, py, px + pw, py + ph], outline=INK, width=1)
    d.text((px, py + ph + 6), "FOTOGRAFÍA / PHOTOGRAPH",
           font=F("LiberationSans-Regular.ttf", 8), fill=GREY)
    # signature under the photo (kept short so it clears the field column)
    d.text((px, 398), "Elena Marlowe",
           font=F("LiberationSans-Italic.ttf", 19), fill=SIGN_BLUE)
    d.line([(px, 424), (px + 148, 424)], fill=GREY, width=1)
    d.text((px, 428), "FIRMA DEL TITULAR / HOLDER'S SIGNATURE",
           font=F("LiberationSans-Regular.ttf", 8), fill=GREY)

    # fields, right of the photo
    fx = 192
    field(d, fx, 176, "TIPO / TYPE", "P", 17)
    field(d, 262, 176, "CÓDIGO / CODE", "LEO", 17)
    field(d, 352, 176, "PASAPORTE / PASSPORT NO.", "LEO482910", 17)
    field(d, fx, 220, "APELLIDOS / SURNAME", "MARLOWE", 20)
    field(d, fx, 264, "NOMBRES / GIVEN NAMES", "ELENA ROSA", 20)
    field(d, fx, 308, "NACIONALIDAD / NATIONALITY", "LEONIDESA", 17)
    field(d, 392, 308, "SEXO / SEX", "F", 17)
    field(d, fx, 352, "FECHA DE NACIMIENTO / DATE OF BIRTH", "12 MAY 1998", 17)
    field(d, fx, 396, "LUGAR DE NACIMIENTO / PLACE OF BIRTH",
          "VICE CITY, LEONIDA", 15)
    field(d, fx, 440, "EXPEDICIÓN / DATE OF ISSUE", "14 MAR 2024", 16)
    field(d, 352, 440, "CADUCIDAD / DATE OF EXPIRY", "13 MAR 2034", 16)
    field(d, fx, 484, "AUTORIDAD / AUTHORITY", "PASSPORT OFFICE, VICE CITY", 14)
    field(d, fx, 528, "N.º PERSONAL / PERSONAL NO.", "980512-4821", 16)
    field(d, 352, 528, "OCUPACIÓN / OCCUPATION", "AIRBOAT GUIDE", 15)

    # observations box (drawn first so the ghost portrait sits on top of it)
    d.rectangle([28, 584, 500, 656], outline=TEAL, width=1,
                fill=(239, 232, 210))
    d.text((40, 594), "OBSERVACIONES / OBSERVATIONS",
           font=F("LiberationSans-Bold.ttf", 11), fill=TEAL)
    d.text((40, 614), "Holder is a licensed airboat guide, licence AG-2210.",
           font=F("LiberationSans-Regular.ttf", 13), fill=INK)
    d.text((40, 634), "Everglades transit endorsement on page 3.",
           font=F("LiberationSans-Regular.ttf", 13), fill=INK)

    # ghost portrait, faded, over the right end of the observations box
    ghost = portrait.crop((86, 60, 426, 513)).resize((64, 86), Image.LANCZOS)
    ghost = ghost.convert("RGBA")
    ghost.putalpha(Image.new("L", ghost.size, 70))
    img.alpha_composite(ghost, (424, 584))
    d = ImageDraw.Draw(img)

    # visa-free box
    d.rectangle([28, 676, 500, 736], outline=TEAL, width=1)
    d.text((40, 686), "VISA-FREE TRAVEL — CAYO VERDE · ISLA DEL NORTE · 90 DAYS",
           font=F("LiberationSans-Bold.ttf", 11), fill=TEAL)
    d.text((40, 708), "Issued at Vice City, 14 MAR 2024. See conditions on page 3.",
           font=F("LiberationSans-Regular.ttf", 12), fill=INK)

    # MRZ strip
    l1, l2 = mrz_lines()
    d.rectangle([28, 876, 500, 956], outline=TEAL, width=1,
                fill=(251, 248, 239))
    mono = F("DejaVuSansMono.ttf", 16)
    d.text((40, 888), l1, font=mono, fill=INK)
    d.text((40, 918), l2, font=mono, fill=INK)
    d.text((28, 972), "2", font=F("LiberationSans-Regular.ttf", 12), fill=GREY)


def draw_visa_page(img):
    d = ImageDraw.Draw(img)
    x0, x1 = 524, 1000
    # header
    d.text((x0, 28), "VISAS", font=F("LiberationSerif-Bold.ttf", 26),
           fill=TEAL_DARK)
    d.text((x0 + 108, 34), "· VISADOS",
           font=F("LiberationSerif-Regular.ttf", 16), fill=INK)
    text_right(d, x1, 30, "3", F("LiberationSans-Regular.ttf", 14), GREY)
    d.line([(x0, 62), (x1, 62)], fill=TEAL, width=2)
    d.text((x0, 72), spaced("ENTRY AND EXIT STAMPS — TRAVEL HISTORY", 1),
           font=F("LiberationSans-Regular.ttf", 10), fill=GREY)

    # endorsement box
    d.rectangle([x0, 94, x1, 232], outline=TEAL, width=2,
                fill=(239, 232, 210))
    d.text((x0 + 12, 104), "EVERGLADES TRANSIT ENDORSEMENT",
           font=F("LiberationSans-Bold.ttf", 13), fill=TEAL)
    d.text((x0 + 12, 124), "ENDORSO DE TRÁNSITO · ISSUED VICE CITY 14 MAR 2024",
           font=F("LiberationSans-Regular.ttf", 10), fill=GREY)
    for i, line in enumerate((
            "Airboat crossings of the Alligator Alley waterway are",
            "permitted 01 NOV – 30 APR only. Bearer must report to",
            "the Waterway Warden before each crossing. Valid with",
            "airboat guide licence AG-2210.")):
        d.text((x0 + 12, 146 + i * 18), line,
               font=F("LiberationSans-Regular.ttf", 13), fill=INK)

    # circular fee stamp overlapping the endorsement box corner
    round_fee_stamp(img, 930, 196, 54, FEE_RED,
                    "GATOR CROSSING FEE", "PAID $5", "14 MAR 2024", -12)

    # stamps: two trips, entry/exit pairs, colour-coded by country
    stamps = [
        (RED, "LEONIDA", "DEPARTURE", "02 JUN 2024", "VICE CITY", -2),
        (BLUE, "CAYO VERDE", "ARRIVAL", "02 JUN 2024", "PORT VERDE", 1.5),
        (BLUE, "CAYO VERDE", "DEPARTURE", "15 JUN 2024", "PORT VERDE", 2),
        (RED, "LEONIDA", "ARRIVAL", "16 JUN 2024", "VICE CITY", -1),
        (RED, "LEONIDA", "DEPARTURE", "08 FEB 2025", "VICE CITY", 1),
        (GREEN, "ISLA DEL NORTE", "ARRIVAL", "09 FEB 2025", "PUERTO NORTE", -2),
        (GREEN, "ISLA DEL NORTE", "DEPARTURE", "21 FEB 2025", "PUERTO NORTE", -1.5),
        (RED, "LEONIDA", "ARRIVAL", "22 FEB 2025", "VICE CITY", 2),
    ]
    for i, (color, country, action, date, place, angle) in enumerate(stamps):
        sx = x0 + (i % 2) * 240
        sy = 252 + (i // 2) * 104
        rect_stamp(img, sx, sy, 228, 92, color, country, action, date,
                   place, angle)

    # visitor visa box
    d.rectangle([x0, 682, x1, 800], outline=TEAL, width=1)
    d.rectangle([x0, 682, x1, 708], fill=TEAL)
    d.text((x0 + 12, 688), "CAYO VERDE · VISITOR VISA · VISADO DE VISITANTE",
           font=F("LiberationSans-Bold.ttf", 12), fill=(246, 241, 227))
    field(d, x0 + 12, 718, "TYPE / TIPO", "C · SINGLE ENTRY", 14)
    field(d, x0 + 252, 718, "DURATION OF STAY / DURACIÓN", "30 DAYS", 14)
    field(d, x0 + 12, 758, "VALID FROM / VÁLIDO DESDE", "01 JUN 2024", 14)
    field(d, x0 + 252, 758, "UNTIL / HASTA", "30 JUN 2024", 14)
    d.text((x0 + 12, 786), "ISSUED AT VICE CITY, 18 MAY 2024   ·   FEE $25",
           font=F("LiberationSans-Regular.ttf", 11), fill=GREY)

    # conditions of issue
    d.rectangle([x0, 820, x1, 920], outline=TEAL, width=1)
    d.rectangle([x0, 820, x1, 846], fill=TEAL)
    d.text((x0 + 12, 826), "CONDITIONS OF ISSUE / CONDICIONES",
           font=F("LiberationSans-Bold.ttf", 12), fill=(246, 241, 227))
    for i, line in enumerate((
            "The bearer must report to the Waterway Warden within 24 hours",
            "of landing in Leonida. The Alligator Alley waterway is closed",
            "01 MAY – 31 OCT without a permit. No. LEO482910 · Fee paid.")):
        d.text((x0 + 12, 854 + i * 18), line,
               font=F("LiberationSans-Regular.ttf", 12), fill=INK)

    # footer
    d.text((x0, 948), "This passport remains the property of the Republic of Leonida.",
           font=F("LiberationSans-Italic.ttf", 11), fill=GREY)
    text_right(d, x1, 972, "LEO482910",
               F("LiberationSans-Bold.ttf", 12), TEAL)


def main():
    _self_test_mrz()
    img = Image.new("RGBA", (W, H), TEAL_DARK)
    d = ImageDraw.Draw(img)
    # pages
    d.rectangle([10, 10, 506, 1014], fill=PAPER)
    d.rectangle([518, 10, 1014, 1014], fill=PAPER)
    # spine shadow
    for i in range(6):
        d.line([(512 - i, 10), (512 - i, 1014)], fill=(0, 0, 0, 26 - i * 4))
        d.line([(512 + i, 10), (512 + i, 1014)], fill=(0, 0, 0, 26 - i * 4))
    guilloche(img)
    portrait = Image.open(os.path.join(HERE, "portrait.png")).convert("RGB")
    draw_data_page(img, portrait)
    draw_visa_page(img)
    out = os.path.join(HERE, "entry.png")
    img.convert("RGB").save(out, optimize=True)
    print("wrote", out)


if __name__ == "__main__":
    main()
