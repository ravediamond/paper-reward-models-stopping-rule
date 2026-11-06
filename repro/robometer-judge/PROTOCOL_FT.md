<!-- copied verbatim from road-to-robotics projects/vla-jepa-world-model/robometer/G9A_FT_PROTOCOL.md, first committed 81ce516, deviations 9c81794, a766ee3, a4b2501, run notes after -->

# G9a-FT: the released ArmnetBench fine-tune of Robometer against the length null (WS-133 part 2): protocol, frozen 2026-11-06 before any score

Owner (chat, 2026-11-06): "go vast WS-133", cap $5 (prompt `journal/prompts/2026-11-02_paper_fix_failure_monitors.md`, part 2). Design and bar from that prompt.

## Question

The paper tests Robometer-4B zero-shot and finds it below episode length on ArmnetBench. The obvious reply is to use the released fine-tune. Does `jesbu1/robometer-4b-fft-armnet-tiled` beat length, and on which episodes is that a fair test?

## Data and the leakage check (done before any score)

- Model `jesbu1/robometer-4b-fft-armnet-tiled` @ `b8098db5681317f48b5f286767e5fa01fd0abad5` (base Qwen3-VL-4B-Instruct, Apache-2.0). Input is the tiled frame its card describes: one 640 x 540 RGB frame with the `top` view above the `front` and `wrist` views.
- Tiled videos: `jesbu1/armnetbench_v01_tiled_so101` @ `384d04fcfbe77a373b77c059853d27b4c5fef74f`, 2,499 trajectories in a single `train` split (3.2 GB). Trajectory `trajectory_NNNNNN` is ArmnetBench episode_index NNNNNN, and its `quality_label` equals the `success_class` of `armnetbench_episodes.csv` for all 2,499 episodes (checked 2026-11-06: 1,532 failure, 915 successful, 52 suboptimal; tasks agree).
- **Leakage.** The model card lists this dataset, with no held-out split, as its training data. So every episode of the evaluation set is a training episode of the fine-tune, with its label. The comparison is **in-sample for the fine-tune** and is reported as that. It cannot show generalisation. It can show whether a model trained on these labels, scoring its own training episodes, beats length.
- Evaluated episodes: the same 2,047 policy rollouts of (a) (`success_class` in {successful, failure}, `policy_type` not teleoperated), selected by episode_index from the tiled trajectories.

## Scoring (same code path as the zero-shot run, `score_robometer.py`)

Robometer code at commit `352d160389daa964788de1ec933d1925f3a6de4f`, model loaded with `load_model_from_hf` from a local snapshot, bf16/default dtype as the zero-shot run. Per episode: frames of the tiled video at 1 fps with the last frame always included, the episode's task string verbatim, one forward pass, per-frame `progress` and `success_prob`. `p_succ` = the success probability of the last frame; `last_progress` = progress of the last frame. Out-of-memory handling as in the re-score (retry at full length, then subsample to 40 frames, flagged). One GPU of at least 48 GB.

## Metrics

Primary: pooled AUROC of `p_succ` for success against failure, with the episode bootstrap (2,000 resamples, `default_rng(0)`). Secondary: the pair-weighted within-policy AUROC with its bootstrap, the pooled AUROC of `last_progress` (descriptive), and the paired difference to length within policy (same resamples), computed with `repro/length-null/scripts/robometer_analysis.py`'s functions.

## Bar (from the prompt)

The bar is the paper's own length numbers: **0.938 pooled and 0.942 within policy** (a). The fine-tune beats length only if its within-policy AUROC exceeds length's with the 95 % interval of the paired difference above 0. Because the test is in-sample, a result above length is reported as "in-sample, no evidence of generalisation", and a result at or below length is reported as that, which would be a stronger statement.

## Checks before numbers

1. The model loads and produces finite `progress` in [0, 1] and `success_prob` in [0, 1] on two tiled episodes.
2. The tiled frame has the stated 640 x 540 shape, and the number of scored frames is about the episode's seconds.
3. A hand-computed AUROC on ten scored episodes equals the analysis code's.

## Cost

