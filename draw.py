#!/usr/bin/env python3
"""Draw the world news of Sunday 22 November 2026 as one 1024x1024 PNG.

Pure standard library: a tiny raster canvas, a hand-made 5x7 bitmap font,
simple geometric pictograms, and a minimal PNG encoder (zlib + CRC).
Deterministic: same input bytes -> same output bytes, no network, no time,
no randomness.
Usage: python3 draw.py <output-path>
"""
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (246, 241, 227)
INK = (25, 25, 25)
WHITE = (255, 255, 255)
RED = (179, 39, 30)
DARKRED = (140, 28, 22)
BLUE = (30, 78, 121)
TEAL = (15, 118, 110)
ORANGE = (217, 108, 0)
YELLOW = (240, 196, 25)
GREY = (107, 107, 107)
LIGHTGREY = (200, 200, 200)
DARKBLUE = (20, 40, 70)
GREEN = (46, 125, 50)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 cells, '#' = ink, '.' = empty.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.#.#", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}


def text_width(text, scale):
    return len(text) * 6 * scale - scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns a list of lines (upper-cased)."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def hline(self, x0, x1, y, color):
        if x1 < x0:
            x0, x1 = x1, x0
        for x in range(max(x0, 0), min(x1, self.w - 1) + 1):
            self.set(x, y, color)

    def vline(self, x, y0, y1, color):
        if y1 < y0:
            y0, y1 = y1, y0
        for y in range(max(y0, 0), min(y1, self.h - 1) + 1):
            self.set(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def thick_line(self, x0, y0, x1, y1, color, t=3):
        for ox in range(-(t // 2), t // 2 + 1):
            for oy in range(-(t // 2), t // 2 + 1):
                self.line(x0 + ox, y0 + oy, x1 + ox, y1 + oy, color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            self.hline(x, x + w - 1, yy, color)

    def rect_outline(self, x, y, w, h, color, t=2):
        for i in range(t):
            self.hline(x, x + w - 1, y + i, color)
            self.hline(x, x + w - 1, y + h - 1 - i, color)
            self.vline(x + i, y, y + h - 1, color)
            self.vline(x + w - 1 - i, y, y + h - 1, color)

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, color, t=5):
        self.fill_circle(cx, cy, r, color)
        self.fill_circle(cx, cy, r - t, PAPER)

    def fill_poly(self, pts, color):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(round(xs[i])), int(round(xs[i + 1])), y, color)

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx,
                                         y + row * scale + dy, color)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, cx, y, text, scale, color):
        self.draw_text(cx - text_width(text, scale) // 2, y, text, scale, color)

    def draw_wrapped(self, x, y, text, scale, color, max_w, line_h=None):
        lh = line_h if line_h is not None else 9 * scale
        yy = y
        for line in wrap_text(text, scale, max_w):
            self.draw_text(x, yy, line, scale, color)
            yy += lh
        return yy


# ---------------------------------------------------------------- pictograms
def icon_globe(c, x, y):
    # COP31: a globe with a red crack through it
    cx, cy, r = x + 66, y + 96, 62
    c.fill_circle(cx, cy, r, BLUE)
    c.fill_circle(cx, cy, r - 4, PAPER)
    c.hline(cx - r + 6, cx + r - 6, cy - 26, BLUE)
    c.hline(cx - r + 2, cx + r - 2, cy, BLUE)
    c.hline(cx - r + 6, cx + r - 6, cy + 26, BLUE)
    c.vline(cx, cy - r + 4, cy + r - 4, BLUE)
    c.thick_line(cx - 44, cy - 44, cx - 8, cy - 6, RED, 5)
    c.thick_line(cx - 8, cy - 6, cx + 18, cy + 22, RED, 5)
    c.thick_line(cx + 18, cy + 22, cx + 44, cy + 46, RED, 5)


def icon_missile(c, x, y):
    # Iran strike: a missile with flame
    cx = x + 66
    c.fill_poly([(cx, y + 8), (cx - 16, y + 48), (cx + 16, y + 48)], INK)
    c.rect(cx - 16, y + 48, 32, 78, INK)
    c.fill_poly([(cx - 16, y + 96), (cx - 34, y + 132), (cx - 16, y + 126)], INK)
    c.fill_poly([(cx + 16, y + 96), (cx + 34, y + 132), (cx + 16, y + 126)], INK)
    c.fill_poly([(cx, y + 168), (cx - 13, y + 126), (cx + 13, y + 126)], ORANGE)
    c.fill_poly([(cx, y + 156), (cx - 6, y + 126), (cx + 6, y + 126)], YELLOW)
    c.draw_text_centered(cx, y + 178, "BAHRAIN", 2, RED)


def icon_building(c, x, y):
    # Ukraine: a shelled apartment block, smoke above
    c.fill_circle(x + 34, y + 22, 14, GREY)
    c.fill_circle(x + 66, y + 12, 18, GREY)
    c.fill_circle(x + 98, y + 24, 13, GREY)
    bx, by = x + 16, y + 46
    c.rect(bx, by, 100, 128, LIGHTGREY)
    c.rect_outline(bx, by, 100, 128, INK, 3)
    for row in range(4):
        for col in range(4):
            c.rect(bx + 12 + col * 23, by + 14 + row * 30, 12, 14, INK)
    # jagged crack from the top corner down
    pts = [(bx + 78, by), (bx + 66, by + 26), (bx + 80, by + 52),
           (bx + 62, by + 80), (bx + 74, by + 104), (bx + 58, by + 128)]
    for a, b in zip(pts, pts[1:]):
        c.thick_line(a[0], a[1], b[0], b[1], INK, 3)
    c.thick_line(bx + 100, by + 40, bx + 78, by + 40, INK, 3)


def icon_handcuffs(c, x, y):
    # Mexico: handcuffs
    c.ring(x + 36, y + 96, 30, INK, 7)
    c.ring(x + 96, y + 96, 30, INK, 7)
    c.thick_line(x + 36, y + 66, x + 66, y + 66, INK, 5)
    c.thick_line(x + 66, y + 66, x + 96, y + 66, INK, 5)
    c.fill_circle(x + 66, y + 66, 7, INK)
    c.draw_text_centered(x + 66, y + 148, "CAPTURED", 2, INK)


def icon_chart(c, x, y):
    # Markets: a falling chart
    ox, oy = x + 14, y + 150
    c.thick_line(ox, y + 20, ox, oy, INK, 3)
    c.thick_line(ox, oy, x + 122, oy, INK, 3)
    pts = [(ox + 6, y + 34), (ox + 28, y + 52), (ox + 50, y + 48),
           (ox + 72, y + 84), (ox + 94, y + 108), (ox + 112, y + 136)]
    for a, b in zip(pts, pts[1:]):
        c.thick_line(a[0], a[1], b[0], b[1], RED, 5)
    # arrow head at the end
    ex, ey = pts[-1]
    c.fill_poly([(ex, ey + 8), (ex - 12, ey - 6), (ex + 2, ey - 8)], RED)
    c.draw_text_centered(x + 66, y + 164, "-3.7%  S&P", 2, RED)


def icon_fire(c, x, y):
    # Indonesia: factory fire
    c.fill_poly([(x + 66, y + 6), (x + 96, y + 52), (x + 104, y + 92),
                 (x + 82, y + 116), (x + 66, y + 96), (x + 50, y + 116),
                 (x + 28, y + 92), (x + 36, y + 52)], ORANGE)
    c.fill_poly([(x + 66, y + 46), (x + 84, y + 76), (x + 76, y + 104),
                 (x + 56, y + 104), (x + 48, y + 76)], YELLOW)
    c.rect(x + 18, y + 128, 96, 52, INK)
    c.rect(x + 92, y + 104, 14, 26, INK)
    c.fill_circle(x + 99, y + 92, 9, GREY)
    c.fill_circle(x + 108, y + 78, 11, GREY)


ICONS = [icon_globe, icon_missile, icon_building, icon_handcuffs, icon_chart, icon_fire]

STORIES = [
    ("CLIMATE", RED, "COP31 COLLAPSES",
     "Climate talks in Antalya end with no deal as the EU rejects a draft with no mention of fossil fuels."),
    ("GULF", DARKRED, "IRAN STRIKES BAHRAIN",
     "Iranian projectiles hit an industrial site in Sitra, injuring two. Gulf states condemn the attack."),
    ("UKRAINE", BLUE, "DRONE HITS FLATS NEAR KYIV",
     "A Russian drone collapses part of a five-storey block in Dymer. At least 14 people are missing."),
    ("MEXICO", TEAL, "CARTEL BOSS CAPTURED",
     "'El Chapo Isidro' seized in Sinaloa. 11 people killed in the raid, including four soldiers."),
    ("MARKETS", DARKBLUE, "STOCKS TUMBLE WORLDWIDE",
     "S&P 500 falls 3.7% and Nasdaq 5.3% as the AI sell-off spreads to Japan and Korea."),
    ("DISASTER", ORANGE, "FACTORY FIRE IN INDONESIA",
     "A candy factory blaze in Cikande kills three workers. 36 are still missing."),
]

FOOTER = ("ALSO TODAY: WORLD COURT RULES MYANMAR COMMITTED GENOCIDE AGAINST THE "
          "ROHINGYA - BEPICOLOMBO REACHES MERCURY AFTER 8 YEARS - "
          "VERSTAPPEN WINS LAS VEGAS GP - EU AND INDONESIA SIGN LANDMARK TRADE DEAL")


# ---------------------------------------------------------------- page
def build():
    c = Canvas(W, H, PAPER)

    # masthead
    c.draw_text_centered(W // 2, 20, "THE WORLD IN ONE DAY", 6, INK)
    c.draw_text_centered(W // 2, 76, "SUNDAY, 22 NOVEMBER 2026", 3, RED)
    c.rect(40, 116, W - 80, 4, RED)
    c.draw_text_centered(W // 2, 128, "SIX STORIES THAT DEFINED THE DAY", 2, INK)

    # story panels: 2 columns x 3 rows
    pw, ph, gap = 496, 252, 16
    for i, (tag, color, head, body) in enumerate(STORIES):
        px = 8 + (i % 2) * (pw + gap)
        py = 160 + (i // 2) * (ph + gap)
        c.rect(px, py, pw, ph, WHITE)
        c.rect_outline(px, py, pw, ph, INK, 3)
        # tag strip
        c.rect(px + 3, py + 3, pw - 6, 34, color)
        c.draw_text(px + 14, py + 11, tag, 2, WHITE)
        c.draw_text(px + pw - 14 - text_width("22 NOV 2026", 2),
                    py + 11, "22 NOV 2026", 2, WHITE)
        # pictogram
        ICONS[i](c, px + 12, py + 48)
        # headline + body
        tx = px + 158
        tw = pw - 158 - 14
        yy = py + 52
        for line in wrap_text(head, 3, tw):
            c.draw_text(tx, yy, line, 3, INK)
            yy += 27
        c.draw_wrapped(tx, yy + 10, body, 2, INK, tw, line_h=18)

    # footer band
    c.rect(0, 952, W, H - 952, INK)
    c.draw_wrapped(16, 962, FOOTER, 2, WHITE, W - 32, line_h=18)
    return c


# ---------------------------------------------------------------- PNG out
def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(c, path):
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(c.px[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    size = write_png(build(), out)
    print("wrote %s (%d bytes, %dx%d)" % (out, size, W, H))


if __name__ == "__main__":
    main()
