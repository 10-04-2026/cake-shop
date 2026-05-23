#!/usr/bin/env python3
"""Download free-licensed stock photos for catalog and design previews."""
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
DES = ROOT / "design-images"

HEADERS = {"User-Agent": "kisura-cake-shop/1.0 (local setup)"}

# Unsplash (free license) + Wikimedia CC BY for medovik
CAKES = [
    ("01-medovik.jpg", "https://commons.wikimedia.org/wiki/Special:FilePath/Honey_cake_Medovik.jpg"),
    ("02-vishnya-shokolad.jpg", "https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&h=1100&q=85"),
    ("03-klubnika-plombir.jpg", "https://images.unsplash.com/photo-1565958011703-44f9829ba187?auto=format&fit=crop&w=900&h=1100&q=85"),
    ("04-fistashka-malina.jpg", "https://images.unsplash.com/photo-1488477181946-6428a0291778?auto=format&fit=crop&w=900&h=1100&q=85"),
    ("05-tiramisu.jpg", "https://images.unsplash.com/photo-1571877227200-a6d38bc8428a?auto=format&fit=crop&w=900&h=1100&q=85"),
    ("06-morkovnyy.jpg", "https://images.unsplash.com/photo-1621303836404-76a99d9e0a1f?auto=format&fit=crop&w=900&h=1100&q=85"),
    ("07-nutella-orehi.jpg", "https://images.unsplash.com/photo-1606313564200-e75d5e30476e?auto=format&fit=crop&w=900&h=1100&q=85"),
    ("08-snikers.jpg", "https://images.unsplash.com/photo-1624353365286-3f8d62daad51?auto=format&fit=crop&w=900&h=1100&q=85"),
]

DESIGNS = [
    ("01-lambet.jpg", "https://images.unsplash.com/photo-1519676860739-48c1a490b825?auto=format&fit=crop&w=900&h=700&q=85"),
    ("02-waffle.jpg", "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7440?auto=format&fit=crop&w=900&h=700&q=85"),
    ("03-italian.jpg", "https://images.unsplash.com/photo-1464347694141-4f71b83ad7ab?auto=format&fit=crop&w=900&h=700&q=85"),
    ("04-oval-lambet.jpg", "https://images.unsplash.com/photo-1527529480127-669f9aee5090?auto=format&fit=crop&w=900&h=700&q=85"),
    ("05-custom.jpg", "https://images.unsplash.com/photo-1464349095432-e9a21285b5f5?auto=format&fit=crop&w=900&h=700&q=85"),
]


def fetch(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    if len(data) < 5000:
        raise RuntimeError(f"too small ({len(data)} bytes)")
    dest.write_bytes(data)


def main() -> int:
    IMG.mkdir(parents=True, exist_ok=True)
    DES.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for folder, items in ((IMG, CAKES), (DES, DESIGNS)):
        for name, url in items:
            dest = folder / name
            try:
                print(f"Downloading {name}...")
                fetch(url, dest)
                print(f"  OK {len(dest.read_bytes()) // 1024} KB")
                ok += 1
            except Exception as err:
                print(f"  FAIL: {err}")
                fail += 1
    print(f"Done: {ok} ok, {fail} failed")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
