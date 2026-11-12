#!/usr/bin/env python3
"""DRAFT_4p.src.md -> main.src.tex (same text, placeholders kept); run before make_paper.py when the markdown changes.
Generic: headings, paragraphs, pipe tables (booktabs; a preceding "Table N: ..." line is the caption), figures from
image lines (the .pdf twin of the .png), [@key] / [@k1; @k2] -> \\citep; the References section becomes
\\bibliography{refs}; an "## Appendix: ..." section lands after the bibliography."""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
md = (HERE / "DRAFT_4p.src.md").read_text()

SUB = [("$", r"\$"), ("&", r"\&"), ("%", r"\%"), ("#", r"\#"), ("_", r"\_"), ("≥", r"$\geq$"), ("≤", r"$\leq$"),
       ("×", r"$\times$"), ("°", r"$^\circ$"), ("τ", r"$\tau$"), ("—", "---"), ("–", "--"), ("±", r"$\pm$")]


def esc(x):
    for a, b in SUB:
        x = x.replace(a, b)
    x = re.sub(r"\[@([^\]]+)\]", lambda m: r"\citep{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}", x)
    x = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", x, flags=re.S)
    x = re.sub(r"(?<!\*)\*([^*\n]+)\*", r"\\emph{\1}", x)
    x = re.sub(r"`(.+?)`", r"\\texttt{\1}", x)
    return re.sub(r"\{\{([^}]*)\}\}", lambda m: "{{" + m.group(1).replace(r"\_", "_") + "}}", x)


RP = r">{\raggedright\arraybackslash}p"  # ragged cells: long file names must not overflow the column
COLSPEC = {3: ("table", r"p{3.0cm}p{2.4cm}p{2.6cm}"),
           7: ("table*", r"p{2.8cm}p{2.2cm}p{1.0cm}p{3.1cm}p{1.1cm}p{1.2cm}p{2.3cm}"),
           4: ("table", RP + "{2.3cm}" + RP + "{1.5cm}" + RP + "{2.0cm}" + RP + "{2.1cm}")}


def brk(c):
    """Let file names and paths break inside a table cell (not in placeholders, which are filled later)."""
    return c if "{{" in c else c.replace(r"\_", r"\_\allowbreak{}").replace("/", "/\\allowbreak{}")


def table(rows, caption, wide_pos="t"):
    env, spec = COLSPEC[len(rows[0])]
    out = ["\\begin{%s}[%s]\\centering\\scriptsize" % (env, wide_pos),
           "\\setlength{\\tabcolsep}{3pt}\\renewcommand{\\arraystretch}{1.1}",
           "\\begin{tabular}{" + spec + "}", "\\toprule",
           "\\shissohead " + " & ".join(rows[0]) + r" \\", "\\midrule"]
    out += [" & ".join(brk(c) for c in r) + r" \\" for r in rows[1:]]
    out += ["\\bottomrule", "\\end{tabular}"]
    if caption:
        out.append("\\caption{" + caption + "}")
    out.append("\\end{%s}" % env)
    return "\n".join(out) + "\n\n"


def convert(block_lines):
    out, cap, i = "", "", 0
    while i < len(block_lines):
        l = block_lines[i]
        if l.startswith("```"):  # fenced code from the repository: printed verbatim
            j = i + 1
            while j < len(block_lines) and not block_lines[j].startswith("```"):
                j += 1
            out += "\\begin{lstlisting}\n" + "\n".join(block_lines[i + 1:j]) + "\n\\end{lstlisting}\n"
            i = j + 1
            continue
        if l.startswith("> "):  # a "> **Name.** ..." block is a finding box of the design layer
            j = i
            while j < len(block_lines) and block_lines[j].startswith(">"):
                j += 1
            q = " ".join(x[1:].strip() for x in block_lines[i:j])
            m = re.match(r"\*\*(.+?)\*\*\s*(.*)", q, flags=re.S)
            out += "\\begin{shissofinding}[%s]\n%s\n\\end{shissofinding}\n" % (esc(m.group(1)), esc(m.group(2)))
            i = j
            continue
        if re.match(r"Table \d+: ", l):
            cap = esc(l.split(": ", 1)[1])
        elif l.startswith("|"):
            rows = []
            while i < len(block_lines) and block_lines[i].startswith("|"):
                if not set(block_lines[i]) <= set("|-: "):
                    rows.append([esc(c.strip()) for c in block_lines[i].strip("|").split("|")])
                i += 1
            out += table(rows, cap); cap = ""
            continue
        elif (m := re.match(r"!\[Fig\. 1 — (.*?)\. (.*)\]\((.*)\)", l)):
            out += ("\\begin{figure*}[t]\\centering\\includegraphics[width=\\textwidth]{%s}\\caption{\\textbf{%s.} %s}\\end{figure*}\n\n"
                    % (m.group(3).replace(".png", ".pdf"), esc(m.group(1)[0].upper() + m.group(1)[1:]), esc(m.group(2))))
        elif m := re.match(r"!\[(.*)\]\((.*)\)", l):
            out += ("\\begin{figure}[t]\\centering\\includegraphics[width=\\columnwidth]{%s}\\caption{%s}\\end{figure}\n\n"
                    % (m.group(2).replace(".png", ".pdf"), esc(m.group(1))))
        else:
            out += esc(l) + "\n"
        i += 1
    return out


secs = re.split(r"^## ", md, flags=re.M)
abstract, body, appendix = "", "", ""
for s in secs[1:]:
    title, _, rest = s.partition("\n")
    lines = rest.strip("\n").split("\n")
    if title == "Abstract":
        abstract = convert(lines)
    elif title.startswith("References"):
        continue
    elif title.startswith("Appendix"):
        appendix = "\\appendix\n\\section*{" + esc(title) + "}\n" + convert(lines)
    else:
        name = title.split(" ", 1)[1] if title.split(" ", 1)[0].isdigit() else title
        body += "\\section{" + esc(name) + "}\n" + convert(lines) + "\n"

TPL = r"""\documentclass[10pt,twocolumn]{article}
% Rendered by make_paper.py from main.src.tex (do not edit main.tex; main.src.tex comes from md2tex.py).
\usepackage[margin=0.75in]{geometry}
\usepackage{graphicx,amssymb,hyperref,booktabs}
\usepackage[numbers]{natbib}
\usepackage{listings}\lstset{basicstyle=\ttfamily\scriptsize,breaklines=true,columns=fullflexible,keepspaces=true,frame=tb,framerule=0.3pt,aboveskip=4pt,belowskip=4pt,upquote=true}
\usepackage{style/shisso}
\shissorepo{github.com/ravediamond/paper-reward-models-stopping-rule}
\title{What a reward model can show depends on who stopped the episode: failure judges and monitors on a low-cost arm}
\date{}
\begin{document}
\twocolumn[\vspace*{0.32in}\shissopanel{What a reward model can show depends on who stopped the episode: failure judges and monitors on a low-cost arm}{Ravindu Somawansa\\[1pt]Shisso Robotics, Paris\\[1pt]\texttt{ravindu.somawansa@shissorobotics.com}}{ABSTRACT}{\textbf{Code and rows:} \texttt{github.com/ravediamond/paper-reward-models-stopping-rule}\quad\textbf{Reproduce:} \texttt{make check}}\vspace{4pt}]
BODY
\bibliographystyle{plainnat}
\bibliography{refs}

APPENDIX
\end{document}
"""
(HERE / "main.src.tex").write_text(TPL.replace("ABSTRACT", abstract.strip())
                                   .replace("BODY", body.strip()).replace("APPENDIX", appendix.strip()) + "")
print("main.src.tex written")
