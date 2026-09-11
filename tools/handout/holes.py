#!/usr/bin/env python3
"""
Notable-hole content and the little hole diagrams.

THE DIAGRAMS ARE ORIGINAL. They are simple schematics drawn from the
published written descriptions of each hole -- a corridor, a green, a
hazard. They are deliberately NOT traced from either club's hole
graphics, which are copyrighted, and they are stylised enough that
nobody should mistake them for a survey.

Yardages are from the tee the group actually plays: White at Maggie
Valley, Gold at Sequoyah.
"""

# shape:  straight | dogleg-left | dogleg-right | short | drop | uphill
# hazard: none | water-left | creek | marsh | blind | bunkers
NOTABLE = {
    "maggie": [
        dict(no=3, par=4, yds=430, si=1, shape="dogleg-left", hazard="water-left",
             title="가장 어려운 홀",
             desc="왼쪽 전체가 물입니다. 코너를 질러 각도를 만들면 롱아이언이 남고, "
                  "그린은 양옆이 벙커입니다. 스코어카드상 핸디캡 1번."),
        dict(no=12, par=3, yds=97, si=18, shape="short", hazard="none",
             title="가장 짧은 홀",
             desc="97야드. 코스에서 가장 짧고 가장 쉬운 홀입니다. "
                  "웨지 하나로 끝나지만, 여기서 못 줄이면 후반이 길어집니다."),
        dict(no=16, par=4, yds=360, si=4, shape="dogleg-left", hazard="uphill",
             title="후반의 시작",
             desc="가파른 오르막 좌도그렉. 페어웨이 벙커가 공략선에 놓여 있고 "
                  "그린은 뒤에서 앞으로 굴곡집니다. 카드보다 훨씬 길게 칩니다."),
        dict(no=17, par=4, yds=320, si=12, shape="straight", hazard="blind",
             title="그린이 보이지 않는 홀",
             desc="티에서 그린이 안 보입니다. 200야드 지점 벙커가 공략 지점을 정하고, "
                  "그린은 앞에서 뒤로 기울어 있어 붙이기가 어렵습니다."),
        dict(no=18, par=5, yds=489, si=6, shape="straight", hazard="creek",
             title="베란다 앞에서 끝나는 마무리",
             desc="크리크가 270야드 지점을 가로지른 뒤 오른쪽을 따라 올라갑니다. "
                  "2온이 가능하고, 정직한 레이업도 있습니다."),
    ],
    "sequoyah": [
        dict(no=2, par=3, yds=141, si=11, shape="short", hazard="marsh",
             title="Hornet Place",
             desc="습지를 전부 넘겨 돌담 위에 올린 그린을 공략합니다. "
                  "전부 캐리, 피할 곳은 없습니다."),
        dict(no=6, par=3, yds=219, si=1, shape="straight", hazard="bunkers",
             title="핸디캡 1번, 그런데 파3",
             desc="롱 파3가 코스에서 가장 어려운 홀인 경우는 드뭅니다. "
                  "티에서 그린까지 온전히 하나의 긴 샷입니다."),
        dict(no=11, par=5, yds=500, si=10, shape="drop", hazard="none",
             title="Long Man",
             desc="내리막 파5. 2온을 노려볼 만하지만 그린이 작습니다. "
                  "욕심을 낼지 말지 여기서 갈립니다."),
        dict(no=12, par=5, yds=539, si=2, shape="uphill", hazard="none",
             title="Trail of Tears",
             desc="코스에서 가장 긴 홀. 오르막으로 길게 이어져 넓지만 "
                  "굴곡진 그린에 닿습니다. 핸디캡 2번."),
        dict(no=15, par=4, yds=386, si=14, shape="drop", hazard="none",
             title="이 여행을 건 홀",
             desc="티에서 360도 전망, 맑은 날 지평선에 Kuwohi. 페어웨이까지 약 61m, "
                  "그린까지 다시 23m를 더 떨어집니다. 거리계가 240야드라 해도 180야드처럼 칩니다."),
    ],
}

GREEN, FAIR, GOLD, IVORY = "gprim", "gfair", "gold", "ivory"


