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
                  "그린은 양옆이 벙커입니다."),
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
                  "그린은 앞에서 뒤로 기울어 붙이기 어렵습니다."),
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


def diagram(shape, hazard, scale=0.82):
    """A 26 x 15 mm schematic at scale 1: tee left, green right."""
    d = [r"\begin{tikzpicture}[x=%gmm,y=%gmm,line cap=round,line join=round]"
         % (scale, scale)]
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


def team_log(course, teammates):
    """
    The team's card for one round: a row per player plus a total.

    ONE tabular holding both nines, not two stacked tables. Separate
    tables are laid out independently, so their columns are only ever
    coincidentally aligned and a gap between them reads as a misprint.
    A single tabular makes alignment structural.
    """
    def header(lo, hi, tot_label):
        hdr = " & ".join(
            r"{\capstight\fontsize{5}{6.5}\selectfont\color{gold}" + str(h) + "}"
            for h in range(lo + 1, hi + 1))
        return (r"{\capstight\fontsize{5}{6.5}\selectfont\color{gfair}HOLE} & " + hdr
                + r" & {\capstight\fontsize{5}{6.5}\selectfont\color{gold}" + tot_label + r"} \\")

    def entries():
        rows = []
        for n in ("1", "2", "3"):
            rows.append(
                " & ".join([r"{\num\fontsize{6}{7.6}\selectfont\color{gfair}" + n + r"}\logrow"]
                           + [""] * 10) + r" \\")
            rows.append(r"\hline")
        rows.append(
            " & ".join([r"{\capstight\fontsize{5}{6.5}\selectfont\color{gold}TEAM}\logrow"]
                       + [""] * 10) + r" \\")
        rows.append(r"\hline")
        return rows

    out = [r"\begin{center}", r"\begin{tabular}{@{}K|" + "R" * 9 + r"|U@{}}",
           header(0, 9, "OUT"), r"\hline"]
    out += entries()
    out += [header(9, 18, "IN"), r"\hline"]
    out += entries()
    out += [r"\end{tabular}", r"\end{center}"]
    return "\n".join(out)


def course_panel(course, tee, tee_key, title_en, sub_ko, key,
                 teammates=None, team_name=""):
    """One inside panel: the holes worth knowing, then the team's card."""
    p = [r"\vspace{2pt}",
         r"\begin{center}",
         r"{\disp\fontsize{18}{20}\selectfont\color{gdeep} " + _esc(title_en) + r"}\\[3pt]",
         r"{\capstight\fontsize{6}{8}\selectfont\color{gfair} PAR " + str(course["par"]) + r"}\ "
         r"{\num\fontsize{8.2}{10}\selectfont\color{gdeep} " + tee["name"].upper()
         + r" \textperiodcentered\ " + format(tee["yards"], ",") + r"}\\[3pt]",
         r"{\fontsize{6.4}{8.4}\selectfont\color{gfair} " + sub_ko + "}",
         r"\end{center}",
         r"\vspace{3pt}",
         r"\begin{center}\eyebrow{HOLES WORTH KNOWING \textperiodcentered\ 눈여겨볼 홀}\end{center}",
         r"\vspace{3pt}"]

    for h in NOTABLE[key]:
        meta = (r"{\capstight\fontsize{5.4}{7}\selectfont\color{gfair} PAR "
                + str(h["par"]) + r" \textperiodcentered\ " + str(h["yds"])
                + r" YDS \textperiodcentered\ HDCP " + str(h["si"]) + "}")
        p += [
            r"\noindent\begin{minipage}{\linewidth}",
            r"\begin{minipage}[c]{0.27\linewidth}\centering",
            diagram(h["shape"], h["hazard"]),
            r"\end{minipage}\hfill",
            r"\begin{minipage}[c]{0.69\linewidth}\raggedright",
            r"{\num\fontsize{12}{13}\selectfont\color{gold} " + str(h["no"]) + r"}\ " + meta + r"\\[1pt]",
            r"{\fontsize{7.8}{9.2}\selectfont\color{gdeep} " + h["title"] + r"}\\[1pt]",
            r"{\fontsize{6.2}{7.9}\selectfont\color{ink} " + h["desc"] + "}",
            r"\end{minipage}\end{minipage}\par",
            r"\vspace{1pt}",
        ]

    p += [r"\hairrule", r"\vspace{2pt}",
          r"\begin{center}\goldbrow{TEAM CARD \textperiodcentered\ " + _esc(team_name) + r"}\end{center}",
          r"\begin{center}{\fontsize{5.4}{7}\selectfont\color{gfair} "
          r"세 명의 스코어를 적고 팀 합계를 내세요}\end{center}",
          r"\vspace{2pt}",
          team_log(course, teammates or []),
          r"\vspace{2pt}",
          r"\begin{center}",
          r"\begin{tikzpicture}[x=1mm,y=1mm]",
          r"\node[anchor=east] at (-2.5,0) {{\capstight\fontsize{5}{6.5}\selectfont"
          r"\color{gold}MULLIGANS}};",
          r"\foreach \i in {0,1,2,3,4,5} { \draw[gold,line width=0.5pt] (\i*7.6,0) circle (2.1); }",
          r"\end{tikzpicture}",
          r"\end{center}"]
    return "\n".join(p)


def field_block(players, teams, me_id):
    """
    All six, two columns, grouped by team. The cardholder is marked.

    Plain names, no portraits: the cover already carries the route map
    as its visual, and a second graphic element crowded it.
    """
    cols = []
    for tid, accent in (("laurel", "gold"), ("balsam", "azalea")):
        mates = [p for p in players if p["team"] == tid]
        cell = [r"\begin{minipage}[t]{0.47\linewidth}",
                r"\centering",
                r"{\capstight\fontsize{6}{8}\selectfont\color{" + accent + "} "
                + _esc(teams[tid]["name"].upper()) + r"}\\[4pt]"]
        for p in mates:
            mark = r"\,\marker" if p["id"] == me_id else ""
            cell.append(
                r"{\fontsize{8.8}{12.5}\selectfont\color{gdeep} " + _esc(p["nameKo"]) + "}"
                + mark + r"\ {\num\fontsize{7.8}{12.5}\selectfont\color{gfair} "
                + str(p["hi"]) + r"}\\[1pt]")
        cell.append(r"\end{minipage}")
        cols.append("\n".join(cell))
    return r"\begin{center}" + "\n" + ("\n" + r"\hfill" + "\n").join(cols) + "\n" + r"\end{center}"
