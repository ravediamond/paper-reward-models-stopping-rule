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