Cap $5, worst case counted as in `vast_g9a_ab.sh` (run cap plus grace at the hourly price plus download), on-demand verified offers only, hard deadline and self-destroy on the instance, results pushed to the private dataset `ravediamond/g9a-ab-results` under `ft/`. Credit before: $9.89.

## Deviations

1. **2026-11-06, before any score.** On the instance the first run stopped at check 1: `load_model_from_hf` at the pinned Robometer commit `352d160` raised `TrainingConfig.__init__() got an unexpected keyword argument 'optim'`. The fine-tune's `config.yaml` was written by a later training commit and carries training-only fields (`training.optim: adamw_8bit`) that the pinned code does not know. Change: the scorer loads the model from a local copy of `config.yaml` from which the keys the pinned code does not accept are removed one by one, and the list is written to `out/config_removed_keys.txt`. The inference code (the pinned commit), the frame sampling and the forward pass are unchanged. If any key other than a training field (optimizer, scheduler, logging) has to be removed, the run stops and a newer commit is considered as a further deviation. No score has been taken at this point.

2. **2026-11-06, before any score (the two-episode check gave two numbers, neither is analysed).** Check 2 showed 5 scored frames for episode 0, against 27 in the zero-shot run. The tiled trajectories are fixed-length videos: `ffprobe` gives 64 frames at 20 fps (3.2 s) for episodes 0, 1 and 2, whose original lengths are 510, 421 and 515 frames, so each video is 64 frames spread over the whole episode, and 1 fps of video time is not 1 fps of episode time. The fine-tune's `config.yaml` says `max_frames_after_preprocessing: 64` and `max_frames: 8` (training subsequences of up to 8 frames). Change: the primary score uses all 64 frames of the tiled video, so `p_succ` is the success probability of the last frame (the episode's last frame), as in the zero-shot run, which also scored every frame it sampled. A descriptive variant scores 8 frames spread uniformly over the 64, first and last kept, the training subsequence length (`p_succ_8`). Check 2 now reads: 64 frames decoded per video, tile 540 x 640. The bar, the data, the metric and the forward pass are unchanged.

3. **2026-11-06, before any score is analysed.** The first 14 episodes took 23 s each at 64 frames (an estimate of 13 hours, about $7, against the $5 cap), and the model was trained on subsequences of up to 8 frames (`max_frames: 8`). Change: the primary score is `p_succ`, the last-frame success probability of 8 frames spread uniformly over the 64 (first and last kept), for all 2,047 episodes. The all-64-frame score (`p_succ_64`) is computed on every 14th episode by `episode_index % 14 == 0` (146 episodes) and reported as a descriptive check of how much the frame count matters, with the same metric on that subset. The first run's 14 rows (64 frames and 8 frames) are kept as `ft_rows_v0_64frames_14eps.jsonl` and are not analysed. Bar, data, metric, forward pass and checks are unchanged. Cost: at about 2 to 3 s per episode for 8 frames the run is estimated at 90 minutes plus 50 minutes for the subset.

## Exploratory

Nothing chosen after data.

## Notes after the run (2026-11-06, written after the numbers; not part of the frozen text)

- The `mv` of the first run's rows to `ft_rows_v0_64frames_14eps.jsonl` did not take effect, so the second run resumed from them and skipped episodes 0 to 15. Those 16 rows carry the 64-frame score as `p_succ` and the 8-frame score as `p_succ_8`. The 8-frame score is the same computation as the new primary (8 frames spread uniformly over the 64, first and last kept), so for these 16 rows `p_succ_8` was moved to `p_succ` and the 64-frame values to `p_succ_64` (`from_first_run: true` in `ft_rows.jsonl`; the unmodified file is `ft_rows_raw.jsonl`). The 64-frame subset is therefore the 146 episodes with `episode_index % 14 == 0` plus these 16, 160 in all (two episodes coincide).
- All 2,047 episodes scored, none failed, none were subsampled. The instance was an A40 at $0.556/h; the whole job, including a first instance that never accepted ssh, cost $1.83 (credit 9.89 to 8.06).
- Removed config keys: `training.optim`, `training.torch_compile`, `training.torch_compile_backend`, all training-only (`config_removed_keys.txt`).
