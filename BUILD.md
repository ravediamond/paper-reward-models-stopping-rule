# Build (WS-093, 2026-11-01)

Assembled by road-to-robotics `scripts/paper_repo_build.py` from road-to-robotics and paper-vs-hardware at the commits in PROVENANCE.md, by copying only (100 files). Experiments: flora-input-format length-null reap robometer-judge six-monitors topreward .

- L0: every `repro/*/l0_check.py` passes from a fresh copy (`make l0`); nothing failed to reproduce.
- `make check` regenerates the paper from `repro/` and fails on any difference; two consecutive builds are byte-identical (`SOURCE_DATE_EPOCH` pinned).
- `paper/make_paper.py`: every read points into `repro/<exp>/expected/`; every anchor in `numbers.json` is remapped to that path (an unmapped anchor fails the build). Regenerated before any edit: all 61 values identical to road-to-robotics `journal/papers/failure-monitors/numbers.json`, `main.tex` and `DRAFT_4p.md` unchanged.
- Review of 2026-11-01 applied here (not in road-to-robotics): own-rollout results set against the policy-identity null (TOPReward 0.82 vs 0.87; 0.78 without TurboVLA; Robometer 0.577 vs 0.878), length on the same 69 (0.56), in-sample operating points of Flora / Qwen3.5-27B / Gemini stated and AUROC led with, judges at rest drawn as squares in Fig. 3 with the caption saying the monitor bar does not apply, CIs in Fig. 1, TOPReward's primary score stated as fixed before the run with its Yes/No component as descriptive, both statistics given per model in the abstract, title changed to the two-regime claim. 72 numbers now (11 added, all from `repro/`).
- `repro/length-null` is new (no paper-vs-hardware folder existed): `expected/armnetbench_episodes.csv` is derived from ArmnetBench's public metadata (five columns); its L0 recomputes every AUROC and Wilson interval with the standard library.
- Three published copies differ from the research-repo files only in redacted local strings (Flora's instance id, W1's weights path, the GGUF path); every number is identical.
- Not copied: reviews, feasibility memos, strategy notes, keys, raw data.
