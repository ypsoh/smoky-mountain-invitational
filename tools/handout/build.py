#!/usr/bin/env python3
"""
Build the keepsake handouts: one personalised 5.5 x 8.5in card per
player, double-sided, plus a combined file for printing.

    python3 tools/handout/build.py

Everything on the card comes from assets/js/data.js, so a handicap or
tee changed for the website changes here too. There is no second copy
of the trip data.

Needs: tectonic (brew install tectonic), node, and a network
connection the first time (to fetch fonts and TeX packages).
"""
import json, pathlib, subprocess, sys, shutil, os

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import holes as HOLES

HERE  = pathlib.Path(__file__).resolve().parent
ROOT  = HERE.parent.parent
FONTS = HERE / "fonts"
BUILD = HERE / "build"
OUT   = ROOT / "handouts"
VENV  = HERE / ".venv"


def sh(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


# ---------------------------------------------------------------
# 1. Trip data, evaluated straight out of data.js
# ---------------------------------------------------------------
def load_data():
    js = (ROOT / "assets/js/data.js").read_text()
    prog = (js + "\nconsole.log(JSON.stringify({PLAYERS,COURSES,TEAMS,MULLIGANS}));")
    r = subprocess.run(["node", "-e", prog], capture_output=True, text=True)
    if r.returncode:
        sys.exit("could not evaluate data.js:\n" + r.stderr)
    return json.loads(r.stdout)


# ---------------------------------------------------------------
# 2. Fonts
# ---------------------------------------------------------------
def ensure_fonts():
    need = ["CormorantGaramond-Regular.ttf", "CormorantGaramond-SemiBold.ttf",
            "CormorantGaramond-Italic.ttf", "SourceSerif4-Regular.ttf",
            "SourceSerif4-SemiBold.ttf", "Marcellus-Regular.ttf",
            "BarlowCondensed-Regular.ttf", "BarlowCondensed-SemiBold.ttf",
            "NanumMyeongjo-Regular.ttf", "NanumMyeongjo-Bold.ttf"]
    if all((FONTS / n).exists() for n in need):
        print("  fonts already prepared")
        return
    print("  preparing fonts (first run only)")
    py = VENV / "bin" / "python"
    if not py.exists():
        print("    bootstrapping venv for fontTools")
        sh([sys.executable, "-m", "venv", str(VENV)])
        sh([str(VENV / "bin" / "pip"), "install", "--quiet", "fonttools", "brotli"])
    sh([str(py), str(HERE / "fonts.py")])


# ---------------------------------------------------------------
# 3. LaTeX fragments
# ---------------------------------------------------------------
def tex_escape(s):
    for a, b in [("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_")]:
        s = s.replace(a, b)
    return s


def field_block(data, me):
    """All six names, grouped by team, with the cardholder marked."""
    rows = []
    for tid in ("laurel", "balsam"):
        mates = [p for p in data["PLAYERS"] if p["team"] == tid]
        t = data["TEAMS"][tid]
        cell = [r"\begin{minipage}[t]{0.47\linewidth}",
                r"\raggedright",
                r"{\capstight\fontsize{6.6}{8}\selectfont\color{gold} %s}\\[4pt]"
                % tex_escape(t["name"].upper())]
        for p in mates:
            mark = r"\,\marker" if p["id"] == me["id"] else ""
            cell.append(
                r"{\fontsize{9}{13}\selectfont\color{gdeep} %s}%s\ "
                r"{\num\fontsize{8}{13}\selectfont\color{gfair} %d}\\[1.5pt]"
                % (tex_escape(p["nameKo"]), mark, p["hi"]))
        cell.append(r"\end{minipage}")
        rows.append("\n".join(cell))
    return "\\begin{center}\n" + "\\hfill\n".join(rows) + "\n\\end{center}"


def scorecard(course, tee, label_en):
    """
    Two nine-hole blocks. Rows are 홀 / PAR / 스코어 only.

    No stroke-index row: it is still unverified, and printing a guess
    onto something that gets laminated bakes the error in for good.
    No per-hole yardage either -- only per-tee totals are published --
    so the total sits in the header instead.
    """
    par = course["parByHole"]
    out_, in_ = sum(par[:9]), sum(par[9:])

    def block(holes, pars, tot_label, tot_val, second):
        hdr = " & ".join(r"{\capstight\fontsize{6}{7}\selectfont\color{gold}%s}" % h for h in holes)
        prs = " & ".join(r"{\numlight\fontsize{7.6}{9}\selectfont\color{gfair}%d}" % p for p in pars)
        extra_h = (r"{\capstight\fontsize{6}{7}\selectfont\color{gold}TOT}" if second else "")
        extra_p = (r"{\num\fontsize{7.6}{9}\selectfont\color{gfair}%d}" % course["par"]) if second else ""
        return "\n".join([
            r"\begin{tabular}{@{}L|" + "H" * 9 + "|T|T@{}}",
            r"{\capstight\fontsize{6}{7}\selectfont\color{gfair}HOLE} & " + hdr
              + r" & {\capstight\fontsize{6}{7}\selectfont\color{gold}%s} & %s \\" % (tot_label, extra_h),
            r"\arrayrulecolor{ivory}\hline",
            r"{\capstight\fontsize{6}{7}\selectfont\color{gfair}PAR} & " + prs
              + r" & {\num\fontsize{7.6}{9}\selectfont\color{gfair}%d} & %s \\" % (tot_val, extra_p),
            r"\arrayrulecolor{ivory}\hline",
            # label + nine blank score cells + two blank totals = 12 columns,
            # matching L | HHHHHHHHH | T | T exactly.
            " & ".join([r"{\capstight\fontsize{6}{7}\selectfont\color{gfair}스코어}\tallrow"]
                       + [""] * 11) + r" \\",
            r"\arrayrulecolor{ivory}\hline",
            r"\end{tabular}",
        ])

    head = "\n".join([
        # Explicit leading space: \topsep is zeroed globally (see the
        # template) so centre environments no longer space themselves.
        r"\vspace{7pt}",
        r"\begin{center}",
        r"{\disp\fontsize{14}{16}\selectfont\color{gdeep} %s}\\[2pt]" % tex_escape(label_en),
        r"{\capstight\fontsize{6.4}{8}\selectfont\color{gfair} PAR %d}\ "
        r"{\num\fontsize{8}{9}\selectfont\color{gdeep} %s \textperiodcentered\ %s}"
        % (course["par"], tee["name"].upper(), f"{tee['yards']:,}"),
        r"\end{center}",
        r"\vspace{3pt}",
    ])
    body = "\n\\vspace{2pt}\n".join([
        block([str(i) for i in range(1, 10)],  par[:9],  "OUT", out_, False),
        block([str(i) for i in range(10, 19)], par[9:], "IN",  in_,  True),
    ])
    return head + "\n\\begin{center}\n" + body + "\n\\end{center}"



IMPOSE_TEX = r"""\documentclass{article}
\usepackage[paperwidth=11in,paperheight=8.5in,margin=0pt]{geometry}
\usepackage{pdfpages}
\pagestyle{empty}
\begin{document}
%% Outside of the folded sheet: back cover on the left, front cover on
%% the right. Fold down the middle and the front cover faces out.
\includepdf[pages={4,1},nup=2x1,noautoscale=true]{__SRC__}
%% Inside spread, in reading order.
\includepdf[pages={2,3},nup=2x1,noautoscale=true]{__SRC__}
\end{document}
"""


def impose(stem):
    """
    Lay the four panels onto two Letter sheets for printing.

    Print double-sided, FLIP ON THE SHORT EDGE, then fold once down the
    middle. Short edge matters: these pages are landscape, and a
    long-edge flip puts the inside spread upside down.
    """
    src = (BUILD / f"{stem}.pdf").resolve()
    tex = BUILD / f"{stem}-print.tex"
    tex.write_text(IMPOSE_TEX.replace("__SRC__", str(src)))
    r = subprocess.run(["tectonic", "-X", "compile", "--outdir", str(BUILD), str(tex)],
                       capture_output=True, text=True)
    if r.returncode:
        return None
    out = OUT / f"{stem}-print.pdf"
    shutil.copy(BUILD / f"{stem}-print.pdf", out)
    return out


# ---------------------------------------------------------------
# 4. Render + compile
# ---------------------------------------------------------------
def main():
    if not shutil.which("tectonic"):
        sys.exit("tectonic not found. Install with: brew install tectonic")
    if not shutil.which("node"):
        sys.exit("node not found; it is used to read assets/js/data.js")

    print("The Smoky Mountain Invitational — handouts")
    ensure_fonts()

    data = load_data()
    tpl  = (HERE / "template.tex").read_text()
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)

    mv, sq = data["COURSES"]["maggie"], data["COURSES"]["sequoyah"]
    made = []

    print("  compiling")
    for p in data["PLAYERS"]:
        mvt = mv["tees"][p["tees"]["maggie"]]
        sqt = sq["tees"][p["tees"]["sequoyah"]]
        doc = tpl
        for token, value in {
            "__FONTS__":       str(FONTS) + "/",
            "__NAME_KO__":     tex_escape(p["nameKo"]),
            "__NAME_EN__":     tex_escape(p["name"]),
            "__TEAM_EN__":     tex_escape(data["TEAMS"][p["team"]]["name"].upper()),
            "__HCP__":         str(p["hi"]),
            "__MV_TEE__":      mvt["name"].upper(),
            "__MV_YDS__":      f"{mvt['yards']:,}",
            "__SQ_TEE__":      sqt["name"].upper(),
            "__SQ_YDS__":      f"{sqt['yards']:,}",
            "__FIELD__":       field_block(data, p),
            "__COURSE_MV__":   HOLES.course_panel(mv, mvt, p["tees"]["maggie"],
                                   "Maggie Valley Club",
                                   "전반은 계곡의 평지, 후반 9홀은 800피트를 오르내립니다.", "maggie"),
            "__COURSE_SQ__":   HOLES.course_panel(sq, sqt, p["tees"]["sequoyah"],
                                   "Sequoyah National",
                                   "파5 다섯, 파3 다섯. 길어서가 아니라 까다로워서 어려운 코스.", "sequoyah",
                                   yard_totals=False,
                                   note="홀별 야드는 자료마다 조금씩 다릅니다. 총 거리는 클럽 공식 수치입니다."),
            "__CARD_MV__":     scorecard(mv, mvt, "Maggie Valley Club"),
            "__CARD_SQ__":     scorecard(sq, sqt, "Sequoyah National"),
            "__MULLI_PRICE__": str(data["MULLIGANS"]["extraPrice"]),
        }.items():
            doc = doc.replace(token, value)

        stem = f"smi-2026-{p['id']}"
        src = BUILD / f"{stem}.tex"
        src.write_text(doc)
        r = subprocess.run(["tectonic", "-X", "compile", "--outdir", str(BUILD), str(src)],
                           capture_output=True, text=True)
        if r.returncode:
            tail = "\n".join(r.stderr.strip().splitlines()[-25:])
            sys.exit(f"\n{stem} failed to compile:\n{tail}")
        shutil.copy(BUILD / f"{stem}.pdf", OUT / f"{stem}.pdf")
        made.append(OUT / f"{stem}.pdf")
        printed = impose(stem)
        note = "  + print sheet" if printed else "  (imposition failed)"
        print(f"    {p['name']:<10} {p['nameKo']:<8} -> handouts/{stem}.pdf{note}")

    # One file with all twelve sides, for a single print run.
    if shutil.which("gs"):
        combined = OUT / "smi-2026-all.pdf"
        sh(["gs", "-dBATCH", "-dNOPAUSE", "-q", "-sDEVICE=pdfwrite",
            f"-sOutputFile={combined}", *[str(m) for m in made]])
        print(f"    combined -> handouts/{combined.name}")

    print(f"  done: {len(made)} cards in handouts/")


if __name__ == "__main__":
    main()