def diagram(shape, hazard):
    """A 26 x 15 mm schematic: tee at the left, green at the right."""
    d = [r"\begin{tikzpicture}[x=1mm,y=1mm,line cap=round,line join=round]"]
    d.append(r"\useasboundingbox (0,-1) rectangle (26,15);")

    # ---- the corridor -------------------------------------------
    if shape == "dogleg-left":
        path, green = "(3,4) .. controls (11,4) and (14,6) .. (20,11)", (22, 12)
    elif shape == "dogleg-right":
        path, green = "(3,11) .. controls (11,11) and (14,9) .. (20,4)", (22, 3)
    elif shape == "short":
        path, green = "(8,7) -- (17,7)", (19.5, 7)
    else:                                   # straight / drop / uphill
        path, green = "(3,7) -- (19,7)", (21.5, 7)

    d.append(rf"\draw[{FAIR},line width=3.2pt,opacity=0.28] {path};")
    d.append(rf"\draw[{FAIR},line width=0.5pt,opacity=0.85] {path};")

    # ---- tee -----------------------------------------------------
    tx, ty = (8, 7) if shape == "short" else ((3, 4) if shape == "dogleg-left"
                                             else (3, 11) if shape == "dogleg-right" else (3, 7))
    d.append(rf"\fill[{GOLD}] ({tx-0.9},{ty-0.9}) rectangle ({tx+0.9},{ty+0.9});")

    # ---- green ---------------------------------------------------
    gx, gy = green
    d.append(rf"\fill[{GREEN}] ({gx},{gy}) circle (2.1);")
    d.append(rf"\draw[{GREEN},line width=0.4pt,opacity=0.5] ({gx},{gy}) circle (3.1);")

    # ---- elevation -----------------------------------------------
    if shape == "drop":          # chevrons pointing down the hill
        for i in range(3):
            x = 8 + i * 3.4
            d.append(rf"\draw[{GOLD},line width=0.55pt] ({x},9.6)--({x+1.5},8.4)--({x+3},9.6);")
    if shape == "uphill" or hazard == "uphill":
        for i in range(3):
            x = 8 + i * 3.4
            d.append(rf"\draw[{GOLD},line width=0.55pt] ({x},4.4)--({x+1.5},5.6)--({x+3},4.4);")

    # ---- hazards --------------------------------------------------
    if hazard == "water-left":
        d.append(rf"\fill[{FAIR},opacity=0.30] (2,0.5) rectangle (19,2.6);")
        for i in range(5):
            x = 3.4 + i * 3.1
            d.append(rf"\draw[{FAIR},line width=0.45pt,opacity=0.9] "
                     rf"({x},1.6) .. controls ({x+0.8},2.3) and ({x+1.6},0.9) .. ({x+2.4},1.6);")
    elif hazard == "creek":
        d.append(rf"\draw[{FAIR},line width=1.4pt,opacity=0.45] (13,1.5) -- (13,12.5);")
        d.append(rf"\draw[{FAIR},line width=0.45pt] (13,1.5) .. controls (14.2,5) and (11.8,9) .. (13,12.5);")
    elif hazard == "marsh":
        for r in range(3):
            for c in range(6):
                d.append(rf"\fill[{FAIR},opacity=0.45] ({9.5+c*1.5},{4.6+r*1.6}) circle (0.32);")
    elif hazard == "blind":
        d.append(rf"\draw[{GOLD},line width=0.7pt,dash pattern=on 1.4pt off 1.2pt] (12,2.5) -- (12,12);")
        d.append(rf"\fill[{GOLD}] (10.2,10.6) circle (0.85);")
    elif hazard == "bunkers":
        d.append(rf"\fill[{IVORY}] (17.6,10.2) circle (1.15);")
        d.append(rf"\fill[{IVORY}] (17.6,3.8) circle (1.15);")

    d.append(r"\end{tikzpicture}")
    return "\n".join(d)


# ---------------------------------------------------------------
# Panel builders. These live here rather than in build.py so the
# LaTeX fragments sit in plain raw strings with no second layer of
# escaping between Python and TeX.
# ---------------------------------------------------------------

def _esc(s):
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")]:
        s = s.replace(a, b)
    return s


