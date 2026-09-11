#!/usr/bin/env python3
"""
Prepare static TTFs for the handout.

WHY THIS EXISTS: Marcellus, Barlow Condensed and Nanum Myeongjo ship
as ordinary static fonts and are copied straight through. Cormorant
Garamond and Source Serif 4 are published ONLY as variable fonts, and
XeTeX (which Tectonic runs) renders just a variable font's default
instance. Cormorant's default is Light 300 -- so without the
instancing below, the entire card would silently set too thin and
would not match the website.

The site's own .woff2 files cannot be reused: the Latin ones are
subset to Latin, and Korean is split across 184 unicode-range slices.

Run via build.py; it is also importable on its own.
"""
import pathlib, urllib.request, shutil, sys

HERE = pathlib.Path(__file__).resolve().parent
SRC  = HERE / "fonts" / "src"
OUT  = HERE / "fonts"
RAW  = "https://github.com/google/fonts/raw/main/ofl"
UA   = {"User-Agent": "Mozilla/5.0 (smi-handout-build)"}

# name on disk -> url path
DOWNLOAD = {
    "CormorantGaramond[wght].ttf":        f"{RAW}/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
    "CormorantGaramond-Italic[wght].ttf": f"{RAW}/cormorantgaramond/CormorantGaramond-Italic%5Bwght%5D.ttf",
    "SourceSerif4[opsz,wght].ttf":        f"{RAW}/sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf",
    "Marcellus-Regular.ttf":              f"{RAW}/marcellus/Marcellus-Regular.ttf",
    "BarlowCondensed-Regular.ttf":        f"{RAW}/barlowcondensed/BarlowCondensed-Regular.ttf",
    "BarlowCondensed-SemiBold.ttf":       f"{RAW}/barlowcondensed/BarlowCondensed-SemiBold.ttf",
    "NanumMyeongjo-Regular.ttf":          f"{RAW}/nanummyeongjo/NanumMyeongjo-Regular.ttf",
    "NanumMyeongjo-Bold.ttf":             f"{RAW}/nanummyeongjo/NanumMyeongjo-Bold.ttf",
}

# variable source -> [(output name, {axis: value}), ...]
INSTANCE = {
    "CormorantGaramond[wght].ttf": [
        ("CormorantGaramond-Regular.ttf",  {"wght": 400}),
        ("CormorantGaramond-SemiBold.ttf", {"wght": 600}),
    ],
    "CormorantGaramond-Italic[wght].ttf": [
        ("CormorantGaramond-Italic.ttf",   {"wght": 400}),
    ],
    # opsz 11 is the optical size meant for small text, which is all
    # this card contains.
    "SourceSerif4[opsz,wght].ttf": [
        ("SourceSerif4-Regular.ttf",  {"opsz": 11, "wght": 400}),
        ("SourceSerif4-SemiBold.ttf", {"opsz": 11, "wght": 600}),
    ],
}

COPY = ["Marcellus-Regular.ttf", "BarlowCondensed-Regular.ttf",
        "BarlowCondensed-SemiBold.ttf",
        "NanumMyeongjo-Regular.ttf", "NanumMyeongjo-Bold.ttf"]


def fetch(quiet=False):
    SRC.mkdir(parents=True, exist_ok=True)
    for name, url in DOWNLOAD.items():
        dest = SRC / name
        if dest.exists() and dest.stat().st_size > 20_000:
            if not quiet: print(f"    cached  {name}")
            continue
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=120).read()
        dest.write_bytes(data)
        if not quiet: print(f"    fetched {name:<38}{len(data):>10,}")


def build(quiet=False):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    OUT.mkdir(parents=True, exist_ok=True)
    for name in COPY:
        shutil.copy(SRC / name, OUT / name)
        if not quiet: print(f"    static  {name}")

    for src, targets in INSTANCE.items():
        for out_name, axes in targets:
            font = TTFont(SRC / src)
            instancer.instantiateVariableFont(font, axes, inplace=True, updateFontNames=True)
            font.save(OUT / out_name)
            font.close()
            axis_desc = " ".join(f"{k}={v}" for k, v in axes.items())
            if not quiet: print(f"    instanced {out_name:<36}{axis_desc}")


def main():
    print("  downloading source faces")
    fetch()
    print("  generating static instances")
    build()
    total = sum(p.stat().st_size for p in OUT.glob("*.ttf"))
    print(f"  {len(list(OUT.glob('*.ttf')))} faces ready, {total/1e6:.1f} MB")


if __name__ == "__main__":
    main()
