<!-- copied verbatim from road-to-robotics projects/vla-jepa-world-model/robometer/G9A_AB_PROTOCOL.md, first committed 9d1764d -->

# G9a-AB protocol: Robometer-4B zero-shot as an SO-101 judge, on ArmnetBench (pre-registered 2026-10-14)

Frozen before any episode is scored. Changes after the first score are listed under "Deviations" with the reason and
are labelled exploratory. Owner decision of 2026-10-14: this runs **before** the community cache build.

## Question

Is Robometer-4B usable **zero-shot** as the System 2 judge on SO-101 data from another lab, with real policy
failures and several policies per task? ArmnetBench has 7 policies per task, so a judge can be tested **within each
policy**, which removes the policy-identity confound of our own 81 gate rollouts (where policy identity alone gave
0.76 AUROC).

## Inputs (pinned)

- Model: `robometer/Robometer-4B` @ `beef63bc914c5c189329d49c6d712d96d632aa34`; code `github.com/robometer/robometer`
  @ `352d160389daa964788de1ec933d1925f3a6de4f` (inference path of `scripts/example_inference_local.py`, model loaded
  once, `compute_batch_outputs`, `sample_type="progress"`).
- Data: `armnet/armnetbench_v01_lerobot_so101` @ `1db69c82b589c7172ee31a6b8f7ef58d1fc2c663` (LeRobot v3.0, 20 fps,
  apache-2.0). Labels: per-episode `success_class` (`successful` / `suboptimal` / `failure`), `policy_type`, task string.
- Set: **all 2099 policy rollouts** (`policy_type != teleoperated`): 915 successful, 52 suboptimal, 1532 failure; 8 tasks
  x 7 policies (act, diffusion, smolvla, pi0, pi0.5, grootn1.7, molmoact2). The 400 teleop episodes (all successful) are
  scored as a descriptive extra, not used for the pass. The full set fits the budget (episodes 4-58 s, ~24 frames at
  1 fps), so no sampling. Fallback if the cost estimate after 100 episodes projects above the cap: stratified sample of
  >= 500 rollouts balanced by task x policy x outcome (seed 0), decided and recorded before continuing.
- Views: **primary `top`** (overhead; the view also present in the k1000dai self-rollouts and closest in role to our
  `front_top_camera`); secondary `front`, reported, not used for the pass. Wrist not scored.

## Inference (fixed)

- Frames: the episode's segment of the concatenated video (`from_timestamp`..`to_timestamp`), sampled at **1 fps**
  (the repo default of `example_inference_local.py`: `extract_frames(fps=1.0)`), last frame of the episode always
  included, native resolution, RGB uint8; the model's collator does any further resizing / subsampling.
- Instruction: the episode's ArmnetBench task string, verbatim. No prompt variants, no tuning on this set.
- Outputs per episode: per-frame progress, per-frame success probability.
- **Score used for every metric:** `p_succ` = success probability of the **last frame**. Secondary (reported only):
  last-frame progress, max success probability over the episode.

## Metrics

1. **Pooled AUROC**, successful vs failure (suboptimal excluded), with a 2000-resample episode bootstrap 95 % CI.
2. **Within-policy AUROC** for each of the 7 policies (same binary contrast), with bootstrap CIs; their mean.
3. Per task and per task x policy AUROC (n/a where a class is empty: `cable_clip` has 0 successes in the set).
4. Suboptimal: (a) AUROC successful vs suboptimal and suboptimal vs failure, (b) three-class ordinal: Spearman between
   `p_succ` and failure < suboptimal < successful, (c) mean `p_succ` per class.
5. **Calibration** of `p_succ` (binary set): reliability table in 10 equal-width bins, ECE, Brier score, and accuracy /
   precision / recall / F1 at the paper's 0.5 threshold.
6. Baselines on the same episodes: policy identity (per-policy success rate as the score, fitted on all episodes, so
   an upper bound), episode length (shorter = success; ArmnetBench end-trims successes at `success_cutoff_time`, so
   length is a strong confound to beat), task identity.
7. Teleop (descriptive): mean `p_succ`, fraction above 0.5.

## Decision rule (fixed)

**"Robometer is usable as a zero-shot judge on SO-101"** if both hold, on the primary view, point estimates:
- pooled AUROC (successful vs failure) **>= 0.85**, and
- within-policy AUROC **>= 0.8 for at least 5 of the 7 policies**.

Otherwise: not usable zero-shot (LoRA, view or instruction changes become the next question; none is tried on this set).
The architecture's G9a thresholds (AUROC >= 0.9 and accuracy >= 90 % on our own bowls rollouts) are unchanged and
still apply to our data; this test is about transfer to other SO-101 data.

## Then: auto-labelling the k1000dai self-rollouts

Same setup, same score, after the ArmnetBench run and regardless of its outcome (the result says how much to trust the
labels): `k1000dai/so101_self_rollout` @ `657727f3326ca02fc51d22ebcad8220cc366706e`, 276 MolmoAct2 episodes, 30 fps,
view `top` (848x480), instruction = the dataset task string. Output per episode: `p_succ`, last progress, binary label
at 0.5, and the per-frame curves. Labels are "Robometer zero-shot", never mixed with owner labels.

