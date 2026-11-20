#!/usr/bin/env python3
"""Typeset the front page for Friday 20 November 2026.

Usage: python3 tools/render.py /path/to/entry.png

One page, the whole day: a broadsheet front page that sums up the world
news of Friday 20 November 2026 in a single 1024x1024 image - a lead
story beside a dotted world map of the day's datelines, a day-in-numbers
band, eight illustrated story panels, and an also-today strip.

Every item is drawn from reporting first published on 20 November 2026
(or, for the three one-line briefs, from the morning news cycle of that
day); the tables below are the whole editorial input and the drawing code
adds no facts of its own. Figures are as reported that day; estimates are
labelled as estimates.

Deterministic: fixed fonts, fixed geometry, no clocks, no randomness,
no network. The same edition renders byte-identically on every run.
"""

import sys

from PIL import Image, ImageDraw, ImageFont

W = 1024
H = 1024
MARGIN = 36
INNER = W - 2 * MARGIN

PAPER = (250, 247, 240)
INK = (26, 24, 20)
BODY = (52, 48, 40)
ACCENT = (150, 30, 30)
RULE = (26, 24, 20)
DIV = (203, 195, 180)
FAINT = (110, 102, 90)
MAPDOT = (168, 158, 140)
BAND = (26, 24, 20)
BANDTXT = (250, 247, 240)
BANDSUB = (206, 198, 182)
SKY = (214, 228, 238)
SEA = (180, 205, 220)
LAND = (232, 222, 200)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = f"{FONT_DIR}/DejaVuSerif.ttf"
SERIF_B = f"{FONT_DIR}/DejaVuSerif-Bold.ttf"
SANS = f"{FONT_DIR}/DejaVuSans.ttf"
SANS_B = f"{FONT_DIR}/DejaVuSans-Bold.ttf"

WEEKDAY = "FRIDAY"
DATELINE = "20 NOVEMBER 2026"

LEAD_KICKER = "WASHINGTON \u00b7 THE LEAD"
LEAD_HEADLINE = "Trump puts Iran decision off to 2027"
LEAD_TEXT = (
    "The president says there is no rush on a decision over Iran, and "
    "that he will \u201csee what happens\u201d after 1 January, pushing "
    "any call on military action into next year. The remarks cap a week "
    "of war warnings from Washington."
)

NUMBERS = [
    ("300,000", "people evacuated\nas Akvan lands"),
    ("$1.84bn", "GTA VI launch-day\nsales, estimated"),
    ("1", "light-day: Voyager 1's\ndistance from Earth"),
    ("98", "drones fired at\nUkraine in one day"),
    ("423", "rescue teams\ndeployed in Odisha"),
    ("$120bn", "adaptation finance\nfloor in COP31 draft"),
]

# Each panel: (kicker, headline, brief, illustration key).
PANELS = [
    ("ODISHA \u00b7 WEATHER", "Cyclone Akvan bears down",
     "The storm reaches India's east coast on Friday; schools shut, "
     "300,000 people moved out of its path.", "cyclone"),
    ("SPACE", "Voyager 1, a light-day out",
     "NASA confirms its probe has travelled one light-day from Earth, "
     "49 years after launch.", "voyager"),
    ("SPACE", "Engine trouble ends asteroid landing",
     "Japan's Hayabusa2 abandons its asteroid landing after engine "
     "trouble forces a change of plan.", "asteroid"),
    ("CULTURE", "GTA VI passes $1.84bn",
     "Sensor Tower puts launch-day sales at 19m copies, past The "
     "Odyssey's $1.805bn box office. Estimates only.", "vicecity"),
    ("EUROPE", "Europe open to Russia talks",
     "European leaders say they are ready for talks with Moscow on "
     "ending the war in Ukraine.", "talks"),
    ("KYIV \u00b7 UKRAINE", "EU summons envoy over Kyiv strikes",
     "Russian strikes damaged the Austrian and Dutch embassies; one "
     "person was killed. No staff were hurt.", "embassy"),
    ("ANTALYA \u00b7 CLIMATE", "COP31's final day, no fossil deal",
     "The summit closes today; the latest draft drops every mention "
     "of fossil fuels. Nearly 200 nations must agree.", "climate"),
    ("UNICEF", "World Children's Day",
     "UNICEF marks 20 November with the theme \u201cMy day. My rights. "
     "My future.\u201d \u2014 and a children's manifesto on AI.", "children"),
]

BRIEFS = [
    "Riyadh's PIF Tower hit in a Houthi strike, windows blown out across seven floors",
    "World court rules Myanmar committed genocide against the Rohingya; celebrations in the camps",
    "A Van Gogh sells for a record $190.4m after a row over its Nazi-era history",
]

