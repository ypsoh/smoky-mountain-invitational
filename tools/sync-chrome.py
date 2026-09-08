#!/usr/bin/env python3
"""
Sync the shared nav and footer into every root-level page.

The nav and footer are DUPLICATED verbatim in each page rather than
injected at runtime, so navigation never depends on JavaScript and
works offline and from file://. This script keeps those copies from
drifting: edit tools/chrome/nav.html or footer.html, run this, done.

It rewrites only the text BETWEEN the sentinel comments, and sets
aria-current="page" on whichever nav item matches each filename.

    python3 tools/sync-chrome.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BLOCKS = {
    "NAV":    (ROOT / "tools/chrome/nav.html").read_text().strip(),
    "FOOTER": (ROOT / "tools/chrome/footer.html").read_text().strip(),
}

def sync(path):
    html, page, changed = path.read_text(), path.stem, False
    for key, body in BLOCKS.items():
        start = f"<!-- #region SHARED-{key} v1 -->"
        end   = f"<!-- #endregion SHARED-{key} -->"
        if start not in html:
            continue
        b = body
        if key == "NAV":
            # Mark the current page in STATIC html, so no JS is needed.
            b = b.replace(f'data-page="{page}"', f'data-page="{page}" aria-current="page"')
        new = f"{start}\n{b}\n{end}"
        pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
        if pat.search(html) and pat.search(html).group(0) != new:
            html, changed = pat.sub(lambda _: new, html, count=1), True
    if changed:
        path.write_text(html)
    return changed

pages = sorted(p for p in ROOT.glob("*.html"))
if not pages:
    sys.exit("no pages found")
for p in pages:
    print(("  synced  " if sync(p) else "  ok      ") + p.name)
