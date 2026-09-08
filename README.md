# The Smoky Mountain Invitational

A private site for a two-day golf trip to western North Carolina,
**12–13 September 2026** — Maggie Valley Club on the Saturday and
Sequoyah National on the Sunday.

Plain HTML, CSS and JavaScript. **No build step, no npm, no
dependencies to install.**

---

## Running it

Either works:

```
open index.html                 # double-click also works
python3 -m http.server 8000     # then visit http://localhost:8000/
```

Use the server before deploying. macOS filesystems are
case-insensitive and GitHub Pages is not, so a link like
`Players.html` works locally and 404s in production. `tools/check.py`
catches that.

---

## Entering scores during the trip

Everything lives in one place. Open `assets/js/data.js`, scroll to the
`SCORES` block at the bottom, and type gross strokes into the eighteen
slots for each player:

```js
soh:  [5,4,4,6,4,6,3,5,4, 5,4,4,6,5,3,5,5,6],
```

Leave `N` for holes not yet played — a partial round scores correctly
and only completed holes count. Save the file and refresh `match.html`.
No build, no server, no signal required.

**Before the first tee**, copy the real stroke index off each printed
scorecard into `strokeIndex`. Neither club publishes it, the site ships
with a placeholder, and it silently changes *every* net score.

---

## The match

Three a side, **best two of three net scores per hole**, hole points
accumulating across all thirty-six, at a 90% Playing Handicap
allowance (`ALLOWANCE` in `data.js` — change the one number).

Straight aggregate net was rejected deliberately: one blow-up hole
from the highest handicap would swing a two-day match, which makes
that player a structural liability and, worse, makes them feel like
one. Best-two-of-three lets anyone detonate a hole for free while
still requiring all six to play.

Teams balance to within two strokes on each day and land dead even,
98–98, across the full thirty-six.

---

## Editing

| To change | Edit |
|---|---|
| Scores, handicaps, tees, tee times, course data, route legs | `assets/js/data.js` |
| Nav or footer | `tools/chrome/*.html`, then run `python3 tools/sync-chrome.py` |
| Colours, type scale, spacing | `assets/css/tokens.css` |
| Korean text | the `.ko` spans in the HTML, alongside their `.en` twin |

**Nav and footer are duplicated in every page on purpose.** Fetching a
partial fails from `file://`, and injecting them with JavaScript would
put navigation behind a script. `tools/sync-chrome.py` keeps the seven
copies identical and sets `aria-current` per page.

Run `python3 tools/check.py` before deploying. It verifies every local
link and `url()` resolves with exact case.

---

## Things that are deliberate

- **Scripts are classic scripts, never `type="module"`.** Modules are
  CORS-blocked from `file://`, and this site has to open by
  double-clicking.
- **Fonts and Leaflet are vendored, not loaded from a CDN.** The trip
  crosses Pigeon River Gorge, Soco Gap and the Qualla Boundary, all of
  which have poor or no coverage.
- **The illustrated SVG map is the primary artefact.** The Leaflet map
  below it needs tiles, so it is an enhancement and degrades to a
  notice when offline.
- **`sessionStorage` and `localStorage` access is wrapped in
  try/catch.** Safari throws `SecurityError` on both from `file://`.
- **The envelope animation defaults to OPEN.** The sealed state is
  applied only by an inline script; with JavaScript off the invitation
  is simply a readable page.
- **No dark mode.** A second palette doubles the ways the
  green + cream + one-accent rule can break.

---

## Still to confirm

1. The second tee time at each course (shown as +10 min, inferred).
2. Stroke index and hole-by-hole par from both printed scorecards.
3. Maggie Valley's Gold and Green tee ratings — unpublished, currently
   estimated, and they feed the handicap maths.
4. Women's ratings for Sequoyah's Bronze and Jade tees; the published
   figures look like a men's set.
5. The Korean spelling of everyone's name in `data.js` — romanised
   guesses at present.

---

## Deploying

Ready for GitHub Pages as-is: all paths are relative, all pages sit at
the repo root, `.nojekyll` and `404.html` are in place, and every page
carries `noindex`.

Note that **free GitHub Pages from a private repo still publishes a
public URL.** Fine for six friends with `noindex`; if you want real
access control, Cloudflare Pages plus Access is free and needs no code
change.

---

## Licences and attribution

- Fonts: Cormorant Garamond, Source Serif 4, Marcellus, Barlow
  Condensed and Nanum Myeongjo, all under the SIL Open Font License
  1.1, self-hosted as permitted.
- Maps: Leaflet (BSD-2-Clause), vendored. Tiles © OpenTopoMap
  (CC-BY-SA), map data © OpenStreetMap contributors and SRTM. Route
  geometry from the public OSRM router, fetched once and frozen into
  `data.js`.
- Course facts are compiled from public sources and may be out of
  date. Confirm with the pro shop.

A private gathering of friends. Not affiliated with, endorsed by, or
connected to any professional golf tournament, club, or organisation.
