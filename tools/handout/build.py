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
import routemap as ROUTEMAP

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
    prog = (js + "\nconsole.log(JSON.stringify({PLAYERS,COURSES,TEAMS,MULLIGANS,ROUTE,TRIP}));")
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


def scorecard(course, tee, tee_key, label_en, yard_totals=True):
    """
    The personal card: hole, par, yardage, stroke index, and a row to
    write your own score in.

    Stroke index is printed now that both courses' real allocations are
    known -- it is what tells you which holes you get a shot on.
    """
    par = course["parByHole"]
    yds = course.get("yardsByHole", {}).get(tee_key)
    si  = course["strokeIndex"]

    def thin(label, vals, tot, accent=False):
        col = "gdeep" if accent else "gfair"
        cells = " & ".join(
            r"{\numlight\fontsize{5.8}{7.4}\selectfont\color{%s}%s}" % (col, v) for v in vals)
        return (r"{\capstight\fontsize{5}{6.6}\selectfont\color{gfair}%s} & " % label
                + cells + r" & {\num\fontsize{5.8}{7.4}\selectfont\color{gold}%s} \\" % tot
                + "\n" + r"\hline")

    def block(lo, hi, tot_label, second):
        sl = slice(lo, hi)
        hdr = " & ".join(r"{\capstight\fontsize{5}{6.6}\selectfont\color{gold}%d}" % h
                         for h in range(lo + 1, hi + 1))
        extra_h = (r"{\capstight\fontsize{5}{6.6}\selectfont\color{gold}TOT}" if second else "")
        rows = [r"{\capstight\fontsize{5}{6.6}\selectfont\color{gfair}HOLE} & " + hdr
                + r" & {\capstight\fontsize{5}{6.6}\selectfont\color{gold}%s} & %s \\" % (tot_label, extra_h),
                r"\hline",
                thin("PAR", par[sl], sum(par[sl]), accent=True)]
        if yds:
            rows.append(thin("YDS", yds[sl], format(sum(yds[sl]), ",") if yard_totals else "—"))
        rows.append(thin("HDCP", si[sl], "—"))
        rows.append(" & ".join(
            [r"{\capstight\fontsize{5}{6.6}\selectfont\color{gfair}스코어}\tallrow"] + [""] * 11)
            + r" \\")
        rows.append(r"\hline")
        return rows

    head = "\n".join([
        r"\vspace{3pt}",
        r"\begin{center}",
        r"{\disp\fontsize{12}{14}\selectfont\color{gdeep} %s}\\[2pt]" % tex_escape(label_en),
        r"{\capstight\fontsize{5.8}{7.4}\selectfont\color{gfair} PAR %d}\ "
        r"{\num\fontsize{7.6}{9}\selectfont\color{gdeep} %s \textperiodcentered\ %s}"
        % (course["par"], tee["name"].upper(), f"{tee['yards']:,}"),
        r"\end{center}",
        r"\vspace{3pt}",
    ])
    # One tabular spanning both nines, for the same reason as the team
    # card: two stacked tables have no guaranteed column alignment.
    body = "\n".join(
        [r"\begin{tabular}{@{}L|" + "H" * 9 + r"|T|T@{}}"]
        + block(0, 9, "OUT", False) + block(9, 18, "IN", True)
        + [r"\end{tabular}"])
    return head + "\n\\begin{center}\n" + body + "\n\\end{center}"


IMPOSE_TEX = r"""\documentclass{article}
\usepackage[paperwidth=11in,paperheight=8.5in,margin=0pt]{geometry}
\usepackage{pdfpages}
\pagestyle{empty}
\begin{document}
%% Outside of the folded sheet: back cover left, front cover right.
\includepdf[pages={4,1},nup=2x1,noautoscale=true]{__SRC__}
%% Inside spread, in reading order.
\includepdf[pages={2,3},nup=2x1,noautoscale=true]{__SRC__}
\end{document}
"""


def page_count(pdf):
    """
    Pages via Ghostscript. Scanning raw bytes for /Type /Page does not
    work: Tectonic writes compressed object streams. Returns None if gs
    is absent, in which case the caller skips the check.
    """
    if not shutil.which("gs"):
        return None
    r = subprocess.run(
        ["gs", "-q", "-dNODISPLAY", "-dNOSAFER", "-c",
         f"({pdf}) (r) file runpdfbegin pdfpagecount = quit"],
        capture_output=True, text=True)
    try:
        return int(r.stdout.strip())
    except ValueError:
        return None


def impose(stem):
    """
    Lay the four panels onto two Letter sheets.

    Print double-sided, FLIP ON THE SHORT EDGE, then fold once. Short
    edge matters: these sheets are landscape, and a long-edge flip puts
    the inside spread upside down.
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
    by_team = {t: [q for q in data["PLAYERS"] if q["team"] == t]
               for t in data["TEAMS"]}
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
            "__FIELD__":       HOLES.field_block(data["PLAYERS"], data["TEAMS"], p["id"]),
            "__ROUTEMAP__":    ROUTEMAP.tikz(data["ROUTE"]),
            "__COURSE_MV__":   HOLES.course_panel(mv, mvt, p["tees"]["maggie"],
                                   "Maggie Valley Club",
                                   "전반은 계곡의 평지, 후반 9홀은 800피트를 오르내립니다.", "maggie",
                                   teammates=by_team[p["team"]],
                                   team_name=data["TEAMS"][p["team"]]["name"]),
            "__COURSE_SQ__":   HOLES.course_panel(sq, sqt, p["tees"]["sequoyah"],
                                   "Sequoyah National",
                                   "파5 다섯, 파3 다섯. 길어서가 아니라 까다로워서 어려운 코스.", "sequoyah",
                                   teammates=by_team[p["team"]],
                                   team_name=data["TEAMS"][p["team"]]["name"]),
            "__CARD_MV__":     scorecard(mv, mvt, p["tees"]["maggie"], "Maggie Valley Club"),
            "__CARD_SQ__":     scorecard(sq, sqt, p["tees"]["sequoyah"], "Sequoyah National",
                                   yard_totals=False),
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
        # The booklet folds from ONE sheet, so four panels is not a
        # preference -- a fifth page means it cannot be folded at all.
        # Panel 4 sits close to full, so this has regressed before.
        n = page_count(BUILD / f"{stem}.pdf")
        if n is not None and n != 4:
            sys.exit(f"\n{stem}: produced {n} pages, expected exactly 4.\n"
                     f"Something on a panel grew past its page. Trim it in "
                     f"template.tex or holes.py and rebuild.")
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
