#!/usr/bin/env python3
"""
The mini route map on the cover.

Drawn from the SAME frozen OSRM geometry the website uses (ROUTE.*.geom
in data.js), so the roads bend the way the real roads bend. Projected
with the cosine-latitude correction -- without it a degree of longitude
is treated as equal to a degree of latitude and every ridge and bend
reads stretched east-west.
"""
import math

# Bounding box chosen to contain all three legs with a little air.
LON0, LON1 = -83.99, -82.95
LAT0, LAT1 = 35.38, 36.10
W_MM = 55.0

_ASPECT = math.cos(math.radians((LAT0 + LAT1) / 2))          # ~0.812
H_MM = W_MM * (LAT1 - LAT0) / ((LON1 - LON0) * _ASPECT)


def project(lat, lon):
    x = (lon - LON0) / (LON1 - LON0) * W_MM
    y = (lat - LAT0) / (LAT1 - LAT0) * H_MM                  # TikZ y grows up
    return x, y


def _path(geom, step=2):
    pts = []
    for i, (la, lo) in enumerate(geom):
        if i % step and 0 < i < len(geom) - 1:
            continue
        x, y = project(la, lo)
        pts.append(f"({x:.2f},{y:.2f})")
    return "--".join(pts)


# Ridges suggest terrain without pretending to be topography.
def _ridges():
    out = []
    for i, (base, amp, op) in enumerate([(0.30, 1.5, 0.13), (0.46, 1.3, 0.10),
                                         (0.62, 1.1, 0.08)]):
        pts = []
        for k in range(31):
            x = k * W_MM / 30
            y = base * H_MM + amp * math.sin(k * 0.6 + i * 1.4) \
                            + amp * 0.5 * math.sin(k * 1.3 + i)
            pts.append(f"({x:.1f},{y:.1f})")
        out.append(rf"\draw[gprim,line width=0.35pt,opacity={op}] {'--'.join(pts)};")
    return out


# The TN/NC line follows the Smokies crest, south-west to north-east.
BORDER = [(35.30, -83.95), (35.45, -83.62), (35.5628, -83.4985),
          (35.611, -83.4249), (35.70, -83.29), (35.77, -83.16),
          (35.86, -82.99), (35.93, -82.90)]


def tikz(route):
    d = [r"\begin{tikzpicture}[x=1mm,y=1mm,line cap=round,line join=round]",
         rf"\useasboundingbox (-1,-3.2) rectangle ({W_MM+1:.1f},{H_MM+3.2:.1f});"]
    d += _ridges()

    d.append(rf"\draw[gfair,line width=0.4pt,dash pattern=on 0.7pt off 1.4pt,opacity=0.65]"
             rf" {_path(BORDER, 1)};")
    bx, by = project(35.80, -83.72)
    d.append(rf"\node[anchor=center] at ({bx:.1f},{by:.1f})"
             r" {{\capstight\fontsize{4.4}{5}\selectfont\color{gfair}TENNESSEE}};")
    bx, by = project(35.52, -83.62)
    d.append(rf"\node[anchor=center] at ({bx:.1f},{by:.1f})"
             r" {{\capstight\fontsize{4.4}{5}\selectfont\color{gfair}N. CAROLINA}};")

    # Legs: day one solid, day two lighter, the way home in gold.
    d.append(rf"\draw[gprim,line width=1.05pt] {_path(route['knox_mvc']['geom'])};")
    d.append(rf"\draw[gfair,line width=0.95pt] {_path(route['chalet_seq']['geom'])};")
    d.append(rf"\draw[gold,line width=0.8pt,dash pattern=on 1.6pt off 1.3pt]"
             rf" {_path(route['seq_knox_441']['geom'])};")

    # Passes and landmarks worth naming.
    for lat, lon, label, dx, dy, anchor in [
        (35.760, -83.100, "Pigeon River Gorge", 1.4,  0.6, "west"),
        (35.518, -83.195, "Soco Gap 4,340\\,ft", -2.2, 1.9, "east"),
        (35.611, -83.425, "Newfound Gap 5,046\\,ft", -1.4, 0.9, "east"),
    ]:
        x, y = project(lat, lon)
        d.append(rf"\fill[gfair] ({x:.1f},{y:.1f}) circle (0.55);")
        d.append(rf"\node[anchor={anchor}] at ({x+dx:.1f},{y+dy:.1f})"
                 rf" {{{{\numlight\fontsize{{4.6}}{{5.6}}\selectfont\color{{ink}}{label}}}}};")

    # The three stops.
    for lat, lon, n, label, dx, dy, anchor in [
        (35.96528, -83.91978, "1", "KNOXVILLE",  0.0,  3.4, "south"),
        (35.52258, -83.04821, "2", "MAGGIE VALLEY", 3.2, -0.2, "west"),
        (35.43208, -83.33605, "3", "SEQUOYAH",  0.0, -3.4, "north"),
    ]:
        x, y = project(lat, lon)
        d.append(rf"\fill[gprim] ({x:.1f},{y:.1f}) circle (1.65);")
        d.append(rf"\draw[gprim,line width=0.3pt,opacity=0.45] ({x:.1f},{y:.1f}) circle (2.5);")
        d.append(rf"\node[anchor=center,inner sep=0pt] at ({x:.1f},{y-0.05:.1f})"
                 rf" {{{{\num\fontsize{{4.6}}{{5}}\selectfont\color{{cream}}{n}}}}};")
        d.append(rf"\node[anchor={anchor}] at ({x+dx:.1f},{y+dy:.1f})"
                 rf" {{{{\capstight\fontsize{{5}}{{6}}\selectfont\color{{gdeep}}{label}}}}};")

    d.append(r"\end{tikzpicture}")
    return "\n".join(d)
