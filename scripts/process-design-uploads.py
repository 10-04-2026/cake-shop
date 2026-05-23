#!/usr/bin/env python3
"""
Обработка ваших фото стилей: один фон, один размер для сайта.

1. Положите исходники в design-images/uploads/ (любые имена).
2. Переименуйте или положите сразу:
   upload-01-lambet.jpg, upload-02-waffle.jpg, … upload-05-custom.jpg
   (или один файл — укажите в чате какой стиль).
3. Запуск: python3 scripts/process-design-uploads.py

Готовые файлы: design-images/01-lambet.jpg … 05-custom.jpg
"""
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:
    raise SystemExit("Установите Pillow: pip3 install Pillow")

ROOT = Path(__file__).resolve().parents[1]
UPLOAD = ROOT / "design-images" / "uploads"
OUT = ROOT / "design-images"

# Фон как на сайте (styles.css --bg-base)
BG_RGB = (246, 243, 239)
OUT_W, OUT_H = 1200, 900
PADDING = 48

STYLES = [
    ("01-lambet.jpg", "upload-01-lambet"),
    ("02-waffle.jpg", "upload-02-waffle"),
    ("03-italian.jpg", "upload-03-italian"),
    ("04-oval-lambet.jpg", "upload-04-oval-lambet"),
    ("05-custom.jpg", "upload-05-custom"),
]

EXTS = (".jpg", ".jpeg", ".png", ".webp", ".heic", ".HEIC")


def find_upload(stem: str) -> Optional[Path]:
    for ext in EXTS:
        p = UPLOAD / f"{stem}{ext}"
        if p.is_file():
            return p
    return None


def fit_on_canvas(src: Path, dest: Path) -> None:
    img = Image.open(src).convert("RGB")
    canvas = Image.new("RGB", (OUT_W, OUT_H), BG_RGB)
    max_w = OUT_W - 2 * PADDING
    max_h = OUT_H - 2 * PADDING
    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
    x = (OUT_W - img.width) // 2
    y = (OUT_H - img.height) // 2
    canvas.paste(img, (x, y))
    canvas.save(dest, "JPEG", quality=88, optimize=True)
    print(f"  -> {dest.name} ({dest.stat().st_size // 1024} KB)")


def main() -> int:
    UPLOAD.mkdir(parents=True, exist_ok=True)
    ok = 0
    for out_name, stem in STYLES:
        src = find_upload(stem)
        if not src:
            print(f"Пропуск {out_name}: нет {stem}.* в uploads/")
            continue
        print(f"Обработка {src.name}...")
        fit_on_canvas(src, OUT / out_name)
        ok += 1
    print(f"\nГотово: {ok} из {len(STYLES)}")
    if ok == 0:
        print(f"Положите файлы в: {UPLOAD}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
