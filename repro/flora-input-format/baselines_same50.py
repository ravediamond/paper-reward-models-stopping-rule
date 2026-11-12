"""Exploratory (added 2026-11-12, after the gate results were known; no bar): the two free baselines of the paper,
policy identity and episode length, on the same 50 episodes the judges at rest were scored on, and the paired
difference judge minus policy identity. Inputs: expected/g_flora_scores.csv (Flora-Rewarder-27B, per episode),
expected/g_flora_abl_scores.csv (Qwen3.5-27B, same input), ../topreward/expected/own_rollout_labels.csv (policy,
outcome, length of the 69 rollouts). Failure AUROC: failure is the positive class; a judge's score counts against
success (higher score = more likely success), length counts for failure (longer = failure), policy identity is the
in-sample failure rate of the episode's policy on these 50 (the same null as the paper's). Paired bootstrap over
episodes, 2,000 resamples, seed 0, 95 % percentile interval. Writes expected/baselines_same50.json."""
import csv, json, random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
E = HERE / "expected"


def auroc(y, s):
    """y: 1 = failure. s: higher = more likely failure. Ties count one half."""
    pos = [v for t, v in zip(y, s) if t]; neg = [v for t, v in zip(y, s) if not t]
    if not pos or not neg:
        return None
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def pol_rate(rows):
    f = defaultdict(int); n = defaultdict(int)
    for r in rows:
        n[r["policy"]] += 1; f[r["policy"]] += r["y"]
    return [f[r["policy"]] / n[r["policy"]] for r in rows]


def scores(rows, judge):
    return {"judge": [-r[judge] for r in rows], "policy_identity": pol_rate(rows), "length": [r["length"] for r in rows]}


def main():
    lab = {int(r["episode_index"]): r for r in csv.DictReader(open(HERE.parent / "topreward/expected/own_rollout_labels.csv"))}
    out = {"note": __doc__.split("\n")[0], "n_resamples": 2000, "seed": 0}
    for name, fn, arm in (("flora", "g_flora_scores.csv", None), ("qwen27", "g_flora_abl_scores.csv", "qwen27b")):
        rows = []
        for r in csv.DictReader(open(E / fn)):
            if arm and r["arm"] != arm:
                continue
            L = lab[int(r["episode"])]
            assert L["policy"] == r["policy"] and L["outcome"] == r["outcome"], (fn, r["episode"])
            rows.append({"policy": r["policy"], "y": int(r["outcome"] == "failure"), "length": int(L["length"]),
                         "score": float(r["score"])})
        y = [r["y"] for r in rows]
        S = scores(rows, "score")
        res = {"n": len(rows), "failures": sum(y), "successes": len(y) - sum(y),
               "failures_by_policy": {p: sum(r["y"] for r in rows if r["policy"] == p) for p in sorted({r["policy"] for r in rows})},
               "auroc": {k: auroc(y, v) for k, v in S.items()}}
        rng = random.Random(0); diffs = []
        for _ in range(2000):
            idx = [rng.randrange(len(rows)) for _ in rows]
            sub = [rows[i] for i in idx]; ys = [r["y"] for r in sub]
            if 0 < sum(ys) < len(ys):
                Ss = scores(sub, "score")
                diffs.append(auroc(ys, Ss["judge"]) - auroc(ys, Ss["policy_identity"]))
        diffs.sort()
        res["judge_minus_policy_identity"] = {"point": res["auroc"]["judge"] - res["auroc"]["policy_identity"],
                                              "ci95": [diffs[int(0.025 * len(diffs))], diffs[int(0.975 * len(diffs)) - 1]],
                                              "valid_resamples": len(diffs)}
        out[name] = res
    (E / "baselines_same50.json").write_text(json.dumps(out, indent=1))
    for k in ("flora", "qwen27"):
        print(k, {a: round(b, 3) for a, b in out[k]["auroc"].items()}, out[k]["judge_minus_policy_identity"])


if __name__ == "__main__":
    main()
