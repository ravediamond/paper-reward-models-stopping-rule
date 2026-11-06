"""L0: recompute this post's numbers from the row-level files in expected/ (stdlib, numpy for tick files).
Where a number is a plain count or a summary with no rows behind it, it is read from the pinned result file and
compared; each line says which. Exit 1 on any mismatch."""
import csv, json, statistics, sys
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"
fails = 0


def check(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol
    fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (post: {want}, tol {tol})")


def J(name):
    return json.loads((E / name).read_text())

c = J("g9a_ab_complete.json")["complete"]
check("Robometer pooled AUROC, complete set", c["pooled_auroc"], 0.818, 0.0005)
check("rollouts scored", c["n_scored"], 2099, 0)
wp = c["within_policy"]
W = sum(v["n_success"] * v["n_failure"] for v in wp.values())
check("Robometer within policy, pair-weighted over the per-policy block", sum(v["auroc"] * v["n_success"] * v["n_failure"] for v in wp.values()) / W, 0.8206, 0.0005)
check("Robometer last-progress baseline, pooled", c["baselines"]["last_progress_auroc"], 0.8383, 0.0005)


# G9a-FT (PROTOCOL_FT.md): the released fine-tune on the 2,047 policy rollouts, IN-SAMPLE; recomputed from expected/ft_rows.jsonl and the episode list of length-null
FT = json.loads((E / "ft_results.json").read_text())
eps = [r for r in csv.DictReader(open(E.parent.parent / "length-null/expected/armnetbench_episodes.csv"))
       if r["success_class"] in ("successful", "failure") and r["policy_type"] != "teleoperated"]
ftr = {r["episode_index"]: r for r in (json.loads(l) for l in (E / "ft_rows.jsonl").read_text().splitlines())}


def _auroc(y, sc):
    order = sorted(range(len(sc)), key=lambda i: sc[i]); rk = [0.0] * len(sc); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and sc[order[j + 1]] == sc[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2 + 1
        i = j + 1
    n1 = sum(y); n0 = len(y) - n1
    return (sum(r for r, t in zip(rk, y) if t) - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else None


def _within(rows, score):
    num = den = 0.0
    for p in sorted({r["policy_type"] for r in rows}):
        g = [r for r in rows if r["policy_type"] == p]; y = [r["y"] for r in g]; a = _auroc(y, [score(r) for r in g])
        if a is not None:
            w = sum(y) * (len(y) - sum(y)); num += a * w; den += w
    return num / den


for r in eps:
    r["y"] = r["success_class"] == "successful"; r["len"] = float(r["length"]); r["p"] = ftr[int(r["episode_index"])]["p_succ"]
check("FT rows matched (in-sample)", len(eps), FT["n_scored"], 0)
check("FT pooled AUROC of p_succ (8 frames)", _auroc([r["y"] for r in eps], [r["p"] for r in eps]), FT["pooled"]["auroc"], 1e-9)
check("FT within-policy AUROC", _within(eps, lambda r: r["p"]), FT["within_policy"]["auroc"], 1e-9)
check("FT minus length, within policy", _within(eps, lambda r: r["p"]) - _within(eps, lambda r: -r["len"]), FT["difference_within_policy"]["finetune_minus_length"], 1e-9)
sub = [r for r in eps if ftr[int(r["episode_index"])].get("p_succ_64") is not None]
check("FT 64-frame subset size", len(sub), FT["subset_64"]["n"], 0)
check("FT 64-frame subset pooled AUROC of p_succ_64", _auroc([r["y"] for r in sub], [ftr[int(r["episode_index"])]["p_succ_64"] for r in sub]), FT["subset_64"]["p_succ_64_pooled"], 1e-9)

print("L0", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(1 if fails else 0)
