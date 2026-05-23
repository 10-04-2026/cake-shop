#!/usr/bin/env python3
"""Download design preview images from Pexels (free license)."""
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DES = ROOT / "design-images"

# Pexels photo IDs — wedding cakes & desserts (pexels.com/license)
PHOTOS = [
    ("01-lambet.jpg", 265352),       # tiered white wedding cake
    ("02-waffle.jpg", 2961958),      # waffles close-up
    ("03-italian.jpg", 2915287),     # cake with berries
    ("04-oval-lambet.jpg", 1696088), # elegant wedding cake
    ("05-custom.jpg", 306071),       # wedding cake with flowers
]

FALLBACK = [
    ("01-lambet.jpg", 1028740),
    ("02-waffle.jpg", 708490),
    ("03-italian.jpg", 206756),
    ("04-oval-lambet.jpg", 1702373),
    ("05-custom.jpg", 1126359),
]


def url(photo_id: int) -> str:
    return (
        f"https://images.pexels.com/photos/{photo_id}/"
        f"pexels-photo-{photo_id}.jpeg"
        f"?auto=compress&cs=tinysrgb&w=1200&h=900&fit=crop"
    )


def download(photo_id: int, dest: Path) -> None:
    req = urllib.request.Request(
        url(photo_id),
        headers={"User-Agent": "Mozilla/5.0 (compatible; kisura-site/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    if len(data) < 15000:
        raise RuntimeError(f"too small ({len(data)} bytes)")
    dest.write_bytes(data)


def main() -> int:
    DES.mkdir(parents=True, exist_ok=True)
    fb_map = dict(FALLBACK)
    ok = fail = 0
    for fname, pid in PHOTOS:
        dest = DES / fname
        ids = [pid, fb_map.get(fname, pid)]
        done = False
        for i, photo_id in enumerate(dict.fromkeys(ids)):
            try:
                if i:
                    time.sleep(1)
                print(f"Downloading {fname} (pexels:{photo_id})...")
                download(photo_id, dest)
                print(f"  OK {len(dest.read_bytes()) // 1024} KB")
                ok += 1
                done = True
                break
            except Exception as err:
                print(f"  FAIL: {err}")
        if not done:
            fail += 1
    print(f"Done: {ok} ok, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
