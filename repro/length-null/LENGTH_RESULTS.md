# WS-077 · Length as the null model — results (protocol `LENGTH_PROTOCOL.md`, frozen `1a69f30`)

ArmnetBench `armnet/armnetbench_v01_lerobot_so101` @ `1db69c82`, `meta/` only; G9a-AB's set: the 7 policies' rollouts,
`success_class` in {successful, failure}: **2047 episodes (515 successes, 1532 failures)**. Teleoperated episodes
(400, all successes) excluded, as G9a-AB did; with them the pooled AUROC is 0.911 (first run, superseded: the protocol
fixes G9a-AB's set). Length = frames; timeout T per task = the task's longest episode (the metadata states none).
Episode bootstrap, 2,000 resamples, seed 0, within policy strata. Script `length_analysis.py`, output
`results/length_armnetbench.json`, `results/counts_ci.json`.

## (a) Within-policy length

| statistic | AUROC | 95 % CI |
|---|---|---|
| pooled (G9a-AB reported 0.938) | 0.938 | [0.925, 0.951] |
| **stratified within policy** (pair-weighted) | **0.942** | **[0.927, 0.956]** |
| policy act (n 321, 67 ok) | 0.941 | [0.901, 0.976] |
| policy diffusion (n 237, 53 ok) | 0.930 | [0.885, 0.969] |
| policy grootn1.7 (n 228, 83 ok) | 0.911 | [0.869, 0.951] |
| policy molmoact2 (n 473, 71 ok) | 0.945 | [0.908, 0.974] |
| policy pi0 (n 234, 87 ok) | 0.963 | [0.937, 0.984] |
| policy pi0.5 (n 235, 109 ok) | 0.945 | [0.913, 0.974] |
| policy smolvla (n 319, 45 ok) | 0.955 | [0.900, 0.991] |

Per task (8): Insert the colourful ring 0.97; Insert the missing tool 0.86; Push the Displayport cable n/a (0 policy successes); Put the eye drops 0.96; Put the eye drops 0.98; Remove the power cable 0.95; Remove the small middle 0.91; Stack the colouful blocks 0.90. Task x policy cells with >= 5 successes and >= 5 failures: 38, AUROC 0.61-1.00 (median 0.98).

## (b) Fixed-time truncation

Failures that run to >= 0.98 T: **8.7 %**; successes: 0.2 %.

| observed up to | pooled AUROC | within policy | 95 % CI (within) | failures still running | successes still running |
|---|---|---|---|---|---|
| 25 % of T | 0.610 | 0.617 | [0.588, 0.644] | 98.6 % | 73.0 % |
| 50 % of T | 0.838 | 0.851 | [0.829, 0.873] | 88.0 % | 18.6 % |
| 75 % of T | 0.927 | 0.931 | [0.915, 0.946] | 61.2 % | 4.7 % |

## Reading (rules fixed in the protocol)

- **Length is a real within-policy null: yes** (stratified CI lower bound 0.927 > 0.60).
- **Length is more than the timeout: yes** (at 50 % of T, within-policy CI lower bound 0.829 > 0.60). Few failures hit the timeout; most are still running when successes have ended.
- **(c) Robometer under (a)-(b): not run.** Its per-episode scores (`ab_top.jsonl`, `ab_top_rescore.jsonl`) are on the old Mac archive, not on the Orin. Owner: copy them from the Mac, or approve the ~$6 re-score on vast.

## (d) Every count of the memo's evidence table

| count | k / n | Wilson 95 % | bootstrap 95 % |
|---|---|---|---|
| Judge τ: failures caught | 0 / 8 | 0.0-32.4 % | 0.0-0.0 % |
| Judge τ: successes interrupted | 1 / 42 | 0.4-12.3 % | 0.0-7.1 % |
| G16-B: failures flagged | 8 / 8 | 67.6-100.0 % | 100.0-100.0 % |
| G16-B: successes flagged | 41 / 42 | 87.7-99.6 % | 92.9-100.0 % |
| W1-A L2 surprise: failures caught | 2 / 8 | 7.1-59.1 % | 0.0-62.5 % |
| W1-A L2 surprise: false interventions | 2 / 42 | 1.3-15.8 % | 0.0-11.9 % |
| W1-A cosine drift: failures caught | 0 / 8 | 0.0-32.4 % | 0.0-0.0 % |
| W1-A live reflex: successes flagged | 42 / 42 | 91.6-100.0 % | 100.0-100.0 % |
| G-flora: failures flagged | 8 / 8 | 67.6-100.0 % | 100.0-100.0 % |
| G-flora: successes flagged | 2 / 42 | 1.3-15.8 % | 0.0-11.9 % |
| G-flora-abl Qwen3.5-27B: failures | 7 / 8 | 52.9-97.8 % | 62.5-100.0 % |
| G-flora-abl Qwen3.5-27B: successes | 2 / 42 | 1.3-15.8 % | 0.0-11.9 % |
| G-flora-abl Qwen3.5-9B: successes flagged | 16 / 42 | 25.0-53.2 % | 23.8-52.4 % |
| G-flora-abl Gemini 3.8 Flash: failures | 8 / 8 | 67.6-100.0 % | 100.0-100.0 % |
| G-flora-abl Gemini 3.8 Flash: successes | 3 / 42 | 2.5-19.0 % | 0.0-16.7 % |
| REAP v1 logistic: failures | 6 / 8 | 40.9-92.9 % | 49.7-100.0 % |
| REAP v1 logistic: false interventions | 7 / 42 | 8.3-30.6 % | 7.1-28.6 % |
| REAP v1 elapsed time: failures | 0 / 8 | 0.0-32.4 % | 0.0-0.0 % |
| REAP v2 logistic: failures | 3 / 8 | 13.7-69.4 % | 0.0-75.0 % |
| REAP v2 logistic: false interventions | 5 / 42 | 5.2-25.0 % | 2.4-21.4 % |
| REAP v2 MLP: failures | 6 / 8 | 40.9-92.9 % | 49.7-100.0 % |
| REAP v2 MLP: false interventions | 13 / 42 | 19.1-46.0 % | 16.7-45.2 % |
| REAP v2 GRU floor: failures | 2 / 8 | 7.1-59.1 % | 0.0-62.5 % |
| REAP v2 GRU floor: false interventions | 3 / 42 | 2.5-19.0 % | 0.0-16.7 % |
| G9c-3: false positives | 0 / 25 | 0.0-13.3 % | 0.0-0.0 % |
| G9c-3: false negatives | 5 / 62 | 3.5-17.5 % | 1.6-14.5 % |

Note: for k = 0 or k = n the bootstrap interval collapses to a point (nothing to resample); read the Wilson interval there.
