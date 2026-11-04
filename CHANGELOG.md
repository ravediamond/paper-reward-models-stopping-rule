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

## 2026-11-04 — WS-133 Part 1, build and fixes on the Orin
`make check` run (L0 green, numbers.json regenerated without change, PDF rebuilt, 4 pages). Fixed what the first build showed: five bibliography entries said "authors to fill" (authors now from the papers mirror, long lists cut to six and "others"); the model-card entries now carry the vendor URL, licence and access date 2026-11-04 (Flora-Rewarder released 2026-10-15; the Qwen3.5-27B and 9B cards, Qwen3-VL-8B-Instruct, and the Gemini 3.8 Flash model page); the appendix table no longer overflows its column; the title footnote no longer says that every bar commit is in this repository (the bar commits 1a69f30, 9d1764d, 6241570, 37497f0, 75f81bf, c0f1b0d are in the research repository ravediamond/road-to-robotics, not in this one's history; the protocols are copied here verbatim).
The review prompt's 0.875 for Robometer's last-progress score is the `partial` run (1,637 episodes scored); the `complete` run gives 0.838, which the paper uses.
