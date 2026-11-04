# Changelog

- 2026-11-01: repository assembled from road-to-robotics and paper-vs-hardware (WS-093); see BUILD.md and PROVENANCE.md.
- 2026-11-01: created private on GitHub (ravediamond/paper-reward-models-stopping-rule); from now on the source of truth, road-to-robotics keeps memos, reviews and WS history.

## 2026-11-04 — WS-133 Part 1 (peer-review pass, chat)
Robometer within policy un-pended: pair-weighted 0.821 over the per-policy block (new l0 check), per-policy range in
place of a bootstrap CI (per-episode scores not stored); last-progress head reported (0.838 pooled, descriptive);
Displayport one-class task stated; refs.bib + natbib with inline citations (18 entries); codenames moved to an
appendix analysis map; abstract cut to four numbers; Tables 1–2 added; Related work added; every judge gets the same
AUROC + caught/flagged triple with in-sample thresholds marked; md2tex.py generalised (tables, figures, citations).
No verdict changed; the only revised value is rbm_within, from the unweighted 0.819 to the pair-weighted 0.821.
PDF not rebuilt in the chat container; run `make check` on the Orin.
