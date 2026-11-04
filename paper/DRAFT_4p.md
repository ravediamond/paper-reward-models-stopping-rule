# What a reward model can show depends on who stopped the episode: failure judges and monitors on a low-cost arm

*Ravindu Somawansa, Shisso Robotics, Paris — draft, 4-page workshop version. Rendered by `make_paper.py` from the
result files; every number is a placeholder filled from `numbers.json`, which records each value's anchor. The
appendix maps every analysis to its result file and protocol.*

## Abstract

Reward models that score robot rollouts are also used as failure detectors, and the baseline they must beat depends
on who stopped the episode. On 2,047 public SO-101 rollouts from 7 policies, where runs end at a time
limit, plain episode length separates failure from success at AUROC 0.942 within policy — and still
0.851 when only half of the longest run has been observed: failed runs are slow, not timed out. Both
zero-shot reward models we test score below that baseline (the best reaches 0.821 within policy). On our own
operator-stopped rollouts the regime flips: length falls to 0.56, neither reward model beats the
policy-identity null, and what works is a judge at rest — a robot-trained 27B judge passes its pre-registered bar,
though its operating threshold is in-sample, and every mid-episode monitor we tested misses the bar. We recommend
reporting a length baseline, within policy, and the dataset's stopping rule.

## 1 Introduction

A reward model that scores robot rollouts is also a failure detector, and papers evaluate it as one. Any such
evaluation has a hidden variable: the dataset's *stopping rule* — who decides that an episode is over. When a
benchmark stops failed runs at a time limit, how long an episode ran encodes its outcome, and a detector should be
read against the baselines the stopping rule hands out for free: elapsed length, and the identity of the policy that
ran. When an operator stops each run by judgment, those baselines collapse, and the task changes. None of the
reward-model papers in our library reports how far plain episode length gets on the same data. We measure it on a
public SO-101 benchmark and on our own rollouts, with the length analyses frozen before the numbers,
and set every learned judge and monitor we ran against it. Contributions: (i) a pre-registered length analysis of
2,047 public rollouts, pooled, within policy and truncated in time; (ii) the same analysis for two zero-shot
reward models, with the stopping-rule baselines beside them; (iii) judge and monitor gates
on 88 operator-stopped rollouts of our own, with every in-sample threshold disclosed.

## 2 Data and labels

ArmnetBench v0.1 (SO-101, 8 tasks, 7 policies): 2,047 policy rollouts with a success or
failure class (515 successes, 1,532 failures); teleoperated episodes excluded. One task (pushing a
Displayport cable, 270 rollouts) has rollouts of a single class and so no per-task AUROC. Our rollouts: 88
labelled bowls-task episodes on one SO-101 arm and a Jetson Orin NX, and the 50-episode subset (42 successes, 8
failures) every monitor gate used. Labels are the operator's, not blind to policy.

## 3 The length baseline

