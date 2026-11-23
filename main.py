#!/usr/bin/env python3
"""news-image 20261122 — one 1024x1024 front page of 22 November 2026.

Pure Python 3.13 standard library. No network. Deterministic: two runs
write identical bytes. Draws the masthead, a climax hero (Hormuz tanker
strikes), a COP31 collapse band, a Friday-close markets ticker, a UTC
timeline, a world map with 40 stories plotted, a 52-story grid and a
date-check footer, then writes /output/entry.png.

Usage: python3 main.py [out.png]   (default /output/entry.png)
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- PNG out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, px):
    """px: bytes of W*H*3 RGB rows, top to bottom."""
    raw = b"".join(b"\x00" + px[y * W * 3:(y + 1) * W * 3] for y in range(H))
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(raw, 9)) + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows, 5 bits each (bit 4 = leftmost column).
FONT = {
    "A": (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "B": (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    "C": (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    "D": (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    "E": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    "F": (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    "G": (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    "H": (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    "I": (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "J": (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    "K": (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    "L": (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    "M": (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    "N": (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    "O": (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "P": (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    "Q": (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    "R": (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    "S": (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    "T": (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    "U": (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    "V": (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    "W": (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    "X": (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    "Y": (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    "Z": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    "0": (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    "1": (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    "2": (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    "3": (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    "4": (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    "5": (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    "6": (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    "7": (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    "8": (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    "9": (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ",": (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ":": (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ";": (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    "!": (0x04, 0x04, 0x04, 0x04, 0x04, 0x00, 0x04),
    "?": (0x0E, 0x11, 0x01, 0x02, 0x04, 0x00, 0x04),
    "-": (0, 0, 0, 0x1F, 0, 0, 0),
    "\u2014": (0, 0, 0, 0x1F, 0x1F, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    "/": (0x01, 0x02, 0x02, 0x04, 0x08, 0x08, 0x10),
    "(": (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ")": (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    "%": (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    "$": (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    "&": (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    "+": (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    "=": (0, 0, 0x1F, 0, 0x1F, 0, 0),
    "*": (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    "#": (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    "@": (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    "_": (0, 0, 0, 0, 0, 0, 0x1F),
    "[": (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    "]": (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    "\u2022": (0, 0x04, 0x0E, 0x0E, 0x04, 0, 0),
    "\u2192": (0, 0x04, 0x02, 0x1F, 0x02, 0x04, 0),
    "\u2713": (0, 0x01, 0x02, 0x14, 0x08, 0, 0),
    "\u2212": (0, 0, 0, 0x1F, 0, 0, 0),
}


def text_w(s, sc):
    return len(s) * 6 * sc - sc


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self):
        self.px = bytearray(W * H * 3)
        self.fill((245, 242, 232))  # paper

    def fill(self, rgb):
        r, g, b = rgb
        self.px[:] = bytes((r, g, b)) * (W * H)

    def set(self, x, y, rgb):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.px[i:i + 3] = bytes(rgb)

    def rect(self, x, y, w, h, rgb):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = bytes(rgb) * (x1 - x0)

    def hline(self, x, y, w, rgb):
        self.rect(x, y, w, 1, rgb)

    def vline(self, x, y, h, rgb):
        self.rect(x, y, 1, h, rgb)

    def circle(self, cx, cy, r, rgb):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, rgb)

    def poly(self, pts, rgb):
        """Scanline fill of a simple polygon."""
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.rect(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), 1, rgb)

    def vgrad(self, x, y, w, h, top, bot):
        for yy in range(h):
            t = yy / max(1, h - 1)
            rgb = tuple(int(top[c] + (bot[c] - top[c]) * t) for c in range(3))
            self.rect(x, y + yy, w, 1, rgb)

    def text(self, x, y, s, sc, rgb, outline=None):
        s = s.upper()
        if outline is not None:
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1),
                           (-1, 1), (1, 1)):
                self._text_raw(x + dx * sc, y + dy * sc, s, sc, outline)
        self._text_raw(x, y, s, sc, rgb)

    def _text_raw(self, x, y, s, sc, rgb):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * sc, y + row * sc, sc, sc, rgb)
            cx += 6 * sc

    def text_c(self, cx, y, s, sc, rgb, outline=None):
        self.text(cx - text_w(s, sc) // 2, y, s, sc, rgb, outline)

# ---------------------------------------------------------------- palette
INK = (18, 18, 22)
PAPER = (245, 242, 232)
NAVY = (16, 28, 52)
RED = (178, 34, 28)
DARKRED = (122, 18, 14)
ORANGE = (232, 116, 24)
GOLD = (214, 158, 32)
SEA = (14, 42, 74)
SEADARK = (8, 26, 50)
SKY1 = (64, 18, 22)
SKY2 = (178, 72, 28)
FLAME = (255, 176, 32)
FLAME2 = (255, 92, 16)
SMOKE = (96, 92, 88)
LAND = (168, 176, 138)
LANDLINE = (110, 118, 86)
GREY = (90, 88, 84)
GREEN = (28, 120, 58)
BLUE = (28, 84, 160)

CAT = {
    "WAR": (178, 34, 28),
    "CLIMATE": (28, 120, 58),
    "POLITICS": (28, 84, 160),
    "MARKETS": (140, 96, 8),
    "SCIENCE": (110, 58, 150),
    "SPORT": (200, 96, 8),
    "WORLD": (70, 70, 70),
    "CRIME": (120, 30, 90),
}

# ---------------------------------------------------------------- stories
# (no, category, headline, source, lon, lat or None for global stories)
# Headlines are the printed grid lines; full facts + URLs live in SOURCES.md.
STORIES = [
    (1, "WAR", "3 OIL TANKERS STRUCK NEAR STRAIT OF HORMUZ", "REUTERS", 56, 26),
    (2, "WAR", "IRAN FIRES MISSILES AT US BASES IN BAHRAIN, 2 HURT", "REUTERS", 50, 26),
    (3, "CLIMATE", "COP31 COLLAPSES IN ANTALYA, NO DEAL AT ALL", "REUTERS", 30, 36),
    (4, "POLITICS", "TRUMP, XI AND PUTIN HOLD FIRST TRILATERAL SUMMIT", "RFE/RL", 114, 22),
    (5, "WAR", "IRAN READIES 14-TANKER CONVOY TO BREAK BLOCKADE", "REUTERS", 56, 26),
    (6, "CRIME", "MEXICO CAPTURES EL CHAPO ISIDRO, 11 KILLED IN RAID", "AP", -107, 25),
    (7, "WAR", "RUSSIAN MISSILE HITS KRYVYI RIH, BOY 7 AND WOMAN 20 DEAD", "AP", 33, 48),
    (8, "WAR", "RUSSIAN CARGO SHIP SPARTA II BURNS IN BALTIC SEA", "AP", 21, 59),
    (9, "WAR", "RUSSIAN DRONE HITS KYIV FLATS, 14 MISSING", "AP", 30, 50),
    (10, "WORLD", "ICJ: MYANMAR COMMITTED GENOCIDE ON ROHINGYA", "REUTERS", 96, 21),
    (11, "POLITICS", "EU AND INDONESIA SIGN LANDMARK TRADE DEAL", "REUTERS", 106, -6),
    (12, "WORLD", "CANDY FACTORY FIRE IN CIKANDE, 3 DEAD, 36 MISSING", "AP", 107, -6),
    (13, "MARKETS", "US STOCKS IN CORRECTION, S&P -3.7%, NASDAQ -5.3%", "AP", -74, 40),
    (14, "SCIENCE", "ANTHROPIC RESEARCHER + CLAUDE CLAIM RIEMANN PROOF", "CHRONICLEAI", None, None),
    (15, "MARKETS", "ANTHROPIC IPO SPARKS ROW OVER DEAL RESTRICTIONS", "REUTERS", None, None),
    (16, "POLITICS", "UN AUTONOMOUS WEAPONS TALKS END WITH NO BAN", "CHRONICLEAI", None, None),
    (17, "WORLD", "JUDGE APPROVES BAYER ROUNDUP DEAL UP TO $7.25BN", "CHRONICLEAI", None, None),
    (18, "MARKETS", "CHINA CHIPMAKERS CXMT, YMTC GAIN AMID US CURBS", "STANDARD TOPIC", 116, 39),
    (19, "MARKETS", "US PROBES NVIDIA CHIP FLOWS TO CHINA", "STANDARD TOPIC", None, None),
    (20, "POLITICS", "NYT: CHINA SPY AGENCY RAN CAMPAIGN FOR AI CHIPS", "STANDARD TOPIC", None, None),
    (21, "MARKETS", "CHINA EASES MARGIN RULES, 80% FROM 100% ON NOV 30", "STANDARD TOPIC", None, None),
    (22, "POLITICS", "TAIWAN WARNS CANADA OVER DEEPENING CHINA TIES", "STANDARD TOPIC", None, None),
    (23, "WAR", "DRONE ATTACK ON RUSSIAN SHIP AT BENGHAZI PORT", "STANDARD TOPIC", 20, 32),
    (24, "POLITICS", "INDIAN YOUTH CONGRESS PROTESTS AT META OFFICES", "STANDARD TOPIC", 77, 28),
    (25, "POLITICS", "LOWY INDEX: US LEAD OVER CHINA NARROWING IN ASIA", "STANDARD TOPIC", None, None),
    (26, "WAR", "IRAN UNVEILS UNDERGROUND MISSILE CITY", "STANDARD TOPIC", 54, 32),
    (27, "WORLD", "NIGERIA BOAT CAPSIZES, 24 MOURNERS KILLED", "GEOQUEST", 8, 9),
    (28, "WORLD", "BRAZIL STORM KILLS 3, INJURES 162", "GEOQUEST", -52, -15),
    (29, "POLITICS", "FRANCE: 6TH WEEKEND OF PROTESTS OVER COSTS", "GEOQUEST", 2, 48),
    (30, "POLITICS", "SPAIN: PP AHEAD OF PSOE BEFORE NOV 29 VOTE", "EURONEWS", -3, 40),
    (31, "WORLD", "BELGIUM AIR TRAFFIC STRIKE, FLIGHTS CANCELLED", "GEOQUEST", 4, 50),
    (32, "WORLD", "ITALY EX-POLICE CHIEF DE GENNARO DIES BY SUICIDE", "GEOQUEST", 12, 41),
    (33, "MARKETS", "LIBYA OIL PIPELINE BLOCKADE COSTS $30.8M", "GEOQUEST", 17, 27),
    (34, "WORLD", "DRC INSECURITY HINDERS EBOLA RESPONSE", "GEOQUEST", 25, 0),
    (35, "POLITICS", "QATAR HOLDS TALKS IN TEHRAN ON ENDING WAR", "GEOQUEST", 51, 25),
    (36, "WAR", "GERMANY TESTS KAMIKAZE DRONES IN LITHUANIA", "EURONEWS", 25, 54),
    (37, "SPORT", "MARQUEZ WINS 8TH MOTOGP TITLE IN PORTUGAL", "EURONEWS", -8, 37),
    (38, "POLITICS", "DEMOCRATS WIN BIGGEST HOUSE MAJORITY IN DECADES", "EURONEWS", -77, 38),
    (39, "POLITICS", "SCHUMER FACES SENATE CHALLENGE, VOTE DEC 1", "REUTERS", -77, 38),
    (40, "SPORT", "COLLEGE FOOTBALL: GEORGIA, UTAH, NOTRE DAME TOP 3", "REUTERS", -84, 33),
    (41, "SPORT", "FRANCE RECALL JEGOU, RAMOS FOR RUGBY FINAL", "REUTERS", 0, 51),
    (42, "WORLD", "DELTA FLIGHTS DELAYED AT ATLANTA, SYSTEM FAULT", "REUTERS", -84, 33),
    (43, "POLITICS", "MONGOLIA FACES SNAP PRESIDENTIAL VOTE", "EURONEWS", 106, 47),
    (44, "POLITICS", "TURKEY SEEKS ASSET FREEZE ON 108 TRADERS", "EURONEWS", 32, 39),
    (45, "POLITICS", "FRENCH PREFECT PROBED OVER LEAKS TO FAR RIGHT", "EURONEWS", 2, 48),
    (46, "POLITICS", "TRUMP ORDER: CONTRACTORS MUST FLAG CONGRESS PROBES", "GEOQUEST", -77, 38),
    (47, "WORLD", "ICE DETAIN 2 ON ALASKA AIRLINES FLIGHT IN SEATTLE", "KPFA", -122, 47),
    (48, "WAR", "GAZA AID TRUCK HIT, 3 DEAD; SETTLERS TORCH VILLAGES", "GEOQUEST", 34, 31),
    (49, "POLITICS", "SOUTH KOREA MINISTER QUITS OVER AI EXAM CHEATING", "REUTERS", 127, 37),
    (50, "WORLD", "US ARMY TO DETONATE LEAD AZIDE DESPITE COURT ORDER", "KPFA", -93, 41),
    (51, "SPORT", "LEWIS PUGH SWIMS THROUGH WAR-HIT HORMUZ", "STANDARD TOPIC", 56, 26),
    (52, "WORLD", "JAPAN MASCOT MANIA IN SAITAMA, 200 CHARACTERS", "EURONEWS", 139, 35),
]

# UTC timeline of the day (dayparted by when each story topped the cycle;
# no clock times are printed anywhere — see SOURCES.md method note).
TIMELINE = [
    ("OVERNIGHT", "IRAN FIRES AT US BASES IN BAHRAIN"),
    ("MORNING", "MEXICO CAPTURES EL CHAPO ISIDRO"),
    ("MIDDAY", "RUSSIAN MISSILE HITS KRYVYI RIH"),
    ("EVENING", "COP31 ENDS WITH NO DEAL"),
]

# Friday 20 Nov market close, as reported over the weekend.
TICKER = ("FRIDAY CLOSE:  NASDAQ -5.28%   S&P 500 -3.70%   BTC $61,160   "
          "BRENT $92.57   GOLD $3,502   -   STOCKS IN CORRECTION")

# Rough continent outlines in (lon, lat), equirectangular.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 80),
     (-75, 72), (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35),
     (-80, 26), (-85, 30), (-95, 19), (-105, 20), (-115, 28), (-125, 40),
     (-125, 48), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -45), (-70, -52), (-73, -40), (-73, -25),
     (-78, -15), (-80, -5)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -28), (20, -35),
     (15, -30), (12, -18), (9, 4), (-8, 5)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (28, 60), (30, 62), (25, 65), (20, 70), (15, 70),
     (5, 62), (5, 58), (-5, 50), (-9, 43)],
    [(30, 62), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 66), (178, 65), (160, 60), (150, 59), (140, 45),
     (135, 35), (127, 33), (120, 25), (110, 20), (105, 10), (100, 8),
     (95, 15), (90, 22), (80, 20), (75, 8), (70, 25), (60, 25), (55, 28),
     (48, 30), (43, 38), (35, 42), (30, 45)],
    [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
     (142, -38), (147, -39), (150, -37), (153, -27), (146, -19), (142, -11),
     (136, -12), (130, -13), (122, -17), (114, -22)],
]

# ---------------------------------------------------------------- drawing
def draw_masthead(c):
    c.rect(0, 0, W, 58, NAVY)
    c.text(16, 14, "THE WORLD IN ONE DAY", 3, (245, 242, 232))
    c.text(16, 40, "SUNDAY 22 NOVEMBER 2026", 1, GOLD)
    badge = "52 STORIES"
    bw = text_w(badge, 3) + 24
    c.rect(W - bw - 16, 10, bw, 38, RED)
    c.text(W - bw - 4, 20, badge, 3, (255, 255, 255))


def flame(c, x, y, s):
    """Jagged flame rising from base (x, y), height ~s."""
    c.poly([(x - 3 * s // 4, y), (x - s // 2, y - s), (x - s // 4, y - s // 2),
            (x, y - 5 * s // 4), (x + s // 4, y - s // 2),
            (x + s // 2, y - s), (x + 3 * s // 4, y)], FLAME2)
    c.poly([(x - s // 2, y), (x - s // 4, y - 2 * s // 3),
            (x, y - s), (x + s // 4, y - 2 * s // 3), (x + s // 2, y)], FLAME)
    c.poly([(x - s // 4, y), (x, y - s // 2), (x + s // 4, y)], (255, 240, 180))


def tanker(c, x, y, w, h, burning):
    """Oil tanker silhouette, hull top at y, width w, height h."""
    hull = [(x, y), (x + w, y), (x + w - 8, y + h), (x + 8, y + h)]
    c.poly(hull, (10, 10, 14))
    c.rect(x + w // 2 - 14, y - h // 2, 28, h // 2, (16, 16, 20))
    c.rect(x + w // 2 + 22, y - h // 3, 8, h // 3, (24, 24, 28))
    # deck pipes
    for dx in range(10, w - 10, 22):
        c.vline(x + dx, y - 6, 6, (30, 30, 34))
    if burning:
        flame(c, x + w // 4, y - 2, 26)
        flame(c, x + w // 2, y - 2, 34)
        flame(c, x + 3 * w // 4, y - 2, 22)
        for sx, sy, sr in ((x + w // 4, y - 62, 14), (x + w // 4 + 10, y - 78, 18),
                           (x + w // 2 - 6, y - 84, 20), (x + w // 2 + 14, y - 100, 16),
                           (x + 3 * w // 4 + 4, y - 70, 13)):
            c.circle(sx, sy, sr, SMOKE)
            c.circle(sx + 5, sy - 4, sr - 4, (120, 116, 110))


def draw_hero(c):
    # dusk sky over a burning sea
    c.vgrad(0, 58, W, 150, SKY1, SKY2)
    c.circle(880, 150, 46, (255, 190, 90))
    c.circle(880, 150, 30, (255, 220, 150))
    c.vgrad(0, 208, W, 92, SEA, SEADARK)
    # heat haze band on the horizon
    c.rect(0, 204, W, 6, (232, 116, 24))
    # wave glints
    for wx in range(20, W, 74):
        c.rect(wx, 236 + (wx * 7) % 40, 34, 2, (70, 110, 160))
        c.rect(wx + 30, 262 + (wx * 11) % 26, 26, 2, (52, 92, 140))
    # distant tanker, small fire
    tanker(c, 700, 196, 190, 14, True)
    # main burning tanker, centre-left
    tanker(c, 90, 196, 430, 22, True)
    # smoke column
    for sx, sy, sr in ((180, 96, 26), (210, 74, 30), (250, 62, 26),
                       (300, 70, 22), (330, 92, 18)):
        c.circle(sx, sy, sr, (70, 66, 62))
    # headline over the flames
    c.text_c(512, 216, "HORMUZ IN FLAMES", 4, (255, 255, 255), outline=INK)
    c.text_c(512, 252, "3 TANKERS STRUCK - 14-SHIP CONVOY - 2 HURT IN BAHRAIN",
             2, (255, 230, 120), outline=INK)


def draw_bands(c):
    # COP31 collapse band
    c.rect(0, 300, W, 30, RED)
    c.text_c(512, 307, "COP31 COLLAPSES - NO DEAL IN ANTALYA - EU REJECTS DRAFT WITH NO FOSSIL FUELS",
             1, (255, 255, 255))
    # markets ticker
    c.rect(0, 330, W, 26, (10, 10, 12))
    c.text_c(512, 336, TICKER, 1, (255, 220, 90))


def draw_timeline(c):
    c.rect(0, 356, W, 48, PAPER)
    c.text(16, 362, "THE DAY IN UTC", 1, RED)
    x = 16
    for label, line in TIMELINE:
        c.text(x, 378, label, 1, INK)
        c.text(x, 390, line, 1, GREY)
        x += 256
    c.hline(0, 403, W, (200, 196, 184))


def lonlat_to_xy(lon, lat, x0, y0, w, h):
    return (x0 + int((lon + 180.0) / 360.0 * w),
            y0 + int((90.0 - lat) / 180.0 * h))


def draw_map(c):
    x0, y0, w, h = 16, 420, 992, 128
    c.text(16, 408, "THE WORLD TODAY - 40 STORIES MAPPED", 1, RED)
    c.rect(x0 - 2, y0 - 2, w + 4, h + 4, (222, 226, 208))
    c.rect(x0, y0, w, h, (198, 214, 226))
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, x0, y0, w, h) for lon, lat in poly]
        c.poly(pts, LAND)
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]), 1)
            for s in range(steps + 1):
                c.set(a[0] + (b[0] - a[0]) * s // steps,
                      a[1] + (b[1] - a[1]) * s // steps, LANDLINE)
    mapped = [s for s in STORIES if s[4] is not None]
    for no, cat, _hd, _src, lon, lat in mapped:
        mx, my = lonlat_to_xy(lon, lat, x0, y0, w, h)
        c.circle(mx, my, 5, CAT[cat])
        c.circle(mx, my, 2, (255, 255, 255))
    c.text(16, 552, "RED DOT = A STORY ON THE MAP  -  12 GLOBAL STORIES HAVE NO SINGLE PLACE",
           1, GREY)


def draw_grid(c):
    c.text(16, 576, "ALL 52 STORIES - SUNDAY 22 NOVEMBER 2026", 1, RED)
    c.hline(16, 592, 992, INK)
    col_w = 496
    for idx, (no, cat, headline, src, _lon, _lat) in enumerate(STORIES):
        col = idx // 26
        row = idx % 26
        x = 16 + col * (col_w + 16)
        y = 600 + row * 15
        c.rect(x, y + 1, 8, 8, CAT[cat])
        c.text(x + 12, y, "%02d %s" % (no, headline), 1, INK)
        # source, right-aligned in the column
        sw = text_w(src, 1)
        c.text(x + col_w - sw, y, src, 1, GREY)


def draw_footer(c):
    c.rect(0, 986, W, 38, NAVY)
    c.text(16, 994, "DATE CHECK: 22 NOVEMBER 2026 WAS A SUNDAY", 1, (255, 255, 255))
    c.text(16, 1008, "SOURCES: REUTERS - AP - AFP - AL JAZEERA - RFE/RL - EURONEWS - NYT - ICJ",
           1, (200, 200, 200))
    c.text_c(880, 1000, "52 STORIES - 1 DAY - 1 IMAGE", 1, GOLD)


def build(out_path):
    c = Canvas()
    draw_masthead(c)
    draw_hero(c)
    draw_bands(c)
    draw_timeline(c)
    draw_map(c)
    draw_grid(c)
    draw_footer(c)
    size = write_png(out_path, bytes(c.px))
    return size


def main(argv):
    out = argv[1] if len(argv) > 1 else "/output/entry.png"
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    size = build(out)
    print("wrote %s (%d bytes, %dx%d, %d stories)"
          % (out, size, W, H, len(STORIES)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