# Coarse dotted world map, one character per dot cell. '#' is land.
MAP_ROWS = [
    "                                                                ",
    "        #######                                                 ",
    "     ###########      ##     ##########  ##################     ",
    "   #############    ####   ############ ####################    ",
    "  ##############    ####  ###############################       ",
    "   ############      ##    #############################        ",
    "    ##########              ##########################          ",
    "     ########                ###  #################             ",
    "      ######                  ##    ##############              ",
    "       #####                        ############                ",
    "       ####                          ##########                 ",
    "       ###                            ########                  ",
    "      ####                             ######                   ",
    "      ###                               ####        ##          ",
    "     ####                               ###        ####         ",
    "     ###                                                ##      ",
    "                                                                ",
]
# (column, row, label, label dx, label dy) markers on the map grid above.
# Kyiv and Antalya sit almost on top of each other, so their labels go
# to opposite sides of their dots.
MARKERS = [(10, 4, "WASHINGTON", 7, -6), (45, 6, "ODISHA", 7, -6),
           (33, 3, "KYIV", -38, -6), (31, 4, "ANTALYA", 7, 8)]


def wrap(draw, text, font, width):
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=font) <= width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit(draw, text, path, size, width, max_lines):
    while size > 9:
        font = ImageFont.truetype(path, size)
        if len(wrap(draw, text, font, width)) <= max_lines:
            return font
        size -= 1
    return ImageFont.truetype(path, size)


def centered(draw, text, font, y, fill):
    x = (W - draw.textlength(text, font=font)) / 2
    draw.text((x, y), text, font=font, fill=fill)


def draw_masthead(draw):
    y = 20
    kicker_font = ImageFont.truetype(SANS_B, 19)
    centered(draw, "THE DAY IN BRIEF \u00b7 THE WORLD ON ONE PAGE", kicker_font, y, ACCENT)
    y += 28
    title_font = ImageFont.truetype(SERIF_B, 46)
    centered(draw, f"{WEEKDAY} {DATELINE}", title_font, y, INK)
    y += 58
    draw.rectangle([MARGIN, y, W - MARGIN, y + 5], fill=RULE)
    draw.rectangle([MARGIN, y + 9, W - MARGIN, y + 11], fill=RULE)
    return y + 20


def draw_map(draw, x, y, w):
    # Dotted continents with red dateline markers.
    cols = len(MAP_ROWS[0])
    rows = len(MAP_ROWS)
    cell = w / cols
    for r, row in enumerate(MAP_ROWS):
        for c, ch in enumerate(row):
            if ch == "#":
                cx = x + c * cell + cell / 2
                cy = y + r * cell + cell / 2
                draw.ellipse([cx - 1.6, cy - 1.6, cx + 1.6, cy + 1.6], fill=MAPDOT)
    label_font = ImageFont.truetype(SANS_B, 10)
    for c, r, label, dx, dy in MARKERS:
        cx = x + c * cell + cell / 2
        cy = y + r * cell + cell / 2
        draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=ACCENT)
        draw.text((cx + dx, cy + dy), label, font=label_font, fill=ACCENT)
    return y + int(rows * cell)


def draw_lead(draw, top):
    text_w = 580
    kicker_font = ImageFont.truetype(SANS_B, 16)
    draw.text((MARGIN, top), LEAD_KICKER, font=kicker_font, fill=ACCENT)
    headline_font = fit(draw, LEAD_HEADLINE, SERIF_B, 36, text_w, 2)
    y = top + 24
    for line in wrap(draw, LEAD_HEADLINE, headline_font, text_w):
        draw.text((MARGIN, y), line, font=headline_font, fill=INK)
        y += 40
    body_font = ImageFont.truetype(SERIF, 15)
    y += 2
    for line in wrap(draw, LEAD_TEXT, body_font, text_w):
        draw.text((MARGIN, y), line, font=body_font, fill=BODY)
        y += 21
    map_x = MARGIN + text_w + 28
    map_bottom = draw_map(draw, map_x, top + 4, INNER - text_w - 28)
    cap_font = ImageFont.truetype(SANS, 11)
    draw.text((map_x, map_bottom + 4), "WHERE THE DAY HAPPENED", font=cap_font, fill=FAINT)
    bottom = max(y, map_bottom + 22)
    draw.line([MARGIN, bottom + 6, W - MARGIN, bottom + 6], fill=DIV, width=1)
    return bottom + 14


