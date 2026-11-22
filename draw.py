#!/usr/bin/env python3
"""Draw the front page of THE WORLD TODAY for Sunday 22 November 2026.

Renders one 1024x1024 newspaper front page with Pillow: masthead, a COP31
lead, two sub-lead items, three columns of region stories (37 stories,
7 regions), a UTC timeline and a date check. Deterministic: no clock,
no randomness, no network; the same input bytes always produce the same
PNG. Run: python3 draw.py  (writes entry.png next to this file).
"""

import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968

PAPER = (250, 246, 236)
INK = (22, 22, 22)
GREY = (105, 100, 92)
RED = (163, 30, 34)
BLUE = (28, 68, 120)
RULE = (60, 58, 52)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF = lambda s: font("DejaVuSerif.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit `width` px."""
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(draw, text, fnt, width, max_lines):
    """Wrap text, trimming to max_lines with an ellipsis if it overflows."""
    lines = wrap(draw, text, fnt, width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + " …", font=fnt) > width:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + " …"
    return lines


# ---------------------------------------------------------------- stories
# (region, headline, one-line summary, source)
STORIES = [
    # EUROPE
    ("EUROPE", "Russia's 400-drone barrage",
     "Ukraine suffers its largest attack of the year: 110 missiles and more than 400 drones.",
     "EVENTGRAPH"),
    ("EUROPE", "Missile hits Zelenskyy's hometown",
     "Russian strike on Kryvyi Rih kills two and wounds dozens; Ukraine hits a Russian ship.",
     "ONE TURN"),
    ("EUROPE", "Russian ship ablaze off Finland",
     "Russian-linked cargo vessel Sparta II catches fire after a suspected Ukrainian drone strike.",
     "DAILY BRIEF"),
    ("EUROPE", "Polish airspace violated",
     "Warsaw reports a Russian cruise missile crossing into its airspace.",
     "EVENTGRAPH"),
    ("EUROPE", "Denmark expels Russian attaché",
     "Copenhagen orders the diplomat out over an alleged plot.",
     "ONE TURN"),
    ("EUROPE", "'Killer robots' talks fail",
     "UN talks in Geneva end with no binding treaty on lethal autonomous weapons.",
     "DAILY BRIEF"),
    # MIDDLE EAST
    ("MIDDLE EAST", "Iran hits US bases in Bahrain",
     "Tehran strike damages a civilian industrial site; Guards claim US Navy positions hit.",
     "REUTERS"),
    ("MIDDLE EAST", "Two tankers hit near Hormuz",
     "Oil tankers struck close to the Strait of Hormuz as Iran tensions rise.",
     "DAILY BRIEF"),
    ("MIDDLE EAST", "Riyadh under missile fire",
     "Houthis fire ballistic missiles at the Saudi capital; coalition intercepts three.",
     "WORLD IN 90 SEC"),
    ("MIDDLE EAST", "Gaza strikes go on",
     "Israeli strikes continue in Gaza; an aid vehicle is hit.",
     "ONE TURN"),
    ("MIDDLE EAST", "Power station fire kills four",
     "Blaze at the Hartha plant near Basra injures 35; cause unknown.",
     "WORLD IN 90 SEC"),
    ("MIDDLE EAST", "Aoun blames Israel and Iran",
     "Lebanon's president says both threaten his country's sovereignty.",
     "ONE TURN"),
    # AMERICAS
    ("AMERICAS", "'El Chapo Isidro' captured",
     "Mexican forces arrest cartel boss Fausto Isidro Meza Flores; 11 killed in Sinaloa.",
     "ONE TURN"),
    ("AMERICAS", "AI sell-off drags US stocks",
     "S&P 500 falls 3.7% to 6,910 as chip shares slide; worst week since April 2025.",
     "ONE TURN"),
    ("AMERICAS", "Fed hike now priced in",
     "Traders see a near-certain quarter-point December rise; oil eases near $93.",
     "DAILY BRIEF"),
    ("AMERICAS", "Florida river breaks record",
     "St. Johns River tops a 73-year mark near Cocoa; floods may last into January.",
     "WORLD IN 90 SEC"),
    ("AMERICAS", "Trump orders contractors",
     "White House tells federal contractors to report congressional requests.",
     "ONE TURN"),
    ("AMERICAS", "GTA VI: $3.8bn in a day",
     "Grand Theft Auto VI sets a first-day sales record of $3.8 billion.",
     "NEWS MEDIA HOUSE"),
    # ASIA-PACIFIC
    ("ASIA-PACIFIC", "Hong Kong votes",
     "Election Committee polls: 856 candidates for 723 seats; turnout 93.55% by 2pm.",
     "CHINA DAILY"),
    ("ASIA-PACIFIC", "Trump, Xi, Putin meet",
     "Trilateral summit in Shenzhen agrees talks on nuclear risk reduction.",
     "ONE TURN"),
    ("ASIA-PACIFIC", "India 629/6 in Wellington",
     "Pant's 128 powers a record India total vs New Zealand; lead 261 on day four.",
     "REUTERS"),
    ("ASIA-PACIFIC", "EU-Indonesia deal signed",
     "Trade pact concluded after ten years of talks.",
     "ONE TURN"),
    ("ASIA-PACIFIC", "Toxic alcohol kills 11",
     "Eleven dead and 180 in hospital in Manipur after drinking illicit liquor.",
     "WORLD IN 90 SEC"),
    ("ASIA-PACIFIC", "SoftBank drops $1tn idea",
     "Masayoshi Son explored a buyout of SK Hynix, then shelved the plan.",
     "DAILY BRIEF"),
    ("ASIA-PACIFIC", "Google's Duplex joins Gemini",
     "Autonomous business calls come to Gemini App Tasks.",
     "EVENTGRAPH"),
    # AFRICA
    ("AFRICA", "Funeral boat capsizes: 24 dead",
     "Overcrowded boat sinks in Bayelsa, Nigeria, during a funeral trip.",
     "ONE TURN"),
    ("AFRICA", "Tinubu: end suicide crime",
     "Nigeria's president asks parliament to decriminalise attempted suicide.",
     "AFRICA FRONT PAGE"),
    ("AFRICA", "Landmine kills 22 in Sudan",
     "Civilians die when a blast hits a passenger vehicle in North Kordofan.",
     "EIN NEWS"),
    ("AFRICA", "Rebels seize Bau district",
     "Sudan's Tasis alliance takes the strategic Blue Nile locality.",
     "EIN NEWS"),
    ("AFRICA", "Al-Sisi demands reform",
     "Egypt's president calls for a fairer global financial system.",
     "AFRICA FRONT PAGE"),
    # MARKETS & TECH
    ("MARKETS & TECH", "MEXC named laundering risk",
     "US FinCEN designates the exchange; Binance may freeze its deposits.",
     "EVENTGRAPH"),
    ("MARKETS & TECH", "Spain extends bank levy",
     "Banking tax runs through 2027, raising €1.4bn before a snap election.",
     "DAILY BRIEF"),
    ("MARKETS & TECH", "UK and EU strike deals",
     "London and Brussels agree new pacts; Burnham eyes rejoining.",
     "ONE TURN"),
    ("MARKETS & TECH", "EU plastic ban begins",
     "Exports of plastic waste to non-OECD states stop from 21 November.",
     "DAILY EDITION"),
]

LEAD = {
    "kicker": "CLIMATE  ·  COP31  ·  ANTALYA, TÜRKIYE",
    "headline": "COP31 NEARS A DEAL",
    "summary": ("After two days of overtime, the UN climate summit's co-presidents table a "
                "last-minute package and call a Sunday plenary to approve it. Nearly 200 "
                "nations must still agree — and the text names no fossil fuels."),
    "sub": [
        ("FINAL TEXT OMITS FOSSIL FUELS",
         "Draft keeps an electrify goal and a carbon-capture push, but drops any phase-out language."),
        ("FINANCE FURY",
         "A $120bn adaptation target for poorer nations is cut from the draft; the Africa Group demands more."),
    ],
}

TIMELINE = [
    ("00:41 GMT", "India reach 629/6 at lunch in Wellington"),
    ("03:00 GMT", "COP31 objection deadline in Antalya"),
    ("06:00 GMT", "COP31 approval session opens"),
    ("09:00 HKT", "Hong Kong Election Committee polls open"),
    ("14:00 HKT", "Hong Kong turnout hits 93.55%"),
]

REGIONS = ["EUROPE", "MIDDLE EAST", "AMERICAS", "ASIA-PACIFIC", "AFRICA",
           "MARKETS & TECH"]
REGION_COLOR = {
    "EUROPE": (28, 68, 120),
    "MIDDLE EAST": (163, 30, 34),
    "AMERICAS": (120, 72, 8),
    "ASIA-PACIFIC": (16, 110, 80),
    "AFRICA": (110, 60, 130),
    "MARKETS & TECH": (90, 90, 90),
}


def draw_globe(draw, cx, cy, r):
    """Small line globe: circle, meridians, parallels, one red marker."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=INK, width=3)
    for k in (0.45, 0.85):
        rx = int(r * k)
        draw.ellipse([cx - rx, cy - r, cx + rx, cy + r], outline=INK, width=2)
    for dy in (-r // 2, 0, r // 2):
        half = int((r * r - dy * dy) ** 0.5)
        draw.line([cx - half, cy + dy, cx + half, cy + dy], fill=INK, width=2)
    mx, my = cx + int(r * 0.45), cy - int(r * 0.35)
    draw.ellipse([mx - 6, my - 6, mx + 6, my + 6], fill=RED, outline=INK, width=2)
    draw.text((mx + 10, my - 7), "ANTALYA", font=SANS_B(11), fill=RED)


def story_block(draw, x, y, width, headline, summary, source):
    """One story: bold headline (<=2 lines), summary (<=2 lines) with the
    source tag appended inline to its last line when it fits."""
    lines = fit_lines(draw, headline, SANS_B(12.5), width, 2)
    for ln in lines:
        draw.text((x, y), ln, font=SANS_B(12.5), fill=INK)
        y += 15
    lines = fit_lines(draw, summary, SANS(10), width, 2)
    for i, ln in enumerate(lines):
        draw.text((x, y), ln, font=SANS(10), fill=(52, 50, 46))
        if i == len(lines) - 1:
            tag = "  — " + source
            tw = draw.textlength(ln, font=SANS(10))
            if tw + draw.textlength(tag, font=SANS_B(8)) <= width:
                draw.text((x + tw, y + 1), tag, font=SANS_B(8), fill=GREY)
            else:
                draw.text((x, y + 12), "— " + source, font=SANS_B(8),
                          fill=GREY)
                y += 11
        y += 12
    return y + 2


def region_header(draw, x, y, width, name, color=None):
    c = color if color is not None else REGION_COLOR[name]
    draw.rectangle([x, y + 2, x + 11, y + 13], fill=c)
    draw.text((x + 17, y), name, font=SANS_B(15), fill=INK)
    draw.line([x, y + 20, x + width, y + 20], fill=RULE, width=1)
    return y + 25


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead
    d.text((W // 2, 20), "THE WORLD TODAY", font=SERIF_B(56), fill=INK,
           anchor="ma")
    d.text((W // 2, 86), "SUNDAY,  22  NOVEMBER  2026", font=SANS_B(18),
           fill=INK, anchor="ma")
    d.text((W // 2, 110), "37 STORIES  ·  7 REGIONS  ·  ANTALYA — KYIV — MANAMA — HONG KONG — WELLINGTON",
           font=SANS(11), fill=GREY, anchor="ma")
    d.line([MARGIN, 130, W - MARGIN, 130], fill=INK, width=3)
    d.line([MARGIN, 134, W - MARGIN, 134], fill=INK, width=1)

    # ---- lead story
    y = 146
    d.text((MARGIN, y), LEAD["kicker"], font=SANS_B(14), fill=RED)
    y += 21
    d.text((MARGIN, y), LEAD["headline"], font=SERIF_B(40), fill=INK)
    y += 50
    lead_w = 640
    for ln in wrap(d, LEAD["summary"], SANS(14), lead_w):
        d.text((MARGIN, y), ln, font=SANS(14), fill=(40, 38, 34))
        y += 18
    draw_globe(d, 830, 222, 70)

    # ---- sub-lead strip
    y = 306
    d.line([MARGIN, y, W - MARGIN, y], fill=RULE, width=1)
    y += 8
    col_w = (CW - 24) // 2
    for i, (head, summ) in enumerate(LEAD["sub"]):
        x = MARGIN + i * (col_w + 24)
        d.text((x, y), head, font=SANS_B(13), fill=RED)
        yy = y + 18
        for ln in wrap(d, summ, SANS(12), col_w):
            d.text((x, yy), ln, font=SANS(12), fill=(52, 50, 46))
            yy += 15
    y += 60
    d.line([MARGIN, y, W - MARGIN, y], fill=INK, width=2)

    # ---- body columns
    by_region = {r: [s for s in STORIES if s[0] == r] for r in REGIONS}
    columns = [
        ["EUROPE", "MIDDLE EAST"],
        ["AMERICAS", "ASIA-PACIFIC"],
        ["AFRICA", "MARKETS & TECH"],
    ]
    col_w = (CW - 2 * 24) // 3
    top = y + 10
    for ci, regs in enumerate(columns):
        x = MARGIN + ci * (col_w + 24)
        cy = top
        for reg in regs:
            cy = region_header(d, x, cy, col_w, reg)
            for _, head, summ, src in by_region[reg]:
                cy = story_block(d, x, cy, col_w, head, summ, src)
            cy += 6
        if ci == 2:
            # UTC timeline + date check fill the short third column
            cy += 2
            cy = region_header(d, x, cy, col_w, "THE DAY IN UTC", RED)
            for t, what in TIMELINE:
                d.text((x, cy), t, font=SANS_B(10.5), fill=RED)
                lines = fit_lines(d, what, SANS(10.5), col_w - 78, 1)
                yy = cy
                for ln in lines:
                    d.text((x + 80, yy), ln, font=SANS(10.5), fill=INK)
                    yy += 12
                cy = max(cy + 13, yy) + 1
            cy += 6
            box_lines = wrap(d, "Every story above happened or was first reported on Sunday 22 November 2026.",
                             SANS(10), col_w - 16)
            box_h = 22 + 13 * len(box_lines)
            d.rectangle([x, cy, x + col_w, cy + box_h], outline=RED, width=2)
            d.text((x + 8, cy + 6), "DATE CHECK", font=SANS_B(11), fill=RED)
            by = cy + 22
            for ln in box_lines:
                d.text((x + 8, by), ln, font=SANS(10), fill=INK)
                by += 13
            cy += box_h
        print(f"column {ci + 1} ends at y={cy}")

    # ---- footer
    fy = H - 34
    d.line([MARGIN, fy - 8, W - MARGIN, fy - 8], fill=INK, width=1)
    d.text((MARGIN, fy), "Sources: Reuters · AFP · AP · China Daily · info.gov.hk · EIN News · Africa Front Page",
           font=SANS(10), fill=GREY)
    d.text((W - MARGIN, fy), "No. 326", font=SANS(10), fill=GREY, anchor="ra")

    img.save("entry.png", optimize=True)
    print("wrote entry.png", img.size)


if __name__ == "__main__":
    main()
