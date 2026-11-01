#!/usr/bin/env python3
"""DRAFT_4p.src.md -> main.src.tex (same text, placeholders kept); run before make_paper.py when the markdown changes."""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
md = (HERE / "DRAFT_4p.src.md").read_text()


def sec(title):
    return re.search(r"## " + re.escape(title) + r"\n\n(.*?)(?=\n## |\Z)", md, re.S).group(1).strip()


def tex(x):
    x = re.sub(r"!\[.*?\]\(.*?\)\n?", "", x)
    x = x.replace("%", "\\%").replace("&", "\\&").replace("#", "\\#").replace("_", "\\_")
    x = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", x, flags=re.S); x = re.sub(r"\*(.+?)\*", r"\\emph{\1}", x)
    x = re.sub(r"`(.+?)`", r"\\texttt{\1}", x)
    for a, b in (("≥", "$\\geq$"), ("≤", "$\\leq$"), ("×", "$\\times$"), ("°", "$^\\circ$"), ("–", "--"), ("—", "---"), ("τ", "$\\tau$")):
        x = x.replace(a, b)
    return re.sub(r"\{\{([^}]*)\}\}", lambda m: "{{" + m.group(1).replace("\\_", "_") + "}}", x)


FIGS = {"3 The length baseline": ("armnetbench", "Failure AUROC on ArmnetBench (95 \\% CIs): episode length vs two zero-shot reward models (Robometer-4B, TOPReward with Qwen3-VL-8B)."),
        "4 Is it the timeout?": ("truncation", "Length observed up to a fraction of the task's longest episode, AUROC within policy (band: 95 \\% CI)."),
        "5 Judges and monitors on our rollouts": ("own_monitors", "Fifty own rollouts: failures caught (of 8) vs successes flagged (of 42). Circles: mid-episode monitors; shaded: their bar ($\\geq$ 5/8 at $\\leq$ 1/20). Squares: judges at rest (one score per finished episode) at their in-sample G-flora operating point; the monitor bar does not apply to them.")}
body = ""
for t in ("1 Introduction", "2 Data and labels", "3 The length baseline", "4 Is it the timeout?", "5 Judges and monitors on our rollouts", "6 Limitations"):
    body += "\\section{" + t.split(" ", 1)[1] + "}\n" + tex(sec(t)) + "\n\n"
    if t in FIGS:
        body += "\\begin{figure}[t]\\centering\\includegraphics[width=\\columnwidth]{fig/%s.pdf}\\caption{%s}\\end{figure}\n\n" % FIGS[t]
TPL = r"""\documentclass[10pt,twocolumn]{article}
% WS-077: rendered by make_paper.py from main.src.tex (do not edit main.tex; main.src.tex comes from md2tex.py).
\usepackage[margin=0.75in]{geometry}
\usepackage{graphicx,amssymb,hyperref}
\title{What a reward model can show depends on who stopped the episode: failure judges and monitors on a low-cost arm}
\author{Ravindu Somawansa\\Shisso Robotics}
\date{}
\begin{document}
\maketitle
\begin{abstract}
ABSTRACT
\end{abstract}
BODY
\section*{References}
REFS
\end{document}
"""
(HERE / "main.src.tex").write_text(TPL.replace("ABSTRACT", tex(sec("Abstract"))).replace("BODY", body)
                                   .replace("REFS", tex(sec("References (ids from the papers mirror)"))))
print("main.src.tex written")