## Budget and execution

- Hard cap **$20** for G9a-AB including the k1000dai labelling. One vast.ai GPU >= 24 GB, on-demand, hard deadline,
  self-destroy; destroy as soon as results are fetched. Only the needed camera videos are downloaded on the instance
  (public data, anonymous, no HF token on the instance).
- Results: `robometer/results_g9a_ab.json`, per-episode scores CSV (no videos), README section. Cost and wall time
  recorded.

## Deviations

All before any scored result was looked at for the analysis; none changes the set, the score, the metrics or the rule.

1. **Environment pins (2026-10-14/15):** the repo's `uv sync` resolves today to packages newer than the pinned commit
   and the model does not run: `torchao` > 0.13 needs torch > 2.8 (`ScalingType` import error), and unsloth 2026.10.x
   makes the Qwen3-VL backbone return `hidden_states=None`. Pinned `torchao==0.13.0`, `unsloth==2026.8.16`,
   `unsloth_zoo==2026.8.11` (the releases current on the code's commit date, 2026-08-13). Inference runs under
   `torch.autocast(bf16)` (model weights bf16, collator outputs float32). The first instance (2026-10-14) failed
   before scoring anything.
2. **Seen while debugging:** ArmnetBench episodes 0 and 1 (both `failure`, diffusion, ring insert) were scored on a
   debug instance to check the pipeline: `p_succ` 0.029 and 0.037. Nothing else was looked at.
3. **Runtime and results path:** ~12-15 s per episode at native 1024x576, so the four passes take ~16 h at ~$0.3/h
   (projected ~$5-6, under the $20 cap: the full set is kept, no sampling). Cap 20 h; results pushed to the private
   dataset `ravediamond/g9a-ab-results` every 20 min and at the end (so the instance does not depend on the machine
   that launched it); the instance destroys itself once the final push is verified.
4. **Contamination check (owner request, 2026-10-15, before any result was read).** Is ArmnetBench in Robometer-4B's
   training data? **No, for the pinned checkpoint:** its `config.yaml` (@ `beef63b`) has `data.train_datasets: [rbm-1m-id]`
   and `eval_datasets: [mw]`; in the code @ `352d160`, `robometer/data/dataset_category.py:305` (`rbm-1m-id`) does not
   list ArmnetBench; ArmnetBench was added later as its own alias `armnetbench_v01` (train + eval,
   `dataset_category.py:91-94`) by commit `f5af481` of 2026-06-28 ("Add ArmnetBench ... to the training mix"; also
   `configs/preprocess.yaml:23`, `data/dataset_success_cutoff.txt:66`, `data/datasets/name_mapping.py:96-97`). The
   ArmnetBench repos were created 2026-06-28 (`villekuosmanen/armnetbench_robometer_v01`), 2026-07-03
   (`armnet/armnetbench_v01_lerobot_so101`) and 2026-08-16 (`jesbu1/armnetbench_v01_tiled_so101`,
   `..._tiled_bimanual_so101`), all after the checkpoint's last commit (2026-03-10). Status: **clean** for `beef63b`;
   any later Robometer checkpoint may be contaminated. Had it been in training, the result would have been
   "contaminated, indicative only" and the real zero-shot test would move to our own rollouts.
5. **Within-policy AUROC eligibility:** computed only for policies with >= 10 successful and >= 10 failure episodes;
   excluded policies are listed. The second pass condition becomes "AUROC >= 0.8 for at least 5 eligible policies, or
   for all eligible policies if fewer than 5 are eligible"; the result states which applied. (From the label counts,
   all 7 policies have >= 45 successes and >= 126 failures, so all 7 are expected to be eligible.)
6. **k1000dai threshold:** a second threshold t* = the `p_succ` value with the maximum balanced accuracy on the
   ArmnetBench binary set (primary view). Labels are reported at 0.5 and at t*. They are marked **usable** only if
   G9a-AB passes (primary view, both conditions) **and** the contamination check is clean.
7. **Results push token:** the instance pushes with the owner's account-wide write token (owner decision 2026-10-15),
   copied over SSH to a 600 file on the instance only, not a repo-scoped token. Push from the instance tested
   (commit `7ad23ec` on the private dataset).
8. **Follow-up after the results (2026-10-16, exploratory):** length-confound checks, scoring-error audit and a k1000dai check in [`results/g9a_ab/report.md`](results/g9a_ab/report.md). The 462 errors are CUDA OOM covering two whole cable tasks. The k1000dai `labels_usable = True` flag is overruled by the owner: do not use those labels.
9. **Re-score of the 462 OOM episodes (2026-10-16, owner decision):** same pins, frames, instruction and score; top view only; fixed scorer (OOM recovery, frame cap 64, which subsampled no episode). RTX A6000 48 GB, 462/462 scored on the first attempt, ~$1. The verdict follows the rule on the complete set (2099 rollouts): **FAIL** (pooled 0.818). Results in `rescore/` of the private dataset and [`results/g9a_ab/report.md`](results/g9a_ab/report.md).
