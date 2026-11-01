# Reproduce

## L0 (CPU, seconds)
```bash
python3 l0_check.py
```
Recomputes the pooled and within-policy AUROC of −length, the 50 % truncation and the timeout share from `expected/armnetbench_episodes.csv` (the episode index, task, policy, class and length columns of ArmnetBench's metadata), and the Wilson intervals of `expected/counts_ci.json`; bootstrap CIs are read.

## L1 (CPU, minutes)
Download the metadata of `armnet/armnetbench_v01_lerobot_so101` @ `1db69c82b589c7172ee31a6b8f7ef58d1fc2c663` (`meta/` only, see data/DATA.md), then `python scripts/length_analysis.py --meta <dir>` (numpy, pandas, pyarrow).

## L2
Not applicable.