def ref_strip(course, tee_key, yard_totals=True):
    """The whole card at a glance: hole, par, yards, stroke index."""
    par = course["parByHole"]
    yds = course.get("yardsByHole", {}).get(tee_key)
    si = course["strokeIndex"]

    def cells(vals, accent=False):
        col = "gdeep" if accent else "gfair"
        return " & ".join(
            r"{\numlight\fontsize{6.2}{8}\selectfont\color{" + col + r"}" + str(v) + "}"
            for v in vals)

    def row(label, vals, tot, accent=False):
        return (r"{\capstight\fontsize{5.2}{7}\selectfont\color{gfair}" + label + "} & "
                + cells(vals, accent)
                + r" & {\num\fontsize{6.2}{8}\selectfont\color{gold}" + str(tot) + r"} \\")

    def block(lo, hi, tot_label):
        sl = slice(lo, hi)
        hdr = " & ".join(
            r"{\capstight\fontsize{5.2}{7}\selectfont\color{gold}" + str(h) + "}"
            for h in range(lo + 1, hi + 1))
        out = [r"\begin{tabular}{@{}K|" + "R" * 9 + r"|U@{}}",
               r"{\capstight\fontsize{5.2}{7}\selectfont\color{gfair}HOLE} & " + hdr
               + r" & {\capstight\fontsize{5.2}{7}\selectfont\color{gold}" + tot_label + r"} \\",
               r"\hline",
               row("PAR", par[sl], sum(par[sl]), accent=True)]
        if yds:
            # Sequoyah's per-hole yardages come from a different scorecard
            # revision than the club's published tee totals and sum ~110
            # high. Printing both would contradict itself on a card meant
            # to be kept, so the totals are suppressed there.
            tot = format(sum(yds[sl]), ",") if yard_totals else "—"
            out.append(row("YDS", yds[sl], tot))
        out.append(row("HDCP", si[sl], "—"))
        out.append(r"\end{tabular}")
        return "\n".join(out)

    return (r"\begin{center}" + "\n" + block(0, 9, "OUT") + "\n" + r"\vspace{2pt}" + "\n"
            + block(9, 18, "IN") + "\n" + r"\end{center}")


def course_panel(course, tee, tee_key, title_en, sub_ko, key, yard_totals=True, note=None):
    """One inside panel: the card at a glance, then the holes worth knowing."""
    p = [r"\vspace{2pt}",
         r"\begin{center}",
         r"{\disp\fontsize{19}{21}\selectfont\color{gdeep} " + _esc(title_en) + r"}\\[3pt]",
         r"{\capstight\fontsize{6.2}{8}\selectfont\color{gfair} PAR " + str(course["par"]) + r"}\ "
         r"{\num\fontsize{8.5}{10}\selectfont\color{gdeep} " + tee["name"].upper()
         + r" \textperiodcentered\ " + format(tee["yards"], ",") + r"}\\[4pt]",
         r"{\fontsize{7.2}{10}\selectfont\color{gfair} " + sub_ko + "}",
         r"\end{center}",
         r"\vspace{5pt}",
         ref_strip(course, tee_key, yard_totals),
         r"\vspace{6pt}",
         r"\hairrule",
         r"\vspace{4pt}",
         r"\begin{center}\eyebrow{HOLES WORTH KNOWING \textperiodcentered\ 눈여겨볼 홀}\end{center}",
         r"\vspace{4pt}"]
    if note:
        p.insert(-1, r"\begin{center}{\fontsize{5.8}{7.6}\selectfont\color{gfair} "
                 + note + r"}\end{center}")
        p.insert(-1, r"\vspace{3pt}")

    for h in NOTABLE[key]:
        meta = (r"{\capstight\fontsize{5.6}{7}\selectfont\color{gfair} PAR "
                + str(h["par"]) + r" \textperiodcentered\ " + str(h["yds"])
                + r" YDS \textperiodcentered\ HDCP " + str(h["si"]) + "}")
        p += [
            r"\noindent\begin{minipage}{\linewidth}",
            r"\begin{minipage}[c]{0.29\linewidth}\centering",
            diagram(h["shape"], h["hazard"]),
            r"\end{minipage}\hfill",
            r"\begin{minipage}[c]{0.67\linewidth}\raggedright",
            r"{\num\fontsize{13}{14}\selectfont\color{gold} " + str(h["no"]) + r"}\ " + meta + r"\\[1.5pt]",
            r"{\fontsize{8.6}{10}\selectfont\color{gdeep} " + h["title"] + r"}\\[1.5pt]",
            r"{\fontsize{6.8}{9}\selectfont\color{ink} " + h["desc"] + "}",
            # \par is required: without it the following \vspace is
            # swallowed and consecutive entries collide.
            r"\end{minipage}\end{minipage}\par",
            r"\vspace{6pt}",
        ]
    return "\n".join(p)
