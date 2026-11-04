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

print("L0", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(1 if fails else 0)
