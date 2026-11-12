# What a reward model can show depends on who stopped the episode

Failure judges and reward models on a low-cost arm, set against elapsed time. On 2,047 public SO-101 rollouts that the operator stopped (no set time limit), episode length separates failures from successes better than two zero-shot reward models; on operator-stopped rollouts, length is blind and judges at rest work. Every number is recomputed from `repro/`.

## What is here

- `paper/`: the draft (markdown and LaTeX sources, `make_paper.py`, `numbers.json` with every number's anchor, generated `fig/`, the built `main.pdf`).
- `repro/`: one folder per experiment the paper cites (flora-input-format, length-null, reap, reap-rebuild, robometer-judge, six-monitors, topreward): protocol, scripts, the expected result files the paper reads, `l0_check.py`, `REPRODUCE.md`.
- `data/DATA.md`: every dataset and checkpoint, Hub id and pinned revision. No raw data is stored here.
- `PROVENANCE.md`: where every file was copied from.

## From plain name to analysis

Each analysis of the paper, its folder, the expected files it reads and its protocol. The frozen commits named in the last column are in ravediamond/road-to-robotics, not in this repository's history; the protocols are copied here verbatim.

| analysis | repro folder | expected files | protocol |
|---|---|---|---|
| length baseline, truncation | repro/length-null | length_armnetbench.json, counts_ci.json | LENGTH_PROTOCOL.md, frozen `1a69f30` |
| Robometer on ArmnetBench | repro/robometer-judge, repro/length-null | g9a_ab_complete.json, robometer_length.json | PROTOCOL.md (primary score fixed there); length-null amendment 2026-11-05 |
| Robometer fine-tune on ArmnetBench (in-sample) | repro/robometer-judge | ft_rows.jsonl, ft_results.json | PROTOCOL_FT.md (frozen before any score; deviations numbered) |
| Robometer and length on own rollouts | repro/robometer-judge | g9a_own.json | PROTOCOL.md |
| colour judge | repro/robometer-judge | g9c3_test_results.json | PROTOCOL.md |
| TOPReward, both datasets | repro/topreward | topreward.json, own_rollout_labels.csv | TOPREWARD_PROTOCOL.md, `6241570` |
| judges at rest, input-format gate | repro/flora-input-format | g_flora_summary.json, g_flora_abl_summary.json | PROTOCOL.md |
| window judge, world-model monitors | repro/six-monitors | judge_tau.json, w1a_summary.json | PROTOCOL.md |
| action-conditioned risk head | repro/reap | monitors.json, monitors_v2.json | PROTOCOL.md |
| judges against the free baselines on the same 50 (exploratory, 2026-11-12) | repro/flora-input-format | baselines_same50.json (from `baselines_same50.py`) | none: added after the gate, no bar |
| ReAP Stage 1 + 2 rebuilt from the paper | repro/reap-rebuild | results.json (fetched by `fetch.py` from paper-register-reproducibility@b41d795) | upstream/PROTOCOL.md |

## Reproduce

- **L0** (CPU, seconds): `make l0` — recompute every number from `repro/*/expected/`.
- **Paper**: `make check` — L0, then `paper/make_paper.py` regenerates `numbers.json` and the sources from the expected files and fails on any difference, then rebuilds the PDF (needs `tectonic`, numpy, matplotlib).
- **L1** (rerun on the stated hardware) and **L2** (the arm): per experiment, in `repro/<exp>/REPRODUCE.md`.

## Cost

vast.ai: $0.69 (TOPReward), Robometer and Flora runs as recorded in their folders; everything else on a Jetson Orin NX, $0.

## Licence

Code MIT; text and figures CC BY 4.0 (to confirm before any release).
