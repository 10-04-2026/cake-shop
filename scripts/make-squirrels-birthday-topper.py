#!/usr/bin/env python3
"""Build a print-ready 11 cm circular cake topper on A4 from the source photo."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

SOURCE = Path(__file__).resolve().parents[1] / "cake-prints" / "squirrels-birthday-source.jpg"
OUT_DIR = Path(__file__).resolve().parents[1] / "cake-prints"

DPI = 300
A4_W_MM, A4_H_MM = 210.0, 297.0
DIAMETER_MM = 110.0  # 11 cm


def mm_to_px(mm: float, dpi: int = DPI) -> int:
    return int(round(mm / 25.4 * dpi))


def fit_circle(edge_pts: np.ndarray) -> tuple[float, float, float]:
    x = edge_pts[:, 0]
    y = edge_pts[:, 1]
    a = np.column_stack([2 * x, 2 * y, np.ones_like(x)])
    b = x * x + y * y
    sol, *_ = np.linalg.lstsq(a, b, rcond=None)
    cx, cy, c = sol
    r = float(np.sqrt(c + cx * cx + cy * cy))
    return float(cx), float(cy), r


def collect_edge_points(content: np.ndarray) -> np.ndarray:
    h, _w = content.shape
    pts: list[tuple[int, int]] = []
    for y in range(0, h, 2):
        row = content[y]
        if not row.any():
            continue
        xs = np.where(row)[0]
        if int(xs[-1] - xs[0] + 1) < 80:
            continue
        pts.append((int(xs[0]), y))
        pts.append((int(xs[-1]), y))
    return np.asarray(pts, dtype=float)


def aa_circle_mask(size: int, cx: float, cy: float, radius: float) -> np.ndarray:
    """Float mask in [0,1] with sub-pixel coverage at the circle edge."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    dist = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    # 1 inside, 0 outside, linear falloff across ~1 px at boundary
    return np.clip(radius + 0.5 - dist, 0.0, 1.0)


def extract_clean_circle(src: Image.Image) -> Image.Image:
    rgb = np.asarray(src.convert("RGB"), dtype=np.float64)
    white = (rgb[:, :, 0] > 248) & (rgb[:, :, 1] > 248) & (rgb[:, :, 2] > 248)
    content = ~white

    edge_pts = collect_edge_points(content)
    cx, cy, r = fit_circle(edge_pts)

    # Cut away the irregular tip / JPEG fringe outside the true disc
    r_use = r - 1.5

    # Build square output at exact print diameter later; first extract at native res
    side = int(np.ceil(2 * r_use))
    if side % 2 == 0:
        side += 1  # odd size so center lands on a pixel

    out_cx = out_cy = (side - 1) / 2.0
    # Map: out pixel (i,j) <- source (cx + (i-out_cx), ...)
    yy, xx = np.mgrid[0:side, 0:side]
    src_x = cx + (xx - out_cx)
    src_y = cy + (yy - out_cy)

    # Bilinear sample
    x0 = np.floor(src_x).astype(int)
    y0 = np.floor(src_y).astype(int)
    x1 = x0 + 1
    y1 = y0 + 1
    x0c = np.clip(x0, 0, src.width - 1)
    x1c = np.clip(x1, 0, src.width - 1)
    y0c = np.clip(y0, 0, src.height - 1)
    y1c = np.clip(y1, 0, src.height - 1)

    wa = (x1 - src_x) * (y1 - src_y)
    wb = (src_x - x0) * (y1 - src_y)
    wc = (x1 - src_x) * (src_y - y0)
    wd = (src_x - x0) * (src_y - y0)

    sampled = (
        rgb[y0c, x0c] * wa[..., None]
        + rgb[y0c, x1c] * wb[..., None]
        + rgb[y1c, x0c] * wc[..., None]
        + rgb[y1c, x1c] * wd[..., None]
    )

    mask = aa_circle_mask(side, out_cx, out_cy, r_use)
    white_bg = np.array([255.0, 255.0, 255.0])
    composited = sampled * mask[..., None] + white_bg * (1.0 - mask[..., None])
    composited = np.clip(composited, 0, 255).astype(np.uint8)

    # Force anything outside the hard circle to pure white (no brown bleed)
    hard = mask >= 0.5
    composited[~hard] = 255

    # Re-apply 1px AA only at boundary against pure white
    soft = aa_circle_mask(side, out_cx, out_cy, (side - 1) / 2.0 - 0.5)
    result = (
        composited.astype(np.float64) * soft[..., None]
        + white_bg * (1.0 - soft[..., None])
    )
    result = np.clip(result, 0, 255).astype(np.uint8)
    # Absolute guarantee: far outside is 255
    result[soft < 0.01] = 255
    return Image.fromarray(result, "RGB")


def build_a4(circle: Image.Image) -> Image.Image:
    a4_w = mm_to_px(A4_W_MM)
    a4_h = mm_to_px(A4_H_MM)
    diam = mm_to_px(DIAMETER_MM)

    resized = circle.resize((diam, diam), Image.Resampling.LANCZOS)
    arr = np.asarray(resized, dtype=np.float64)
    soft = aa_circle_mask(diam, (diam - 1) / 2.0, (diam - 1) / 2.0, (diam - 1) / 2.0)
    white_bg = np.array([255.0, 255.0, 255.0])
    clean = arr * soft[..., None] + white_bg * (1.0 - soft[..., None])
    clean = np.clip(clean, 0, 255).astype(np.uint8)
    clean[soft < 0.01] = 255
    circle_clean = Image.fromarray(clean, "RGB")

    page = Image.new("RGB", (a4_w, a4_h), (255, 255, 255))
    x = (a4_w - diam) // 2
    y = (a4_h - diam) // 2
    page.paste(circle_clean, (x, y))
    return page


def main() -> None:
    if not SOURCE.exists():
        raise SystemExit(f"Missing source image: {SOURCE}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    src = Image.open(SOURCE)
    circle = extract_clean_circle(src)
    page = build_a4(circle)

    circle_path = OUT_DIR / "squirrels-birthday-11cm-circle.png"
    a4_png = OUT_DIR / "squirrels-birthday-11cm-A4.png"
    a4_pdf = OUT_DIR / "squirrels-birthday-11cm-A4.pdf"
    a4_jpg = OUT_DIR / "squirrels-birthday-11cm-A4.jpg"

    circle.save(circle_path, "PNG", dpi=(DPI, DPI))
    page.save(a4_png, "PNG", dpi=(DPI, DPI))
    page.save(a4_jpg, "JPEG", quality=95, dpi=(DPI, DPI), subsampling=0)
    page.save(a4_pdf, "PDF", resolution=float(DPI))

    diam = mm_to_px(DIAMETER_MM)
    print(f"A4: {page.size[0]}x{page.size[1]} px @ {DPI} DPI")
    print(f"Circle diameter: {diam} px = {diam / DPI * 25.4:.3f} mm")
    print(f"Wrote {circle_path.name}, {a4_png.name}, {a4_jpg.name}, {a4_pdf.name}")


if __name__ == "__main__":
    main()
