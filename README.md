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

## The game

**Nothing is decided.** `match.html` lays out three formats to argue
about, all of them two teams of three, and all of them keeping your
own ball and your own scorecard — which is why none is a scramble.

The page has a **team builder**: tap anyone between the two sides and
it tells you in plain words how even the match looks, with a button
that finds the evenest split of the six. Nothing is saved; it exists
to settle an argument in ten seconds.

**Mulligans:** six per team per round, used at the team's discretion.
A seventh costs $10 into the prize pool. Both numbers are
`MULLIGANS` in `data.js`.

Add a format by appending one object to `FORMATS` in `data.js` — the
cards on the page render from it.

---

## The printed handout

`tools/handout/build.py` generates a **personalised folded booklet for
each of the six** — one Letter sheet, printed double-sided and folded
once into four 5.5 × 8.5″ panels:

| Panel | Contents |
|---|---|
| Front cover | The invitation, their name set large, and a route map drawn from the real road geometry |
| Inside left | Maggie Valley: five holes worth knowing, then the team card and that round's mulligans |
| Inside right | Sequoyah National: same, including the Cherokee-named holes |
| Back cover | Personal scorecards for both rounds, with par, yardage and stroke index |

The inside panels carry the **team** card — three score rows and a
total, per nine — while the back carries your **own** scorecard. They
are deliberately different things: the match is settled on team
scores, which a personal card cannot record.

```
python3 tools/handout/build.py
```

Outputs land in `handouts/`: `smi-2026-<name>.pdf` reads on screen in
page order, and `smi-2026-<name>-print.pdf` is imposed for printing.
**Print double-sided, flip on the SHORT edge, then fold once.** These
pages are landscape, so a long-edge flip puts the inside spread upside
down — test one sheet before running all six.

Needs `tectonic` (`brew install tectonic`) and a network connection the
first time, to fetch TeX packages and fonts. Everything else
bootstraps itself.

Two things worth knowing about how it is built:

- **Fonts are instanced, not just downloaded.** Cormorant Garamond and
  Source Serif 4 are published only as variable fonts, and XeTeX
  renders a variable font's *default* instance — which for Cormorant is
  Light 300. Left alone the whole booklet would set too thin and would
  not match the site. `tools/handout/fonts.py` generates proper static
  weights first.
- **The hole diagrams and the route map are original.** The diagrams
  are schematics drawn from the published written descriptions, not
  traced from either club's copyrighted hole graphics. The cover map
  is projected from the same frozen OSRM geometry the website uses,
  with a cosine-latitude correction so the bends are the real bends.
- **Every panel must fit on one page.** The booklet folds from a single
  sheet, so a fifth page makes it unfoldable. Panels run close to full,
  so `build.py` checks the page count and fails loudly rather than
  quietly emitting something that cannot be folded. To measure the
  headroom, wrap a panel in `\setbox0=\vbox{...}` and print `\the\ht0`
  against `\the\textheight` (560.8pt).

---

## Editing

| To change | Edit |
|---|---|
| Scores, handicaps, tees, tee times, formats, mulligans, route legs | `assets/js/data.js` |
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
2. Maggie Valley's Gold tee rating — unpublished and currently
   estimated. Three of you play it.
3. Women's ratings for Sequoyah's Bronze tee; the published figures
   look like a men's set. Worth a call, but it only moves a shot or
   two.
4. The Korean spelling of everyone's name in `data.js` — romanised
   guesses at present.

**Settled since launch:** stroke index and hole-by-hole par and
yardage are now the real published figures for both courses. Maggie
Valley's per-hole yardages sum exactly to all four published tee
totals. Sequoyah's per-hole set sums ~110 above the club's stated
totals — sources for that course disagree — so the booklet prints its
per-hole yardages without a total, rather than contradicting itself.

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