def draw_numbers(draw, top):
    draw.rectangle([MARGIN, top, W - MARGIN, top + 68], fill=BAND)
    head_font = ImageFont.truetype(SANS_B, 11)
    draw.text((MARGIN + 12, top + 5), "THE DAY IN NUMBERS", font=head_font, fill=BANDSUB)
    col_w = INNER / len(NUMBERS)
    big_font = ImageFont.truetype(SERIF_B, 21)
    small_font = ImageFont.truetype(SANS, 9)
    for i, (big, small) in enumerate(NUMBERS):
        x = MARGIN + 12 + i * col_w
        draw.text((x, top + 19), big, font=big_font, fill=BANDTXT)
        for j, line in enumerate(small.split("\n")):
            draw.text((x, top + 45 + j * 11), line, font=small_font, fill=BANDSUB)
    return top + 76


def draw_cyclone(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SEA)
    cx, cy = x + w // 2, y + h // 2
    for r in (34, 26, 18, 10):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 20, 300, fill=(250, 247, 240), width=3)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=ACCENT)
    draw.polygon([(x, y + h), (x + w // 3, y + h - 14), (x + 2 * w // 3, y + h - 6), (x + w, y + h)],
                 fill=LAND)


def draw_voyager(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 26, 40))
    for sx, sy in ((18, 14), (52, 30), (150, 12), (196, 38), (120, 52), (30, 58), (180, 64)):
        draw.ellipse([x + sx - 1.5, y + sy - 1.5, x + sx + 1.5, y + sy + 1.5],
                     fill=(250, 247, 240))
    cx, cy = x + w // 2 + 30, y + h // 2 - 6
    draw.line([x + 30, y + h - 12, cx, cy], fill=(206, 198, 182), width=2)
    draw.ellipse([cx - 14, cy - 8, cx + 14, cy + 8], fill=(250, 247, 240), outline=INK)
    draw.line([cx + 14, cy, cx + 34, cy - 12], fill=(250, 247, 240), width=2)
    draw.line([cx - 10, cy + 8, cx - 26, cy + 22], fill=(250, 247, 240), width=2)


def draw_asteroid(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(24, 26, 40))
    pts = [(x + 60, y + 16), (x + 130, y + 12), (x + 168, y + 34), (x + 156, y + 62),
           (x + 104, y + 72), (x + 66, y + 58), (x + 52, y + 34)]
    draw.polygon(pts, fill=(150, 140, 126))
    for cx, cy, r in ((92, 34, 6), (128, 46, 8), (104, 56, 4)):
        draw.ellipse([x + cx - r, y + cy - r, x + cx + r, y + cy + r], fill=(110, 100, 86))
    draw.rectangle([x + 168, y + 58, x + 188, y + 70], fill=(250, 247, 240))
    draw.line([x + 178, y + 58, x + 178, y + 44], fill=(250, 247, 240), width=2)


def draw_vicecity(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 176, 120))
    draw.ellipse([x + w // 2 - 24, y + 8, x + w // 2 + 24, y + 56], fill=(255, 220, 120))
    for bx, bw, bh in ((8, 34, 34), (52, 26, 48), (88, 40, 28), (138, 30, 44), (178, 34, 30)):
        draw.rectangle([x + bx, y + h - bh, x + bx + bw, y + h], fill=(60, 30, 60))
    for wx in (16, 28, 60, 70, 96, 110, 146, 158, 186, 198):
        draw.rectangle([x + wx, y + h - 26, x + wx + 5, y + h - 20], fill=(255, 220, 120))


def draw_talks(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 228, 238))
    cx, cy = x + w // 2, y + h // 2 - 4
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(30, 60, 130))
    for k in range(12):
        import math
        ang = math.pi * 2 * k / 12
        sx, sy = cx + 24 * math.cos(ang), cy + 24 * math.sin(ang)
        draw.ellipse([sx - 2.5, sy - 2.5, sx + 2.5, sy + 2.5], fill=(255, 220, 60))
    draw.rectangle([x + 30, y + h - 18, x + w - 30, y + h - 12], fill=(120, 90, 60))


