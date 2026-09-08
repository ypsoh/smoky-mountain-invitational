#!/usr/bin/env python3
"""
Static integrity check. Run before deploying.

Verifies every local href/src in the HTML and every url() in the CSS
resolves to a file that actually exists, WITH EXACT CASE. macOS is
case-insensitive and GitHub Pages (Linux) is not, so a link that
works locally can 404 in production -- this is the single most
common Pages-only regression, and this check is what catches it.

Also flags any word we have committed to never shipping.

    python3 tools/check.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors, checked = [], 0

def exists_exact(rel: str) -> bool:
    p = (ROOT / rel)
    if not p.exists():
        return False
    # Walk the path confirming each segment's real on-disk spelling.
    cur = ROOT
    for part in pathlib.Path(rel).parts:
        names = {c.name for c in cur.iterdir()}
        if part not in names:
            return False
        cur = cur / part
    return True

def check(src_file, ref, kind):
    global checked
    if re.match(r'^(https?:|mailto:|tel:|#|data:)', ref):
        return
    target = ref.split('#')[0].split('?')[0]
    if not target:
        return
    checked += 1
    rel = (src_file.parent / target).resolve().relative_to(ROOT).as_posix()
    if not exists_exact(rel):
        errors.append(f"{src_file.name}: {kind} -> {ref}  (missing or wrong case)")

for f in sorted(ROOT.glob("*.html")):
    t = f.read_text()
    for ref in re.findall(r'(?:href|src)="([^"]+)"', t):
        check(f, ref, "link")

for f in sorted((ROOT / "assets/css").glob("*.css")):
    t = f.read_text()
    for ref in re.findall(r'url\(([^)]+)\)', t):
        check(f, ref.strip('\'"'), "url()")

# Names and marks we have committed to never shipping.
BANNED = ["amen corner", "augusta national", "green jacket",
          "tradition unlike", "butler cabin"]
for f in sorted(ROOT.glob("*.html")):
    low = f.read_text().lower()
    for b in BANNED:
        if b in low:
            errors.append(f"{f.name}: contains banned phrase {b!r}")
    # "masters" as a word, but allow "mastersXYZ"-free plain prose checks
    if re.search(r'\bmasters\b', low):
        errors.append(f"{f.name}: contains the word 'masters'")

print(f"checked {checked} local references across "
      f"{len(list(ROOT.glob('*.html')))} pages")
if errors:
    print("\nFAILED:")
    for e in errors:
        print("  " + e)
    sys.exit(1)
print("all references resolve, no banned terms present")
