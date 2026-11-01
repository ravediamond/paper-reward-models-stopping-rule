# Data and checkpoints (Hub pointers, pinned; nothing stored here)

| what | Hub id | revision | subset used |
|---|---|---|---|
| ArmnetBench SO-101 | `armnet/armnetbench_v01_lerobot_so101` | `1db69c82b589c7172ee31a6b8f7ef58d1fc2c663` | meta/ (length); top view (TOPReward, Robometer) |
| our rollouts | `ravediamond/so101-bowls-policy-rollouts` | `bad1c8ea363789f5f55f9098e775f7361a0f019f` | 69 episodes, front_top_camera, meta/rollout_labels.csv |
| Qwen3-VL-8B-Instruct | `Qwen/Qwen3-VL-8B-Instruct` | `0c351dd01ed87e9c1b53cbc748cba10e6187ff3b` | TOPReward |
| Robometer-4B | `robometer/Robometer-4B` | `beef63bc914c5c189329d49c6d712d96d632aa34` | G9a |
| Flora-Rewarder-27B, Qwen3.5-27B / 9B | as in `repro/flora-input-format/README.md` | — | G-flora |
| W1 world model | as in `repro/six-monitors/REPRODUCE.md` | — | W1-A, REAP |

`repro/length-null/expected/armnetbench_episodes.csv` is derived from ArmnetBench's `meta/episodes` (five columns, Apache-2.0), generated on the Orin on 2026-11-01.