def draw_embassy(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    draw.rectangle([x + 60, y + 22, x + 160, y + h], fill=(232, 222, 200), outline=INK)
    for fx in (76, 106, 136):
        draw.rectangle([x + fx, y + 34, x + fx + 12, y + 52], fill=(90, 110, 140))
    draw.rectangle([x + 100, y + 58, x + 122, y + h], fill=(120, 90, 60))
    draw.line([x + 60, y + 22, x + 60, y + 8], fill=INK, width=2)
    draw.polygon([(x + 60, y + 8), (x + 82, y + 13), (x + 60, y + 18)], fill=ACCENT)
    draw.line([x + 160, y + 22, x + 160, y + 8], fill=INK, width=2)
    draw.polygon([(x + 160, y + 8), (x + 182, y + 13), (x + 160, y + 18)], fill=(200, 60, 40))
    draw.line([x + 84, y + 30, x + 96, y + 48], fill=ACCENT, width=2)
    draw.line([x + 96, y + 48, x + 108, y + 30], fill=ACCENT, width=2)


def draw_climate(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SKY)
    cx, cy = x + w // 2, y + h // 2
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], fill=(90, 150, 200))
    draw.ellipse([cx - 34, cy - 34, cx + 34, cy + 34], outline=INK)
    draw.arc([cx - 20, cy - 34, cx + 20, cy + 34], 270, 90, fill=(200, 230, 240), width=3)
    draw.arc([cx - 34, cy - 12, cx + 34, cy + 12], 0, 360, fill=(200, 230, 240), width=2)
    draw.polygon([(cx - 8, cy - 6), (cx + 12, cy - 14), (cx + 6, cy + 8)], fill=(120, 180, 90))
    draw.ellipse([cx + 46, cy - 30, cx + 62, cy - 14], fill=(255, 220, 120))


def draw_children(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(255, 236, 200))
    for i, col in enumerate(((150, 30, 30), (30, 90, 150), (40, 130, 70))):
        fx = x + 56 + i * 56
        draw.ellipse([fx - 13, y + 12, fx + 13, y + 38], fill=col)
        draw.polygon([(fx - 16, y + h), (fx - 12, y + 40), (fx + 12, y + 40), (fx + 16, y + h)],
                     fill=col)
    draw.rectangle([x + w - 52, y + 10, x + w - 14, y + 34], fill=(30, 60, 130))
    draw.ellipse([x + w - 40, y + 16, x + w - 26, y + 28], fill=(255, 220, 120))


ILLUSTRATIONS = {
    "cyclone": draw_cyclone,
    "voyager": draw_voyager,
    "asteroid": draw_asteroid,
    "vicecity": draw_vicecity,
    "talks": draw_talks,
    "embassy": draw_embassy,
    "climate": draw_climate,
    "children": draw_children,
}


def draw_panel(draw, kicker, headline, brief, art, x, y, w):
    ILLUSTRATIONS[art](draw, x, y, w, 92)
    ty = y + 100
    kick_font = ImageFont.truetype(SANS_B, 10)
    draw.text((x, ty), kicker, font=kick_font, fill=ACCENT)
    ty += 15
    head_font = fit(draw, headline, SANS_B, 14, w, 2)
    for line in wrap(draw, headline, head_font, w):
        draw.text((x, ty), line, font=head_font, fill=INK)
        ty += 16
    brief_font = fit(draw, brief, SERIF, 11, w, 4)
    ty += 2
    for line in wrap(draw, brief, brief_font, w):
        draw.text((x, ty), line, font=brief_font, fill=BODY)
        ty += 13
    return ty


def draw_grid(draw, top):
    gap = 18
    col_w = (INNER - 3 * gap) // 4
    row_h = 244
    for row in range(2):
        y = top + row * (row_h + 14)
        for col in range(4):
            panel = PANELS[row * 4 + col]
            x = MARGIN + col * (col_w + gap)
            draw_panel(draw, panel[0], panel[1], panel[2], panel[3], x, y, col_w)
        if row == 0:
            draw.line([MARGIN, y + row_h + 4, W - MARGIN, y + row_h + 4], fill=DIV, width=1)
    return top + 2 * row_h + 14


def draw_briefs(draw, top):
    head_font = ImageFont.truetype(SANS_B, 13)
    draw.text((MARGIN, top), "ALSO TODAY", font=head_font, fill=ACCENT)
    font = ImageFont.truetype(SANS, 12)
    y = top + 20
    x = MARGIN
    for item in BRIEFS:
        text = item + "   \u00b7   "
        width = draw.textlength(text, font=font)
        if x + width > W - MARGIN:
            y += 17
            x = MARGIN
        draw.text((x, y), text, font=font, fill=BODY)
        x += width
    return y + 17


def draw_footer(draw):
    top = H - 34
    draw.rectangle([MARGIN, top, W - MARGIN, top + 2], fill=RULE)
    colophon = "Compiled from the day's reporting \u00b7 One page, the whole day \u00b7 No story here is invented; figures as reported that day"
    font = ImageFont.truetype(SANS, 12)
    y = top + 8
    x = (W - draw.textlength(colophon, font=font)) / 2
    draw.text((x, y), colophon, font=font, fill=FAINT)


def main():
    out_path = sys.argv[1]
    page = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(page)
    y = draw_masthead(draw)
    y = draw_lead(draw, y)
    y = draw_numbers(draw, y)
    y = draw_grid(draw, y + 2)
    draw_briefs(draw, y + 4)
    draw_footer(draw)
    page.save(out_path, format="PNG", optimize=True)
    print("wrote", out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
