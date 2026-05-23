#!/usr/bin/env python3
"""Download design previews from Pixabay CDN (Pixabay License)."""
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DES = ROOT / "design-images"

# Direct cdn.pixabay.com links — free for commercial use (Pixabay License)
PHOTOS = [
    ("01-lambet.jpg", "https://cdn.pixabay.com/photo/2017/07/31/19/40/wedding-cake-2559500_1280.jpg"),
    ("02-waffle.jpg", "https://cdn.pixabay.com/photo/2017/01/22/19/05/waffles-1999276_1280.jpg"),
    ("03-italian.jpg", "https://cdn.pixabay.com/photo/2017/05/04/23/43/berry-2283219_1280.jpg"),
    ("04-oval-lambet.jpg", "https://cdn.pixabay.com/photo/2016/11/18/22/42/wedding-cake-1835088_1280.jpg"),
    ("05-custom.jpg", "https://cdn.pixabay.com/photo/2017/08/06/13/06/wedding-cake-2596764_1280.jpg"),
]

FALLBACK = [
    ("01-lambet.jpg", "https://cdn.pixabay.com/photo/2016/03/20/09/21/fruit-1267259_1280.jpg"),
    ("03-italian.jpg", "https://cdn.pixabay.com/photo/2016/03/05/19/02/dessert-1199327_1280.jpg"),
    ("04-oval-lambet.jpg", "https://cdn.pixabay.com/photo/2017/01/20/15/06/wedding-cake-1995015_1280.jpg"),
    ("05-custom.jpg", "https://cdn.pixabay.com/photo/2018/12/12/11/34/cake-3865842_1280.jpg"),
]


def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; kisura-site/1.0)"},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = resp.read()
    if len(data) < 20000:
        raise RuntimeError(f"too small ({len(data)} bytes)")
    dest.write_bytes(data)


def main() -> int:
    DES.mkdir(parents=True, exist_ok=True)
    fb = dict(FALLBACK)
    ok = fail = 0
    for fname, url in PHOTOS:
        dest = DES / fname
        urls = [url, fb.get(fname, url)]
        done = False
        for i, u in enumerate(dict.fromkeys(urls)):
            try:
                if i:
                    time.sleep(2)
                print(f"Downloading {fname}...")
                download(u, dest)
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
