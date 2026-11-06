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

- 2026-11-04: prose rewritten against road-to-robotics `journal/papers/ai-map/WRITING_RULES.md` (no verdict or existing number changed). main.pdf rebuilt with xelatex in the chat container; run `make check` on the Orin for the tectonic build. main.src.tex regenerated with md2tex.py.
- 2026-11-05: prose updated to WRITING_RULES.md groups H and I (rules 41-70: ranked limitations, the author named as labeller, opening from the belief tested, abstract at most four numbers, shorter captions, running example, practical close) and road-to-robotics MY_STYLE.md. No verdict or existing number changed. main.pdf rebuilt with xelatex in the chat container; run make check on the Orin for the tectonic build. Robometer CI paragraph moved to Limitations; added a Conclusion; rbm_rescore placeholder (LENGTH_RESULTS.md); md2tex.py now escapes $.
- 2026-11-05: rules 13, 23, 42, 65 (owner changes) and 71-74 (triads, tone) applied. Only the question heading of §4 replaced (rule 65).
- 2026-11-05: rules 13 (varied sentence length), 23 (varied wording), 71 (no tidy triads) and 72-74 (limitations in the method's voice, failures framed by condition, strengths and cost first) applied. No number changed.
- 2026-11-05: rule 78 (de-polish) applied to all prose: dense sentences split, semicolons and colon set-ups removed, advice and closers removed except one practical sentence in the conclusion, contrast kept only where a result contradicts a paper, plain description with the citation in the sentence. No number changed.
- 2026-11-05: merge pass (rule 78g) reverted. The 15:01 EditLens run scored it higher than the split version in all four papers (colon and 'X, with Y' set-ups pushed up; sentence length had no effect). Back to the 14:12 text.
- 2026-11-05: the paragraph with the highest EditLens score rewritten by the author (grammar fixes only, numbers back as placeholders).
- 2026-11-05: the pair-weighted within-policy AUROC (stratified() from repro/length-null/scripts/length_analysis.py) shown as code in §3. md2tex.py prints fenced code with listings. No number changed.
- 2026-11-05: prose rewritten paragraph by paragraph against EditLens (open 3B) scores and WRITING_RULES group L (named things, split list sentences, case before label). No number, placeholder or verdict changed; main.pdf rebuilt. Data and tools: road-to-robotics journal/papers/ai-map/2026-11-05_rewrite/.
- 2026-11-05: Robometer per-episode scores recovered from the private Hub dataset ravediamond/g9a-ab-results (no re-score needed, $0). Analysis (c) of the length-null protocol now runs (amendment committed before any number): Robometer within policy 0.821 (CI 0.794-0.847), 0.12 below length with a paired CI that excludes 0; truncated prefixes at 0.25, 0.5 and 0.75 of the longest episode; truncation figure and limitation updated. The $6 re-score is not needed.
- 2026-11-06: WS-133 part 2 (go vast WS-133, cap $5, spent $1.83): the released ArmnetBench fine-tune of Robometer scored on the 2,047 rollouts. IN-SAMPLE: its training set is all 2,499 ArmnetBench episodes with no held-out split. 0.994 pooled, 0.994 within policy, 0.052 above length (paired CI 0.039 to 0.067); 8 frames per episode (training length), 64 frames on 160 episodes 0.995. Protocol PROTOCOL_FT.md frozen before any score, three numbered deviations before any score was analysed (config keys, 64-frame tiled videos, 8-frame primary for cost). Abstract, Table 1, section 3, limitations, conclusion and Figure 1 updated.
- 2026-11-06: two paragraphs polished against EditLens with ws paper-polish (introduction, mid-episode monitors); mean 0.176 to 0.170, worst paragraph 0.299 to 0.268; the candidates are in polish/iterlog.jsonl. No number changed.
