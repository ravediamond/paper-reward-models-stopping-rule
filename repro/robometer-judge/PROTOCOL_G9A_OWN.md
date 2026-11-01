# G9a-own protocol: Robometer-4B zero-shot on our own bowls rollouts (pre-registered 2026-10-16)

Frozen before any of our episodes is scored. This is the **baseline** for a later LoRA on our own data. G9a-AB has
already shown Robometer-4B is not a zero-shot judge (D34), so a fail here is expected and changes no plan. The
architecture's G9a bars (v0.8 §4: AUROC >= 0.9 and accuracy >= 90%) are applied and reported anyway.

## Data (all with video and operator labels)

- **Orin NX sessions:** `ravediamond/so101-bowls-policy-rollouts` (public, LeRobot v3.0, 30 fps): 69 episodes, 46
  success / 23 failure. Labels: `meta/rollout_labels.csv`, from the operator via the harness `trials.csv`.
  - Policies: act, smolvla, smolvla_vlacpp, smolvla_vlacpp_fa, vla_jepa (5 good policies, 6 failures between them)
    and four TurboVLA variants (17 failures).
- **M1 sessions** (old-Mac archive, now at `~/.cache/huggingface/lerobot/ravediamond/rollout_*` on this Mac):
  - 5 datasets, 22 episodes.
  - Labels: `shared/gate/data/rollout_catalog.csv` (`success`, `labeled`).
  - Episodes without a labelled row are excluded and counted.
  - Uploaded to the instance over SSH; never pushed anywhere.
- **The "73 rollouts (65 / 8)"** in architecture v0.8 is superseded by this inventory.
- **Camera:** `observation.images.front_top_camera` (640x480 AV1), the top camera, per the G9a-AB rule. The wrist
  camera is not scored.
- **Instruction:** each episode's own task string, verbatim: "Put the blue bowl in the pink bowl." (`turbovla_a`:
  "Pick up the blue bowl.").

## Scores (same model and pins as G9a-AB)

- **(A) G9a-AB input:** 1 fps over the episode, last frame included, native 640x480. `p_succ` = last-frame success
  probability.
- **(B) G9b input:** exactly 16 frames linspace over the episode, first and last included, resized to a 240 px
  shortest edge. This is the zero-shot baseline for any later LoRA.

## Metrics (success vs failure, per score)

- AUROC with a 2000-resample bootstrap 95% CI.
- Accuracy and balanced accuracy at t* = 0.124 (ArmnetBench complete-set threshold, fixed) and at 0.5.
- The threshold with maximum balanced accuracy on this set (descriptive only, in-sample).
- **Baselines:**
  - episode length;
  - policy identity: per-policy success rate, an upper bound. **This is the main confound:** 17 of 23 Orin failures
    are TurboVLA.
- AUROC on the non-TurboVLA policies only (6 failures: indicative).
- Per device (Orin NX / M1), and mean `p_succ` by failure mode.

**Bars (v0.8 §4):** AUROC >= 0.9 **and** accuracy >= 90% at t* = 0.124, on score (A). They are reported as
"G9a-own zero-shot: pass / fail". No decision depends on them; G9b and a LoRA on our data come first.

## Budget and execution

- One 48 GB vast.ai GPU, launched with `vast_g9a_ab.sh --own --cap 1`: ~40 min setup, ~15 min scoring, about $0.5.
- Results go to the private dataset `ravediamond/g9a-ab-results` under `own/`, with the same push, verify and
  self-destroy as G9a-AB.
- No per-episode scores in git.
