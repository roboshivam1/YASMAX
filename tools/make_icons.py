"""
File: tools/make_icons.py

Draws the YASMAX app icons (PNG) with plain Python, no image library, so
the build runs anywhere with nothing to install. Called by build_site.py.

The icon: a Windows-7-blue rounded square (the title bar colour of the
simulator window) holding a grey chip with pins on all four sides, and a
cyan "screen" on the chip, the colour of the instruction memory view.

    python3 tools/make_icons.py OUT_DIR    writes icon-192.png, icon-512.png,
                                           icon-maskable-512.png, apple-touch-icon.png
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

BLUE_TOP, BLUE_BOTTOM = (70, 130, 205), (23, 76, 150)
CHIP, CHIP_EDGE, PIN = (226, 230, 236), (120, 132, 150), (245, 208, 120)
SCREEN, SCREEN_LINE = (128, 255, 255), (40, 150, 170)


def png(width: int, height: int, rows: list[bytes]) -> bytes:
    """Encode RGBA rows as a PNG file."""
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    raw = b"".join(b"\0" + row for row in rows)
    head = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


def inside_round_rect(x: float, y: float, x0: float, y0: float, x1: float, y1: float, r: float) -> bool:
    cx = min(max(x, x0 + r), x1 - r)
    cy = min(max(y, y0 + r), y1 - r)
    return (x - cx) ** 2 + (y - cy) ** 2 <= r * r


def pixel(u: float, v: float, full_bleed: bool) -> tuple[int, int, int, int]:
    """Colour at (u, v) in 0..1 icon coordinates."""
    if not full_bleed and not inside_round_rect(u, v, 0.02, 0.02, 0.98, 0.98, 0.2):
        return (0, 0, 0, 0)
    # Chip body with pins. Full-bleed (maskable) icons get cropped to a
    # circle by some systems, so the chip stays inside the central safe zone.
    s = 0.46 if full_bleed else 0.5
    c0, c1 = 0.5 - s / 2, 0.5 + s / 2
    if inside_round_rect(u, v, c0, c0, c1, c1, 0.04):
        edge = not inside_round_rect(u, v, c0 + 0.015, c0 + 0.015, c1 - 0.015, c1 - 0.015, 0.03)
        if edge:
            return (*CHIP_EDGE, 255)
        m0, m1 = c0 + s * 0.2, c1 - s * 0.2
        if m0 <= u <= m1 and m0 <= v <= m1:
            line = int((v - m0) / (m1 - m0) * 5) != int((v - m0 + 0.012) / (m1 - m0) * 5)
            return (*(SCREEN_LINE if line else SCREEN), 255)
        return (*CHIP, 255)
    for i in range(5):
        p = c0 + s * (0.12 + i * 0.19)
        if abs(u - p) < s * 0.045 and (c0 - 0.07 < v < c0 or c1 < v < c1 + 0.07):
            return (*PIN, 255)
        if abs(v - p) < s * 0.045 and (c0 - 0.07 < u < c0 or c1 < u < c1 + 0.07):
            return (*PIN, 255)
    t = v
    return (*(round(a + (b - a) * t) for a, b in zip(BLUE_TOP, BLUE_BOTTOM)), 255)


def draw(size: int, full_bleed: bool = False) -> bytes:
    """Render with 3x3 supersampling so the curves are smooth."""
    rows = []
    for y in range(size):
        row = bytearray()
        for x in range(size):
            acc = [0, 0, 0, 0]
            for sy in (0.17, 0.5, 0.83):
                for sx in (0.17, 0.5, 0.83):
                    r, g, b, a = pixel((x + sx) / size, (y + sy) / size, full_bleed)
                    acc = [acc[0] + r * a, acc[1] + g * a, acc[2] + b * a, acc[3] + a]
            alpha = acc[3] / 9
            row += bytes([round(acc[i] / acc[3]) if acc[3] else 0 for i in range(3)] + [round(alpha)])
        rows.append(bytes(row))
    return png(size, size, rows)


def make_icons(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    (out / "icon-192.png").write_bytes(draw(192))
    (out / "icon-512.png").write_bytes(draw(512))
    (out / "icon-maskable-512.png").write_bytes(draw(512, full_bleed=True))
    (out / "apple-touch-icon.png").write_bytes(draw(180, full_bleed=True))


if __name__ == "__main__":
    make_icons(Path(sys.argv[1] if len(sys.argv) > 1 else "web/icons"))
    print("Icons written.")
