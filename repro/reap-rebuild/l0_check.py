"""L0: the ReAP rebuild numbers the paper cites, read from the pinned result file (fetched by fetch.py) and compared.
Plain counts and one AUROC from the upstream run; there are no row files here (they stay upstream). Exit 1 on any
mismatch."""
import json, sys
from pathlib import Path

E = Path(__file__).resolve().parent / "expected"
fails = 0


def check(name, got, want, tol):
    global fails
    ok = abs(got - want) <= tol
    fails += not ok
    print(f"{'ok ' if ok else 'BAD'} {name}: {got:.4f} (paper: {want}, tol {tol})")


m = json.loads((E / "results.json").read_text())["main_set"]
c = m["seed0"]["comb:true"]
check("main set failures (count)", m["failures"], 8, 0)
check("main set successes (count)", m["successes"], 42, 0)
check("combined monitor caught (of 8)", c["caught"], 2, 0)
check("combined monitor false interventions (of 42)", c["fi"], 1, 0)
check("combined monitor AUROC", c["auroc"], 0.72, 0.005)
check("seeds run", m["seeds_run"], 1, 0)
print("L0", "PASS" if fails == 0 else f"FAIL ({fails})")
sys.exit(1 if fails else 0)
