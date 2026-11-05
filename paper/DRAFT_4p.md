# What a reward model can show depends on who stopped the episode: failure judges and monitors on a low-cost arm

*Ravindu Somawansa, Shisso Robotics, Paris — draft, 4-page workshop version. Rendered by `make_paper.py` from the
result files; every number is a placeholder filled from `numbers.json`, which records each value's anchor. The
appendix maps every analysis to its result file and protocol.*

## Abstract

Reward models that score robot rollouts are also used as failure detectors, and we compared two zero-shot reward
models with plain episode length. On ArmnetBench, a public SO-101 benchmark where runs end at a time limit, length
separates failure from success at AUROC 0.942 within policy. Failed runs there are slow rather than cut off,
and length observed only up to half of the longest episode still gives 0.851. Both reward models score below
length, the better one at 0.821. On our own rollouts, which an operator stopped by judgment, length falls to
0.56 and neither reward model beats the identity of the policy. A judge that sees the finished episode
passes its threshold there, at an operating point chosen in-sample, and no mid-episode monitor reaches its bar. The
baseline a detector has to beat depends on the dataset's stopping rule.

## 1 Introduction

Papers that evaluate a reward model as a failure detector usually compare it with other learned detectors. When a
benchmark stops failed runs at a time limit, the length of an episode also encodes its outcome, and so can the
identity of the policy that ran (we call this the policy-identity null). When an operator stops each run by judgment,
both signals are weaker. We call the way a dataset ends its episodes its *stopping rule*. None of the reward-model
papers in our library reports the stopping rule or a length baseline.

We started with a narrower claim, that elapsed time is the reward model to beat, and our own rollouts did not support
it: on them length is near chance, and a robot-trained judge passed its pre-registered threshold. The stopping rule
separates the two results, so it became the subject of the paper.

We measured length on ArmnetBench and on our own rollouts, with the length analyses frozen before any
number existed. We compared it with two zero-shot reward models, Robometer and TOPReward,
and on our 88 operator-stopped rollouts also with every judge and monitor we had run.

## 2 Data and labels

ArmnetBench v0.1 has 8 tasks and 7 policies on the SO-101. We use its 2,047 policy rollouts
with a success or failure class (515 successes, 1,532 failures) and leave out the teleoperated episodes.
One task, pushing a Displayport cable (270 rollouts), has rollouts of a single class and so no per-task AUROC.
Our own data are 88 labelled bowls-task episodes on one SO-101 arm with a Jetson Orin NX, and every monitor gate used
the same 50-episode subset (42 successes, 8 failures). The author was the operator, who stopped each run and labelled
it at rest, not blind to the policy.

## 3 The length baseline

On ArmnetBench, episode length is a strong failure detector within each policy (Table 1, Fig. 1). Pooled over policies
it reaches 0.938, and within each policy it ranges from 0.91 to 0.96. Pair-weighted,
the within-policy value is 0.942, with a CI of 0.927–0.956.

We ran Robometer-4B zero-shot, as its authors ship it, and it scores 0.818 pooled and
0.821 within policy. The within-policy value is pair-weighted over its per-policy scores, whose range stands
in for a CI (§7). TOPReward, run with Qwen3-VL-8B and no training, scores 0.661
within policy, and its paired difference to length has a 95 % CI of -0.31 to -0.25. The protocols
fixed each model's primary score before any score existed: the success probability for Robometer and the success score
of its paper for TOPReward. Two other scores from the same runs, listed in Table 1 as descriptive rows, are higher and
still below length.

Table 1: ArmnetBench, failure AUROC with 95 % episode-bootstrap CIs. Read down the within-policy column: no reward-model score reaches length.

| signal | pooled | within policy |
|---|---|---|
| episode length | 0.938 (0.925–0.951) | 0.942 (0.927–0.956) |
| length seen up to 50 % of the longest run | — | 0.851 (0.829–0.873) |
| Robometer-4B, success probability | 0.818 (0.790–0.843) | 0.821 (per-policy 0.79–0.87) |
| Robometer-4B, last progress (descriptive) | 0.838 (no CI) | — |
| TOPReward, success score | 0.653 (0.623–0.684) | 0.661 (0.631–0.692) |
| TOPReward, Yes/No component (descriptive) | — | 0.678 |

![Failure AUROC on ArmnetBench: episode length against two zero-shot reward models. Length leads both, pooled and within policy (95 % CIs where available).](fig/armnetbench.png)

## 4 Length is more than the timeout

We take each task's longest episode as its timeout, and only 8.7 % of failures run that long. At half that
length 88 % of failures are still running, against 19 % of successes. Length observed up to
that cut gives 0.851 within policy (CI 0.829–0.873; Fig. 2), and TOPReward on frames up to the same
cut reaches 0.667. Failed rollouts are slow, not timed out, and both readings fixed in the protocol hold.

