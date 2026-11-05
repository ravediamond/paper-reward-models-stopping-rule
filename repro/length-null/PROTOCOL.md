<!-- copied verbatim from road-to-robotics journal/papers/failure-monitors/LENGTH_PROTOCOL.md, first committed 1a69f30 -->

# Length as the null model — analysis protocol (WS-077, frozen 2026-10-31 before any number)

Paper B (failure monitors, `FEASIBILITY.md`; WS-073 folded in as its §3–4). This file is committed before the
ArmnetBench metadata is read for this analysis; anything decided after it is labelled exploratory.

## Data

- **ArmnetBench** `armnet/armnetbench_v01_lerobot_so101` @ `1db69c82b589c7172ee31a6b8f7ef58d1fc2c663` (the revision
  G9a-AB used), `meta/` only (no video). Episodes kept exactly as G9a-AB: `success_class` ∈ {successful, failure}
  (other classes excluded), label y = 1 for successful. Length = the episode's frame count in the metadata (seconds =
  frames / fps). Policy = `policy_type`, task = the episode's task string.
- **Robometer scores** (G9a-AB per-episode `p_succ`, files `ab_top.jsonl` / `ab_top_rescore.jsonl`, or `scores_ab.csv`)
  — on the old Mac archive, not on the Orin. If not recovered, (c) is not run and the re-score (~$6 on vast) is listed
  for the owner; nothing is spent by this item.
- **Own rollouts**: the counts of the memo's evidence table (G9a-own, Judge τ, G16-B, W1-A, W1-C2, G-flora, G-flora-abl,
  REAP v1 / v2, G9c-3) as recorded in `journal/EXPERIMENTS.md`.

## Analyses

**(a) Within-policy length.** AUROC of −length for y, (i) pooled (as G9a-AB, reproduces 0.938), (ii) per policy (7),
(iii) per task, (iv) per task × policy cell with ≥ 5 successes and ≥ 5 failures. A stratified within-policy AUROC: the
pair-weighted mean of the per-policy AUROCs (each policy's AUROC weighted by its successes × failures). CIs: episode
bootstrap, 2,000 resamples, `numpy.random.default_rng(0)`, resampling episodes within each stratum.

**(b) Fixed-time truncation.** Per task, T = the task's timeout if the metadata states one, else the longest episode of
that task (stated in the output which applies). For t ∈ {0.25, 0.50, 0.75}: score = min(length, t·T) (time elapsed
when observed at t·T; every episode still running counts as t·T, ties averaged), AUROC of −score for y, pooled and
stratified within policy as in (a), same bootstrap. Also: the share of failures and of successes whose length is
≥ 0.98·T ("hit the timeout").

**(c) Robometer under (a) and (b)**, on its `p_succ`, if the files are found; plus the beyond-length statistic of
G9a-AB (AUROC inside global length quintiles) per policy.

**(d) Every count** k/n of the memo's evidence table: the Wilson score interval (95 %) and the episode-bootstrap
interval (2,000, seed 0; for a count of independent episodes, resampling the n episodes).

## Reading rules (fixed now)

- **Length is a real within-policy null** if the stratified within-policy AUROC (a) has a CI lower bound > 0.60. If
  instead its CI includes 0.60 or lower, the paper reports that length's pooled 0.938 is largely between-policy.
- **Length is more than the timeout** if the stratified AUROC at t = 0.50 (b) has a CI lower bound > 0.60; if not, the
  paper says the length signal on ArmnetBench is the timeout.
- **Robometer beats length within policy** only if its stratified within-policy AUROC exceeds length's with the paired
  bootstrap CI of the difference above 0 (if (c) runs).
- (d) is descriptive: every count in the draft is printed with both intervals.

## Outputs

`journal/papers/failure-monitors/length_analysis.py`, `results/length_armnetbench.json`, `results/counts_ci.json`,
`LENGTH_RESULTS.md`; then `DRAFT_4p.md` + `main.tex` (rendered as in WS-076).

## Amendment 2026-11-05 (before any Robometer number is computed)

The Robometer scores of G9a-AB were found in the private Hub dataset `ravediamond/g9a-ab-results` (`out/ab_top.jsonl`, `rescore/ab_top_rescore.jsonl`, `rescore/SHA256SUMS`), so analysis (c) runs and the $6 re-score is not needed. No frozen reading rule changes.

- **Rows.** 1,637 episodes scored in the first run plus the 462 re-scored after out-of-memory failures (`expected/robometer_scores.jsonl`, one row per episode: `p_succ`, the per-frame `success_prob`, `n_frames`, source). The analysed set is the same 2,047 policy rollouts as (a).
- **Scores.** `p_succ` is the success probability of the last scored frame of the full-episode pass, as in G9a-AB. The pass scores the episode's frames at 1 fps in one call.
- **(c) under (a).** Pooled and stratified within-policy AUROC of `p_succ`, with the episode bootstrap of (a) (2,000 resamples, `default_rng(0)`, resampling within policy). The paired difference to length is the stratified within-policy AUROC of `p_succ` minus that of −length on the same resamples, and the reading rule above applies to its 95 % interval.
- **(c) under (b).** For t ∈ {0.25, 0.50, 0.75} the score of an episode is `success_prob` at its last scored frame whose position, (k+1)/n_frames × length, is at most t·T; an episode with no such frame uses its first frame. T is the task's longest episode, as in (b). Length is cut at t·T as in (b) and the paired difference is taken on the same resamples.
- **Limit, stated now.** The per-frame values come from one pass over the whole episode. A frame's value can depend on later frames, so a prefix of that pass is not the score Robometer would give to a clip that ends at t·T. The truncation result is therefore an upper bound on what a truly truncated pass gives, if later frames help.
