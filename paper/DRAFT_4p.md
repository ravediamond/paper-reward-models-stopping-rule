# What a reward model can show depends on who stopped the episode: failure judges and monitors on a low-cost arm

*Ravindu Somawansa, Shisso Robotics, Paris — draft, 4-page workshop version. Rendered by `make_paper.py` from the
result files; every number is a placeholder filled from `numbers.json`, which records each value's anchor. The
appendix maps every analysis to its result file and protocol.*

## Abstract

Episode length is a failure detector that zero-shot reward models must beat, and how hard it is to beat depends on
who stopped the episode. On public SO-101 rollouts that end at a time limit, length alone separates failure from
success at AUROC 0.942 within policy. It does not need the timeout: watched only up to half of the longest
episode, it still gives 0.851, because failed runs are slow rather than cut off. Both reward models we test
score below it, the better one at 0.821. On our own rollouts, which an operator stopped by judgment, length
falls to 0.56 and the picture reverses. Neither reward model beats the identity of the policy, a judge
that sees the finished episode passes its bar (at a threshold chosen in-sample), and every mid-episode monitor misses.
So report a within-policy length baseline, and name the dataset's stopping rule.

## 1 Introduction

A reward model that scores robot rollouts is also a failure detector, and papers evaluate it as one, mostly against
other learned detectors. The baseline that matters is often simpler. When a benchmark stops failed runs at a time
limit, the length of an episode encodes its outcome, and so does the identity of the policy that ran (we call the
second one the policy-identity null). When an operator stops each run by judgment, both signals collapse and the
detection task changes with them. Which of the two a dataset uses is its *stopping rule*, and none of the
reward-model papers in our library reports it or the length baseline it implies.

We started with a narrower claim, that elapsed time is the reward model to beat. Our own rollouts broke it: there,
length is near chance and a robot-trained judge passed its bar. The stopping rule is what separates the two results,
so it became the subject of the paper.

We measured length on a public SO-101 benchmark and on our own rollouts, with the length analyses
frozen before any number existed, and set against it two zero-shot reward models and every
judge and monitor we had run on our 88 operator-stopped rollouts.

## 2 Data and labels

ArmnetBench v0.1 covers the SO-101 with 8 tasks and 7 policies. We use its 2,047 policy
rollouts with a success or failure class (515 successes, 1,532 failures) and leave out the teleoperated
episodes. One task, pushing a Displayport cable (270 rollouts), has rollouts of a single class and so no per-task
AUROC. Our own data are 88 labelled bowls-task episodes on one SO-101 arm with a Jetson Orin NX, and the 50-episode
subset (42 successes, 8 failures) that every monitor gate used. The author was the operator: he stopped each run and
labelled it at rest, not blind to the policy.

## 3 The length baseline

On ArmnetBench, episode length is a strong failure detector, and not only because it tells the policies apart
(Table 1, Fig. 1). Pooled over policies it reaches 0.938. Within each policy it ranges from 0.91
to 0.96, or 0.942 pair-weighted, with a CI of 0.927–0.956.

Both reward models fall below it. Robometer-4B, run zero-shot as its authors ship it, scores
0.818 pooled and 0.821 within policy (pair-weighted over its per-policy scores, whose range stands in
for a CI; §7 says why). TOPReward, with Qwen3-VL-8B and no training, scores 0.661
within policy, and its paired difference to length has a 95 % CI of -0.31 to -0.25. The protocols
fixed each model's primary score before any score existed (Robometer's success probability, and the success score of
TOPReward's paper). The two descriptive rows of Table 1, read from the same runs, score higher but still below
length.

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

## 4 Is it the timeout?

If length only reflected the timeout, its signal would sit in the few runs that hit it. We take each task's longest
episode as its timeout, and only 8.7 % of failures run that long. At half that length, 88 % of
failures are still running but only 19 % of successes. Length observed up to that cut gives
0.851 within policy (CI 0.829–0.873; Fig. 2), and TOPReward on frames up to the same cut reaches
0.667. Failed rollouts are slow, not timed out. Both readings the protocol fixed in advance hold: length is a
real within-policy null, and it is more than the timeout.

