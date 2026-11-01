# G9c-3 protocol: the G9c judge at "still after the last release, or timeout" (pre-registered 2026-10-16)

Owner decision 2026-10-16, after G9c-2 ([report](results/g9c2/report.md)). Frozen before the rule is run on any
test rollout. Results are reported **next to** G9c and G9c-2, not replacing them.

**Nothing new is tuned:**
- the judge and its thresholds: `g9c_config.json` (ec3d4e0);
- the gripper threshold, stillness test and skin detector: `g9c2_rule.json` (bc88250), unchanged.

Only the end rule changes (no start-pose requirement), and so do the metrics and bars.

## Judge frame (recordings)

Inputs: `observation.state` (30 fps), top view (`front_top_camera`).

1. **Final release, t_rel:** the last frame where `gripper.pos > g_open` (10). If the gripper never opens, t_rel = 0.
2. **Still:** every arm joint moves less than `still_tol_deg` (1.5) over the past `still_s` (0.5 s). No start-pose
   requirement.
3. **Judge frame:** the **first** frame t >= t_rel + `still_s` where the arm is still, **or** the subtask timeout,
   whichever comes first.
   - On these recordings, the **subtask timeout = the recording's last frame**: each recording is one trial, ended by
     the harness's trial time limit or by the operator.
4. **The frozen G9c judge** runs with its window ending at the judge frame: last 1 s, extended back up to 3 s if
   occluded. An undecidable result counts as invalid.
5. **Hand:** the top view is scanned at `hand_fps` (5) from t_rel to the judge frame, with the frozen detector.
   **Any** detection makes the episode **invalid**. No re-tune (low priority, owner).

## Data

- The same 88 labelled bowls rollouts as G9c and G9c-2 (69 Orin NX + 19 M1).
- **Labels:** with the confirmed relabels of Orin 29 and 30 (success -> failure, `wrong_object`;
  [`data/labels/LABEL_CHANGES.md`](../../../data/labels/LABEL_CHANGES.md)), so 62 success / 26 failure.
- For comparison, the result is also reported on the labels as they were (64 / 24).
- **Dev sanity run** (teleop demos, as in G9c dev): reported, and it cannot change any parameter.

## Metrics

- **Coverage** = fraction of the 88 episodes judged (not invalid). **"Invalid" is not an error.**
- **Accuracy on judged episodes**, with a 95% bootstrap CI. **False positives** (failure judged success), counted.
- Also:
  - AUROC on judged episodes;
  - per-failure-type recall, on judged episodes;
  - invalid episodes by cause (hand / undecidable);
  - the judge frame relative to the release and to the recording end;
  - a confusion matrix and an error contact sheet;
  - side by side with G9c (86.4%, 0 FP) and G9c-2 (coverage 67%, 96.6% on judged, 0 FP).

## Pass rule (fixed, point estimates)

**"Deterministic judge usable at the subtask end"** if all three hold:

- **accuracy on judged >= 95%**;
- **zero false positives**;
- **coverage >= 90%**.

## Execution

- Mac, no GPU, no spend.
- Code: `g9c3_test.py`, the single test call; it reuses `g9c2_endrule.py`'s gripper, stillness and hand functions.
- Results: `judge/results/g9c3/`.
