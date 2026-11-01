# What a reward model can show depends on who stopped the episode

Failure judges and reward models on a low-cost arm, set against elapsed time. On 2,047 public SO-101 rollouts that end at a time limit, episode length separates failures from successes better than two zero-shot reward models; on operator-stopped rollouts, length is blind and judges at rest work. Every number is recomputed from `repro/`.

## What is here

- `paper/`: the draft (markdown and LaTeX sources, `make_paper.py`, `numbers.json` with every number's anchor, generated `fig/`, the built `main.pdf`).
- `repro/`: one folder per experiment the paper cites (flora-input-format, length-null, reap, robometer-judge, six-monitors, topreward): protocol, scripts, the expected result files the paper reads, `l0_check.py`, `REPRODUCE.md`.
- `data/DATA.md`: every dataset and checkpoint, Hub id and pinned revision. No raw data is stored here.
- `PROVENANCE.md`: where every file was copied from.

## Reproduce

- **L0** (CPU, seconds): `make l0` — recompute every number from `repro/*/expected/`.
- **Paper**: `make check` — L0, then `paper/make_paper.py` regenerates `numbers.json` and the sources from the expected files and fails on any difference, then rebuilds the PDF (needs `tectonic`, numpy, matplotlib).
- **L1** (rerun on the stated hardware) and **L2** (the arm): per experiment, in `repro/<exp>/REPRODUCE.md`.

## Cost

vast.ai: $0.69 (TOPReward), Robometer and Flora runs as recorded in their folders; everything else on a Jetson Orin NX, $0.

## Licence

Code MIT; text and figures CC BY 4.0 (to confirm before any release).
