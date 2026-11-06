#!/usr/bin/env python3
"""G9a-FT analysis (G9A_FT_PROTOCOL.md): the released ArmnetBench fine-tune of Robometer against episode length, from ../expected/ft_rows.jsonl.

    python ft_analysis.py          # writes ../expected/ft_results.json
Primary: pooled AUROC of p_succ (8 frames), episode bootstrap (2,000, seed 0). Secondary: pair-weighted within-policy AUROC with its bootstrap, the paired
difference to length within policy, pooled last-progress (descriptive). Descriptive: p_succ_64 against p_succ and length on the episodes where it was scored.
All of it is IN-SAMPLE for the fine-tune: every evaluated episode is in its training set (protocol, leakage). numpy and pandas only."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent; E = HERE.parent / "expected"
sys.path.insert(0, str(HERE.parents[1] / "length-null" / "scripts"))
import length_analysis as LA  # noqa: E402
import robometer_analysis as RA  # noqa: E402,F401  (paired_boot)


def main():
    d = pd.read_csv(HERE.parents[1] / "length-null/expected/armnetbench_episodes.csv")
    d = d[d.success_class.isin(["successful", "failure"]) & (d.policy_type != "teleoperated")].copy()
    d["y"] = d.success_class == "successful"; d["neg_len"] = -d.length.astype(float)
    rows = {r["episode_index"]: r for r in (json.loads(l) for l in (E / "ft_rows.jsonl").read_text().splitlines())}
    for k in ("p_succ", "last_progress", "p_succ_64", "last_progress_64"):
        d[k] = d.episode_index.map(lambda i: rows[i].get(k) if i in rows and not rows[i].get("error") else np.nan)
    n0 = len(d); s = d.dropna(subset=["p_succ"]).copy()
    out = {"in_sample": True, "n_policy_rollouts": n0, "n_scored": len(s), "n_errors": int(sum(1 for r in rows.values() if r.get("error"))),
           "n_success": int(s.y.sum()), "n_failure": int((~s.y).sum()), "subsampled_episodes": int(sum(1 for r in rows.values() if r.get("attempts", 1) > 1))}
    out["pooled"] = {"auroc": LA.auroc(s.y, s.p_succ), "ci95": LA.boot(s, lambda x: LA.auroc(x.y, x.p_succ))}
    out["within_policy"] = {"auroc": LA.stratified(s, "p_succ"), "ci95": LA.boot(s, lambda x: LA.stratified(x, "p_succ"))}
    out["length_within_policy"] = {"auroc": LA.stratified(s, "neg_len"), "ci95": LA.boot(s, lambda x: LA.stratified(x, "neg_len"))}
    out["length_pooled"] = {"auroc": LA.auroc(s.y, s.neg_len)}
    out["difference_within_policy"] = {"finetune_minus_length": out["within_policy"]["auroc"] - out["length_within_policy"]["auroc"],
                                       "ci95": RA.paired_boot(s, lambda x: LA.stratified(x, "p_succ"), lambda x: LA.stratified(x, "neg_len"))}
    t = s.dropna(subset=["last_progress"])
    out["last_progress_pooled"] = {"auroc": LA.auroc(t.y, t.last_progress), "n": len(t)}
    out["per_policy"] = {p: {"n": len(g), "auroc": LA.auroc(g.y, g.p_succ), "length_auroc": LA.auroc(g.y, g.neg_len)} for p, g in s.groupby("policy_type")}
    u = s.dropna(subset=["p_succ_64"])
    out["subset_64"] = {"n": len(u), "p_succ_8_pooled": LA.auroc(u.y, u.p_succ), "p_succ_64_pooled": LA.auroc(u.y, u.p_succ_64), "length_pooled": LA.auroc(u.y, u.neg_len),
                        "p_succ_8_within_policy": LA.stratified(u, "p_succ"), "p_succ_64_within_policy": LA.stratified(u, "p_succ_64"), "length_within_policy": LA.stratified(u, "neg_len")}
    out["reading"] = {"finetune_beats_length_within_policy": out["difference_within_policy"]["ci95"][0] > 0,
                      "bar": {"length_pooled": 0.938, "length_within_policy": 0.942}}
    (E / "ft_results.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({k: out[k] for k in ("n_scored", "n_errors", "subsampled_episodes", "pooled", "within_policy", "length_within_policy", "difference_within_policy", "last_progress_pooled", "subset_64", "reading")}, indent=1, default=float))


if __name__ == "__main__":
    main()