![Length observed up to a fraction of the task's longest episode, AUROC within policy: most of the signal is there by half the episode (band: 95 % CI).](fig/truncation.png)

On our own operator-stopped rollouts the same baseline is at chance: 0.56 on the 69 rollouts
TOPReward scored and 0.52 on all 88. The baseline that matters here is the policy-identity null, because
17 of the 25 failures in the 69 come from one policy, TurboVLA.
Neither reward model beats it. TOPReward scores 0.82 (CI 0.70–0.93) against
0.87 for policy identity alone, and 0.78 on the 50 episodes without TurboVLA.
Robometer scores 0.577 against 0.878 on all 88.

## 5 Judges and monitors on our rollouts

Table 2 reports every judge and monitor the same way: a threshold-free AUROC where one is defined, then failures caught
and successes flagged at the operating point. The judges at rest have their operating thresholds chosen in-sample on
the same 50 episodes (their AUROCs are not).

A judge that sees the finished episode works on these rollouts, and the input format matters more than the robot
fine-tune. A deterministic top-camera check (colour masks and geometry, no learning) is right on 94.3 % of
judged episodes, with 0 false positives (Wilson 0–13 %) and 5 false negatives. Given a
64-frame two-view clip and NVIDIA's prompt, Flora-Rewarder-27B reaches a threshold-free AUROC of
1.00 (bootstrap CI 1.00–1.00). At its in-sample operating point it flags 8 of 8
failures at 2 of 42 successes (Wilson on the false alarms 1–16 %), which passes the pre-registered
bar of at least 6 of 8 failures at no more than 2 of 42 successes. Its base model Qwen3.5-27B, without the
robot fine-tune, passes the same bar on the same input: AUROC 0.91 (0.78–1.00), 7 of 8 at
2 of 42. The smaller Qwen3.5-9B and Gemini 3.8 Flash fail it, the 9B by flagging
16 successes and Gemini by one false alarm too many.

No mid-episode monitor meets its bar of at least 5 of 8 failures at no more than 1 of 20 false interventions (Fig.
3). The surprise of a separate world model, trained in the LeWorldModel recipe, comes closest with 2
of 8 at 2 of 42 (AUROC 0.86). A Gemini sliding-window judge catches 0. The
action-conditioned risk head on the world model's latent has a history. Its first version reached AUROC
0.93, but it read elapsed time, so we withdrew that result and pre-registered a second version without time
or length. The second version catches 3 of 8 at 5 of 42, with AUROC 0.79 against
0.71 when its actions are shuffled, and its MLP variant catches 6 of 8 but flags 13 of 42.

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

Robometer and TOPReward are the two reward models we test. Robometer scales a
general-purpose reward model through trajectory comparisons, and TOPReward reads the token probabilities of a
video-language model as hidden rewards. A survey of verifiers for robot policies maps the wider
family. Mid-episode failure detection is its own line of work, and our monitors borrow from it. FAIL-Detect
 and SAFE learn uncertainty- and feature-based failure scores for imitation and VLA policies.
FARM reads failure signals from the internal states of a frozen world model, close to our world-model
monitors, and ReAP predicts action-conditioned risk, the idea behind our risk head. VLA-Corrector
, Spotter and REMORA add stage verification, a reflecting VLM and recurrent
progress tracking.
ArmnetBench and a standardized SO-101 VLA benchmark evaluate policies on the same
low-cost arm. None of these works reports the elapsed-length baseline under the dataset's stopping rule, and that
comparison is what this paper adds.

## 7 Limitations

The result most likely to move is the judge pass on our own rollouts. It rests on 8 failures, labels the author gave
without being blind to the policy, and operating thresholds chosen on the same 50 episodes; fresh rollouts scored at
those frozen thresholds would test it. Policy identity is the next concern: 17 of the 25
failures in our 69 rollouts are TurboVLA's, so any score that reads the policy gets the policy-identity null for free.
The risk head is trained and tested on the same 50 episodes (five folds by episode keep episodes from leaking, but
tasks and policies do leak). Robometer's within-policy number has no episode-bootstrap CI and Robometer is missing
from the truncation analysis, because its per-episode scores stayed on an older machine; a copy from that machine or a
re-score of about $6 would restore both. TOPReward's paper does not give its prefix count, frames per
query or Yes/No wording, so those are our choices. The ArmnetBench result covers eight tasks, and the timeout is
approximated by each task's longest episode.

## 8 Conclusion

Before evaluating a reward model as a failure detector, run episode length within policy on the same rows, and say how
the episodes ended. On a benchmark that stops at a time limit, length was the detector to beat, and neither reward
model beat it. On rollouts an operator stopped, length was useless, and what caught failures was a judge that saw the
whole finished episode in the right input format.

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