Table 1 carries the numbers. Pooled over policies, length gives 0.938 (CI 0.925–0.951);
within each policy it ranges 0.91–0.96, pair-weighted 0.942
(CI 0.927–0.956): the baseline is not the policy identity (Fig. 1). Robometer-4B,
run zero-shot as its authors ship it, gives 0.818 pooled (CI 0.790–0.843) and 0.821 within
policy (pair-weighted over the per-policy scores, which span 0.79–0.87; its per-episode
scores were not stored, so these carry no episode-bootstrap CI). The protocol fixed Robometer's primary score as its
success probability; read descriptively from the same run, its last-progress head does better, 0.838 pooled,
but stays below length. TOPReward (Qwen3-VL-8B, no training; the primary score, fixed before
any score, is the paper's success score) gives 0.653 pooled (CI 0.623–0.684) and
0.661 within policy (CI 0.631–0.692), below length by -0.31 to -0.25 (paired
95 % CI); its full-video Yes/No component alone reaches 0.678 within policy, descriptively.

Table 1: ArmnetBench, failure AUROC with 95 % episode-bootstrap CIs. The Robometer within-policy entry is pair-weighted over its per-policy block and carries the per-policy range instead of a CI (per-episode scores not stored); the last-progress entry is descriptive (the protocol's primary score was the success probability).

| signal | pooled | within policy |
|---|---|---|
| episode length | 0.938 (0.925–0.951) | 0.942 (0.927–0.956) |
| length seen up to 50 % of the longest run | — | 0.851 (0.829–0.873) |
| Robometer-4B, success probability | 0.818 (0.790–0.843) | 0.821 (per-policy 0.79–0.87) |
| Robometer-4B, last progress (descriptive) | 0.838 (no CI) | — |
| TOPReward, success score | 0.653 (0.623–0.684) | 0.661 (0.631–0.692) |
| TOPReward, Yes/No component (descriptive) | — | 0.678 |

![Failure AUROC on ArmnetBench (95 % CIs where available): episode length against two zero-shot reward models (Robometer-4B, TOPReward with Qwen3-VL-8B). The last-progress bar is descriptive and carries no CI. The Displayport-cable task contributes rollouts of one class only and has no per-task AUROC.](fig/armnetbench.png)

## 4 Is it the timeout?

Only 8.7 % of failures run to the task's longest episode. Observing length only up to half of that, when
88 % of failures but 19 % of successes are still running, gives 0.851 within policy
(CI 0.829–0.873; Fig. 2; TOPReward on frames up to the same cut: 0.667): failed rollouts are slow,
not timed out. Both pre-registered readings hold: length is a within-policy null, and it is more than the timeout. On
our own operator-stopped rollouts the same baseline is at chance (0.56 on the 69; 0.52
on all 88). Neither reward model beats the policy-identity null there: TOPReward 0.82
(CI 0.70–0.93) against 0.87 for policy identity alone, and 0.78 on the
50 episodes without TurboVLA (17 of the 25 failures in the
69 come from TurboVLA); Robometer 0.577 against 0.878 on 88. The baseline depends
on how episodes end, which is why it must be reported per dataset; what works on operator-stopped runs is the judge
at rest (§5).

![Length observed up to a fraction of the task's longest episode, AUROC within policy (band: 95 % CI).](fig/truncation.png)

## 5 Judges and monitors on our rollouts

Table 2 carries every judge and monitor with the same triple: threshold-free AUROC where defined, failures caught and
successes flagged at the operating point. Every operating threshold of the judges at rest is chosen in-sample on the
same 50 episodes; the AUROCs are not.

**At rest.** A deterministic top-camera check (colour masks and geometry, no learning) is right on 94.3 % of
judged episodes with 0 false positives (Wilson 0–13 %) and 5 false negatives. Given a
64-frame two-view clip and NVIDIA's prompt, Flora-Rewarder-27B reaches a threshold-free AUROC of
1.00 (bootstrap CI 1.00–1.00); at its in-sample operating point it flags 8 of 8
failures at 2 of 42 successes (Wilson on the false alarms 1–16 %) and passes its pre-registered
bar. Its base model Qwen3.5-27B reaches 0.91 (0.78–1.00; 7/8 at 2/42)
on the same input at its own in-sample threshold; Qwen3.5-9B reaches 0.75 (7/8 at
16/42) and Gemini 3.8 Flash 0.96 (8/8 at 3/42, one false alarm over the
bar): neither passes. The input format, not the robot fine-tune, decided the result.

**Mid-episode.** A Gemini sliding-window judge catches 0 of 8 failures at 1 of 42; the surprise
of a separate world model, trained in the LeWorldModel recipe, catches 2 of 8 at 2 of 42
(AUROC 0.86, Wilson 7–59 %); the same model's latent drift catches 0 at 2 of 42
(AUROC 0.30). An action-conditioned risk head on the world model's latent reached 0.93 in a first
version that read elapsed time, and that result is withdrawn; the pre-registered second version, without time or
length, catches 3 of 8 at 5 of 42 (AUROC 0.79 against 0.71 with shuffled
actions; Wilson 14–69 %), and its MLP variant 6 of 8 at 13 of 42. No monitor meets the
bar of at least 5 of 8 failures at no more than 1 of 20 false interventions (Fig. 3).

Table 2: Judges and monitors on 50 own operator-stopped rollouts (42 successes, 8 failures). Judges score the finished episode; monitors score mid-episode windows against the monitor bar (≥ 5/8 caught at ≤ 1/20 false interventions). "In-sample" marks an operating threshold chosen on these same 50 episodes.

| method | kind | AUROC | caught / 8 | flagged / 42 | threshold |
|---|---|---|---|---|---|
| colour judge (no learning) | at rest | — (94.3 % right, 0 FP, 5 FN) | — | — | fixed rule |
| Flora-Rewarder-27B | at rest | 1.00 (1.00–1.00) | 8 | 2 | in-sample |
| Qwen3.5-27B, same input | at rest | 0.91 (0.78–1.00) | 7 | 2 | in-sample |
| Qwen3.5-9B, same input | at rest | 0.75 | 7 | 16 | in-sample |
| Gemini 3.8 Flash, same input | at rest | 0.96 | 8 | 3 | in-sample |
| Gemini sliding windows | monitor | — | 0 | 1 | fixed before scoring |
| world-model surprise | monitor | 0.86 | 2 | 2 | fixed before scoring |
| world-model latent drift | monitor | 0.30 | 0 | 2 | fixed before scoring |
| risk head, logistic (v2) | monitor | 0.79 | 3 | 5 | 5-fold by episode |
| risk head, MLP (v2) | monitor | — | 6 | 13 | 5-fold by episode |

![Fifty own rollouts: failures caught (of 8) against successes flagged (of 42). Circles: mid-episode monitors; shaded: their bar (≥ 5/8 at ≤ 1/20). Squares: judges at rest (one score per finished episode) at their in-sample operating point; the monitor bar does not apply to them.](fig/own_monitors.png)

## 6 Related work

Reward models are increasingly proposed as zero-shot failure detectors for manipulation: Robometer
scales a general-purpose reward model by trajectory comparisons, and TOPReward reads token probabilities
of a video-language model as hidden rewards; a recent survey of verifiers for robot policies maps
the wider family. Mid-episode failure detection is its own line: FAIL-Detect and SAFE learn
uncertainty- and feature-based failure scores for imitation and VLA policies, FARM reads failure signals from
the internal states of a frozen world model, ReAP predicts action-conditioned risk, VLA-Corrector
 verifies stages to drive prompt-based recovery, Spotter pairs the embodied model with a
reflecting VLM, and REMORA tracks task progress through errors and recovery with a recurrent
distributional model. Benchmarks on the same low-cost arm — ArmnetBench and a standardized SO-101 VLA
benchmark — evaluate policies; none of these works reports the elapsed-length baseline under the
dataset's stopping rule, which is the comparison this paper adds.

## 7 Limitations

Two task families (ArmnetBench's eight tasks, our bowls task); our labels are the operator's and not blind; the risk
head is trained and tested on the same 50 episodes (5-fold by episode: episodes do not leak, tasks and policies do);
Robometer's within-policy and truncation analyses carry no episode-bootstrap CI and no truncation column because its
per-episode scores were not stored; TOPReward's prefix count, frames per query and Yes/No wording are not given in
its paper and are ours; the operating points of Flora-Rewarder-27B, Qwen3.5-27B and Gemini 3.8 Flash are chosen
in-sample on the 50 episodes they are scored on (their AUROCs are not); 17 of the 25
failures in our 69 rollouts are TurboVLA's, so on our set any score that reads the policy gets the identity null for
free; the timeout is approximated by each task's longest episode.

## Appendix: from plain name to analysis

Every number is recomputable from the repository; this table maps each analysis to its files.

| analysis | repro folder | expected files | protocol |
|---|---|---|---|
| length baseline, truncation | repro/length-null | length_armnetbench.json, counts_ci.json | LENGTH_PROTOCOL.md, frozen `1a69f30` |
| Robometer on ArmnetBench | repro/robometer-judge | g9a_ab_complete.json | PROTOCOL.md (primary score fixed there) |
| Robometer and length on own rollouts | repro/robometer-judge | g9a_own.json | PROTOCOL.md |
| colour judge | repro/robometer-judge | g9c3_test_results.json | PROTOCOL.md |
| TOPReward, both datasets | repro/topreward | topreward.json, own_rollout_labels.csv | TOPREWARD_PROTOCOL.md, `6241570` |
| judges at rest, input-format gate | repro/flora-input-format | g_flora_summary.json, g_flora_abl_summary.json | PROTOCOL.md |
| window judge, world-model monitors | repro/six-monitors | judge_tau.json, w1a_summary.json | PROTOCOL.md |
| action-conditioned risk head | repro/reap | monitors.json, monitors_v2.json | PROTOCOL.md |

## References (ids from the papers mirror)

Robometer — arXiv:2603.02115 · TOPReward — arXiv:2602.19313 · No Free Checker — arXiv:2609.09250 ·
FAIL-Detect — arXiv:2503.08558 · SAFE — arXiv:2506.09937 · FARM — arXiv:2609.11445 · ReAP — arXiv:2610.16309 ·
VLA-Corrector — arXiv:2609.06508 · Spotter — arXiv:2609.36808 · REMORA — arXiv:2610.39125 ·
ArmnetBench — arXiv:2607.24481 · SO-101 benchmark — arXiv:2606.08881 · LeWorldModel — arXiv:2603.19312 ·
TurboVLA — arXiv:2607.27205 · Flora-Rewarder-27B — NVIDIA model card · Qwen3-VL-8B, Qwen3.5 — model cards ·
Gemini 3.8 Flash — Google model page.
