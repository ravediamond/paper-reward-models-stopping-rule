"""L0: recompute the length null (pooled and within-policy AUROC of -length, the 50 % truncation, the timeout share)
from expected/armnetbench_episodes.csv with LENGTH_PROTOCOL.md's filter, and every Wilson interval of
expected/counts_ci.json; compare with expected/length_armnetbench.json. Standard library only; bootstrap CIs are read."""
import csv, json, math
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"; R = json.loads((E / "length_armnetbench.json").read_text()); fails = 0


def check(name, got, want, tol=0.0005):
    global fails
    ok = abs(got - want) <= tol; fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (expected {want:.4f})")


def auroc(y, s):
    order = sorted(range(len(s)), key=lambda i: s[i]); ranks = [0.0] * len(s); i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and s[order[j + 1]] == s[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    n1 = sum(y); n0 = len(y) - n1
    return (sum(r for r, t in zip(ranks, y) if t) - n1 * (n1 + 1) / 2) / (n1 * n0) if n1 and n0 else None


def within(rows, score):
    num = den = 0.0
    for p in sorted({r["policy_type"] for r in rows}):
        g = [r for r in rows if r["policy_type"] == p]; y = [r["y"] for r in g]; a = auroc(y, [score(r) for r in g])
        if a is not None:
            w = sum(y) * (len(y) - sum(y)); num += a * w; den += w
    return num / den


rows = [r for r in csv.DictReader(open(E / "armnetbench_episodes.csv"))
        if r["success_class"] in ("successful", "failure") and r["policy_type"] != "teleoperated"]
for r in rows:
    r["y"] = r["success_class"] == "successful"; r["length"] = float(r["length"])
T = {}
for r in rows:
    T[r["task"]] = max(T.get(r["task"], 0), r["length"])
check("episodes", len(rows), R["n"], 0)
check("pooled AUROC of -length", auroc([r["y"] for r in rows], [-r["length"] for r in rows]), R["a_pooled"]["auroc"])
check("within-policy AUROC of -length", within(rows, lambda r: -r["length"]), R["a_within_policy_stratified"]["auroc"])
check("within-policy AUROC, length cut at 50 % of T", within(rows, lambda r: -min(r["length"], 0.5 * T[r["task"]])), R["b_truncated"]["0.5"]["within_policy"])
# (c) Robometer under (a) and (b), amendment 2026-11-05: recomputed from expected/robometer_scores.jsonl
C = json.loads((E / "robometer_length.json").read_text())
rb = {r["episode_index"]: r for r in (json.loads(l) for l in (E / "robometer_scores.jsonl").read_text().splitlines())}
for r in rows:
    r["ep"] = int(r["episode_index"]); r["p"] = rb[r["ep"]]["p_succ"] if r["ep"] in rb else None
rr = [r for r in rows if r["p"] is not None]
check("Robometer rows matched", len(rr), C["n_scored"], 0)
check("Robometer pooled AUROC", auroc([r["y"] for r in rr], [r["p"] for r in rr]), C["pooled"]["auroc"])
check("Robometer within-policy AUROC", within(rr, lambda r: r["p"]), C["within_policy"]["auroc"])
check("Robometer minus length, within policy", within(rr, lambda r: r["p"]) - within(rr, lambda r: -r["length"]), C["difference_within_policy"]["robometer_minus_length"])
for t in ("0.25", "0.5", "0.75"):
    def pre(r, t=float(t)):
        x = rb[r["ep"]]; n = x["n_frames"]; ok = [k for k in range(n) if (k + 1) / n * r["length"] <= t * T[r["task"]]]
        return x["success_prob"][ok[-1] if ok else 0]
    check(f"Robometer prefix within-policy AUROC at {t} T", within(rr, pre), C["truncated"][t]["robometer_within_policy"])
    check(f"length cut within-policy AUROC at {t} T", within(rr, lambda r, t=float(t): -min(r["length"], t * T[r["task"]])), C["truncated"][t]["length_within_policy"])

f = [r for r in rows if not r["y"]]
check("failures reaching 0.98 T", sum(r["length"] >= 0.98 * T[r["task"]] for r in f) / len(f), R["b_timeout_share"]["failures_hit"])
for name, c in json.loads((E / "counts_ci.json").read_text()).items():
    k, n, z = c["k"], c["n"], 1.959964; p = k / n; d = 1 + z * z / n; m = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    check(f"Wilson lower, {name}", m - h, c["wilson95"][0]); check(f"Wilson upper, {name}", m + h, c["wilson95"][1])
print("L0 PASS" if not fails else f"L0 FAIL ({fails})")
