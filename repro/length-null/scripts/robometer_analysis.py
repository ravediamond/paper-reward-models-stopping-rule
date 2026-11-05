#!/usr/bin/env python3
"""Analysis (c) of PROTOCOL.md (amendment 2026-11-05): Robometer's p_succ under (a) and (b), against length, from the stored per-episode scores.

    python robometer_analysis.py            # reads ../expected/armnetbench_episodes.csv and ../expected/robometer_scores.jsonl
Writes ../expected/robometer_length.json. numpy and pandas only."""
import json
from pathlib import Path

import numpy as np
import pandas as pd

import length_analysis as LA

HERE = Path(__file__).resolve().parent; E = HERE.parent / "expected"


def paired_boot(d, f1, f2):
    """95 % interval of f1 - f2 on the same resamples (within policy, as LA.boot)."""
    rng = np.random.default_rng(LA.SEED); groups = [g for _, g in d.groupby("policy_type")]; v = []
    for _ in range(LA.B):
        s = pd.concat([g.iloc[rng.integers(0, len(g), len(g))] for g in groups]); a, b = f1(s), f2(s)
        if a is not None and b is not None:
            v.append(a - b)
    return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))]


def main():
    d = pd.read_csv(E / "armnetbench_episodes.csv"); d = d[d.success_class.isin(["successful", "failure"]) & (d.policy_type != "teleoperated")].copy()
    d["y"] = d.success_class == "successful"; d["neg_len"] = -d.length.astype(float); d["timeout"] = d.task.map(d.groupby("task").length.max())
    rb = {r["episode_index"]: r for r in (json.loads(l) for l in (E / "robometer_scores.jsonl").read_text().splitlines())}
    d["p"] = d.episode_index.map(lambda i: rb[i]["p_succ"] if i in rb else np.nan); n0 = len(d); d = d.dropna(subset=["p"]).copy()
    out = {"n_policy_rollouts": n0, "n_scored": len(d), "n_success": int(d.y.sum()), "n_failure": int((~d.y).sum()),
           "sources": {s: sum(1 for i in d.episode_index if rb[i]["source"] == s) for s in ("first-run", "rescore")}}
    out["pooled"] = {"auroc": LA.auroc(d.y, d.p), "ci95": LA.boot(d, lambda s: LA.auroc(s.y, s.p))}
    out["within_policy"] = {"auroc": LA.stratified(d, "p"), "ci95": LA.boot(d, lambda s: LA.stratified(s, "p"))}
    out["length_within_policy"] = {"auroc": LA.stratified(d, "neg_len"), "ci95": LA.boot(d, lambda s: LA.stratified(s, "neg_len"))}
    out["difference_within_policy"] = {"robometer_minus_length": out["within_policy"]["auroc"] - out["length_within_policy"]["auroc"],
                                       "ci95": paired_boot(d, lambda s: LA.stratified(s, "p"), lambda s: LA.stratified(s, "neg_len"))}
    out["per_policy"] = {p: {"n": len(g), "auroc": LA.auroc(g.y, g.p), "length_auroc": LA.auroc(g.y, g.neg_len)} for p, g in d.groupby("policy_type")}
    out["truncated"] = {}
    for t in LA.TS:
        def prefix(r):
            x = rb[r.episode_index]; k = np.arange(1, x["n_frames"] + 1) / x["n_frames"] * r.length
            ok = np.where(k <= t * r.timeout)[0]; return x["success_prob"][int(ok[-1]) if len(ok) else 0]
        d["pc"] = d.apply(prefix, axis=1); d["lc"] = -np.minimum(d.length.astype(float), t * d.timeout)
        out["truncated"][str(t)] = {"robometer_within_policy": LA.stratified(d, "pc"), "robometer_ci95": LA.boot(d, lambda s: LA.stratified(s, "pc")),
                                    "length_within_policy": LA.stratified(d, "lc"), "length_ci95": LA.boot(d, lambda s: LA.stratified(s, "lc")),
                                    "difference": LA.stratified(d, "pc") - LA.stratified(d, "lc"), "difference_ci95": paired_boot(d, lambda s: LA.stratified(s, "pc"), lambda s: LA.stratified(s, "lc")),
                                    "robometer_pooled": LA.auroc(d.y, d.pc)}
    out["reading"] = {"robometer_beats_length_within_policy": out["difference_within_policy"]["ci95"][0] > 0}
    (E / "robometer_length.json").write_text(json.dumps(out, indent=1)); print(json.dumps({k: out[k] for k in ("n_scored", "sources", "pooled", "within_policy", "length_within_policy", "difference_within_policy", "reading")}, indent=1))
    print({t: (round(v["robometer_within_policy"], 3), round(v["length_within_policy"], 3), [round(x, 3) for x in v["difference_ci95"]]) for t, v in out["truncated"].items()})


if __name__ == "__main__":
    main()