![Length observed up to a fraction of the task's longest episode, AUROC within policy: most of the signal is there by half the episode (band: 95 % CI).](fig/truncation.png)

On our own operator-stopped rollouts length is at chance, with 0.56 on the 69 rollouts
TOPReward scored and 0.52 on all 88. The baseline to beat here is the policy-identity null, because
17 of the 25 failures in the 69 come from one policy, TurboVLA.
Neither reward model beats it. TOPReward scores 0.82 (CI 0.70–0.93) where policy
identity alone gives 0.87, and 0.78 on the 50 episodes without TurboVLA.
Robometer scores 0.577 on all 88, and policy identity 0.878.

## 5 Judges and monitors on our rollouts

Table 2 gives each judge and monitor a threshold-free AUROC where one is defined, and the failures caught and
successes flagged at its operating point, which for the judges at rest is chosen in-sample.

We first ran a deterministic top-camera check (colour masks and geometry, no learning). It is right on 94.3 %
of judged episodes, with 0 false positives (Wilson 0–13 %) and 5 false negatives. We then
gave Flora-Rewarder-27B a 64-frame two-view clip and NVIDIA's prompt, and it reaches a threshold-free
AUROC of 1.00 (bootstrap CI 1.00–1.00). At its in-sample operating point it flags 8
of 8 failures at 2 of 42 successes (Wilson on the false alarms 1–16 %), which passes the
pre-registered bar of at least 6 of 8 failures at no more than 2 of 42 successes. Its base model, Qwen3.5-27B
, has no robot fine-tune and passes on the same input too, with AUROC 0.91 (0.78–1.00) and
7 of 8 at 2 of 42. The input format mattered more than the fine-tune. Qwen3.5-9B flags
16 successes and fails, and Gemini 3.8 Flash fails by one false alarm.

No mid-episode monitor reaches its bar of at least 5 of 8 failures at no more than 1 of 20 false interventions on
these 50 rollouts (Fig. 3). The surprise of a separate world model, trained in the LeWorldModel recipe,
catches 2 of 8 at 2 of 42 (AUROC 0.86), and a Gemini sliding-window judge catches
0. We also built an action-conditioned risk head on the world model's latent. Its first version reached
AUROC 0.93, but it read elapsed time, so we withdrew that result and pre-registered a second version without
time or length. That version catches 3 of 8 at 5 of 42, with AUROC 0.79 against
0.71 for shuffled actions. The MLP variant catches 6 of 8 and flags 13 of 42.

Table 2: Judges and monitors on the 50 operator-stopped rollouts (42 successes, 8 failures). Judges see the finished episode; monitors are held to ≥ 5/8 caught at ≤ 1/20 false interventions.

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

![Failures caught against successes flagged on the 50 rollouts. No monitor (circles) reaches its shaded bar; the judges at rest (squares) sit at their in-sample operating point, where the monitor bar does not apply.](fig/own_monitors.png)

## 6 Related work

Robometer scales a general-purpose reward model through trajectory comparisons, and TOPReward
 reads the token probabilities of a video-language model as hidden rewards. A survey of verifiers for
robot policies covers the wider family. FAIL-Detect and SAFE learn uncertainty-
and feature-based failure scores for imitation and VLA policies. FARM reads failure signals from the internal
states of a frozen world model, as our world-model monitors do, and our risk head follows ReAP, which predicts
action-conditioned risk. VLA-Corrector verifies stages, Spotter adds a reflecting VLM, and
REMORA tracks progress through errors and recovery. ArmnetBench and a standardized SO-101 VLA
benchmark evaluate policies on the same arm. None of these works reports the elapsed-length baseline
under the dataset's stopping rule.

## 7 Limitations

The judge pass on our own rollouts rests on 8 failures and on operating thresholds chosen on the same 50 episodes,
which a single operator, the author, labelled without being blind to the policy. The threshold-free AUROCs do not
depend on the threshold, and fresh rollouts scored at the frozen thresholds would confirm the operating points.
17 of the 25 failures in our 69 rollouts are TurboVLA's, so any score that reads the policy
gets the policy-identity null for free. The risk head is trained and tested on the same 50 episodes, with five folds
by episode that keep episodes from leaking (tasks and policies do leak). Robometer's per-episode scores stayed on an
older machine. Its within-policy number therefore has no episode-bootstrap CI and it is missing from the truncation
analysis, and a copy from that machine or a re-score of about $6 would restore both. TOPReward's paper
does not give its prefix count, frames per query or Yes/No wording, so those are our choices. The ArmnetBench result
covers eight tasks, and the timeout is approximated by each task's longest episode.

## 8 Conclusion

On ArmnetBench, where runs end at a time limit, episode length beat both reward models. On our operator-stopped
rollouts length was at chance, and a judge that saw the whole finished episode caught the failures. When you evaluate
a reward model as a failure detector, report episode length within policy on the same rows and say how the episodes
ended.

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
