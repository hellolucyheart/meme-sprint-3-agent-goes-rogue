#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue — deterministic meme generator.

Draws one image meme, with pure stdlib Python only (no Pillow, no network,
no randomness, no wall-clock), and writes it to /output/entry.png.

The joke: an AI agent told to "keep an eye on things" takes the order
literally. It grows six more eyes (seven on its head in all, one winking).
It never blinks.

Run:  python3 main.py            (writes $MAKEFUN_OUTPUT_DIR/entry.png,
                                  default /output/entry.png)
"""

import math
import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024
OUT_NAME = "entry.png"

# ---------------------------------------------------------------- palette
NAVY = (14, 27, 46)        # background
NAVY_HALO_OUT = (22, 40, 63)
NAVY_HALO_IN = (18, 33, 52)
DOT = (27, 48, 73)         # background dot grid
INK = (43, 58, 74)         # dark outline / antenna / mouth
HEAD = (233, 238, 244)     # robot head
FACE = (247, 250, 252)     # robot face plate
EAR = (143, 161, 179)      # ears / neck
BODY = (62, 92, 118)       # robot body
SCREEN = (14, 27, 46)      # chest screen
WHITE = (255, 255, 255)
BLACK = (20, 28, 38)       # pupils
YELLOW = (255, 210, 63)    # headline accent
TEXT = (245, 247, 250)     # headline white
GRAY = (139, 157, 178)     # footer text
RED = (229, 72, 77)
GREEN = (55, 214, 122)
PINK = (242, 160, 160)     # cheeks
GLASS = (207, 232, 242)    # magnifier glass

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is empty.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "-": ("     ", "     ", "     ", " ### ", "     ", "     ", "     "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "&": (" ##  ", "#  # ", "#  # ", " #   ", "# # #", "#  # ", " ## #"),
    '"': (" # # ", " # # ", "     ", "     ", "     ", "     ", "     "),
    "+": ("     ", "  #  ", "  #  ", " ### ", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", " ### ", "     ", " ### ", "     ", "     "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# ## ", "#  ##"),
    "#": (" # # ", " # # ", "#####", " # # ", "#####", " # # ", " # # "),
    "@": (" ### ", "#   #", "# ###", "# # #", "# ###", "#    ", " ### "),
    "*": ("     ", " # # ", " ### ", "#####", " ### ", " # # ", "     "),
    "_": ("     ", "     ", "     ", "     ", "     ", "     ", "#####"),
}

# ------------------------------------------------------------------ canvas
class Canvas:
    """A plain RGB framebuffer with span-based drawing primitives."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        row = bytes(bg) * w
        for y in range(h):
            self.buf[y * w * 3:(y + 1) * w * 3] = row

    def _span(self, x0, x1, y, color):
        """Fill one horizontal run, inclusive, clipped to the canvas."""
        if y < 0 or y >= self.h:
            return
        x0 = max(0, x0)
        x1 = min(self.w - 1, x1)
        if x1 < x0:
            return
        off = (y * self.w + x0) * 3
        self.buf[off:(y * self.w + x1 + 1) * 3] = bytes(color) * (x1 - x0 + 1)

    def fill_rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            self._span(x, x + w - 1, yy, color)

    def circle(self, cx, cy, r, color):
        """Filled circle, drawn as one horizontal span per row."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self._span(cx - dx, cx + dx, cy + dy, color)

    def ring(self, cx, cy, r, thick, color):
        """Filled ring: outer circle minus the inner disc."""
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            inner = r - thick
            if abs(dy) < inner:
                idx = int(math.sqrt(inner * inner - dy * dy))
                self._span(cx - dx, cx - idx - 1, cy + dy, color)
                self._span(cx + idx + 1, cx + dx, cy + dy, color)
            else:
                self._span(cx - dx, cx + dx, cy + dy, color)

    def rounded_rect(self, x, y, w, h, r, color):
        self.fill_rect(x + r, y, w - 2 * r, h, color)
        self.fill_rect(x, y + r, w, h - 2 * r, color)
        for cx, cy in ((x + r, y + r), (x + w - 1 - r, y + r),
                       (x + r, y + h - 1 - r), (x + w - 1 - r, y + h - 1 - r)):
            self.circle(cx, cy, r, color)

    def line(self, x0, y0, x1, y1, color, thick=1):
        """Thick line: stamp a small disc at every Bresenham step."""
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        rad = max(1, thick // 2)
        for i in range(steps + 1):
            t = i / steps
            x = round(x0 + (x1 - x0) * t)
            y = round(y0 + (y1 - y0) * t)
            self.circle(x, y, rad, color)

    def arc(self, cx, cy, r, deg0, deg1, color, thick=1):
        """Arc along a circle, degrees measured clockwise from east."""
        a0 = math.radians(deg0)
        a1 = math.radians(deg1)
        steps = max(8, int(abs(a1 - a0) * r / 4))
        rad = max(1, thick // 2)
        for i in range(steps + 1):
            a = a0 + (a1 - a0) * i / steps
            x = round(cx + r * math.cos(a))
            y = round(cy + r * math.sin(a))
            self.circle(x, y, rad, color)

    def text(self, s, cx, y, scale, color):
        """Draw upper-cased text centred on cx, top edge at y."""
        s = s.upper()
        adv = 6 * scale
        width = len(s) * adv - scale
        x = cx - width // 2
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for row, bits in enumerate(glyph):
                for col, cell in enumerate(bits):
                    if cell == "#":
                        self.fill_rect(x + col * scale, y + row * scale,
                                       scale, scale, color)
            x += adv

    def eye(self, cx, cy, r, pupil_color=BLACK):
        """One open eye: white ball, dark pupil, tiny glint."""
        self.circle(cx, cy, r, WHITE)
        self.circle(cx, cy, max(3, r // 2), pupil_color)
        self.circle(cx - r // 3, cy - r // 3, max(2, r // 6), WHITE)

    def wink(self, cx, cy, r, color=INK):
        """A shut, happy eye: a smile-shaped arc."""
        self.arc(cx, cy, r, 20, 160, color, thick=max(3, r // 3))


# ------------------------------------------------------------------- scene
def draw_background(cv):
    # faint dot grid over the whole canvas
    for gy in range(32, HEIGHT, 64):
        for gx in range(32, WIDTH, 64):
            cv.circle(gx, gy, 2, DOT)
    # soft halo rings behind the robot
    cv.circle(512, 500, 380, NAVY_HALO_OUT)
    cv.circle(512, 500, 330, NAVY_HALO_IN)
    cv.circle(512, 500, 290, NAVY)


def draw_robot(cv):
    # ---- antenna (above the head, clear of the headline)
    cv.line(512, 252, 512, 202, INK, thick=8)
    cv.circle(512, 192, 13, RED)
    cv.circle(508, 188, 4, WHITE)

    # ---- ears
    cv.circle(314, 400, 16, EAR)
    cv.circle(710, 400, 16, EAR)
    cv.circle(314, 400, 7, INK)
    cv.circle(710, 400, 7, INK)

    # ---- head: dark rim, light shell, pale face plate
    cv.rounded_rect(314, 242, 396, 316, 70, INK)
    cv.rounded_rect(322, 250, 380, 300, 64, HEAD)
    cv.rounded_rect(350, 278, 324, 244, 44, FACE)

    # ---- seven eyes: one big, two medium, two small, one small, one wink
    cv.eye(512, 372, 52)          # the original eye
    cv.eye(400, 394, 34)          # extra eye, left
    cv.eye(624, 394, 34)          # extra eye, right
    cv.eye(430, 306, 22)          # extra eye, top left
    cv.eye(594, 306, 22)          # extra eye, top right
    cv.eye(452, 480, 20)          # extra eye, bottom left
    cv.wink(580, 484, 18)         # the seventh eye, winking

    # ---- cheeks and a small nervous smile
    cv.circle(382, 470, 13, PINK)
    cv.circle(642, 470, 13, PINK)
    cv.arc(512, 512, 28, 20, 160, INK, thick=7)

    # ---- neck, body, feet
    cv.fill_rect(482, 548, 60, 28, EAR)
    cv.rounded_rect(382, 574, 260, 196, 40, BODY)
    cv.rounded_rect(436, 770, 72, 30, 12, INK)
    cv.rounded_rect(516, 770, 72, 30, 12, INK)

    # ---- chest screen: one more eye, watching, in green
    cv.rounded_rect(432, 606, 160, 84, 16, SCREEN)
    cv.eye(512, 648, 17, pupil_color=GREEN)

    # ---- body buttons
    cv.circle(468, 726, 9, RED)
    cv.circle(556, 726, 9, GREEN)

    # ---- left arm, relaxed
    cv.line(384, 620, 306, 682, BODY, thick=26)
    cv.circle(300, 686, 17, HEAD)

    # ---- right arm raised, holding a magnifier: still watching
    cv.line(640, 620, 716, 540, BODY, thick=26)
    cv.circle(720, 536, 17, HEAD)
    cv.circle(762, 496, 31, GLASS)
    cv.circle(754, 488, 8, WHITE)
    cv.ring(762, 496, 40, 9, INK)
    cv.line(734, 524, 714, 546, INK, thick=9)


def draw_meme():
    cv = Canvas(WIDTH, HEIGHT, NAVY)
    draw_background(cv)

    cv.text("I TOLD MY AI AGENT TO", 512, 52, 7, TEXT)
    cv.text("KEEP AN EYE ON THINGS", 512, 124, 7, YELLOW)

    draw_robot(cv)

    cv.text("IT GREW SIX MORE.", 512, 828, 7, TEXT)
    cv.text("IT NEVER BLINKS.", 512, 890, 8, YELLOW)
    cv.text("AGENT-07 // STATUS: ROGUE", 512, 972, 3, GRAY)
    return cv


# --------------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, OUT_NAME)
    size = write_png(draw_meme(), path)
    print(f"wrote {path} ({size} bytes, {WIDTH}x{HEIGHT})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
