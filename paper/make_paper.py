#!/usr/bin/env python3
"""WS-077: render the 4-page failure-monitors draft (WS-073 folded in as §3-4) and its figures from the result files.

    python3 journal/papers/failure-monitors/make_paper.py

Same pattern as edge-inference/make_paper.py: numbers.json (value + anchor), fig/*.pdf|png, DRAFT_4p.src.md ->
DRAFT_4p.md and main.src.tex -> main.tex by {{key}} placeholders; a placeholder without a value is an error.
"""
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
R = ROOT / "repro"
FIG = HERE / "fig"
N, A = {}, {}


def J(p):
    return json.loads(Path(p).read_text())


ANCHOR_MAP = [
 [
  "WS-085 TOPReward, results/topreward.json",
  "repro/topreward/expected/topreward.json, WS-085 TOPReward"
 ],
 [
  "WS-077 length analysis, results/length_armnetbench.json",
  "repro/length-null/expected/length_armnetbench.json, WS-077 length analysis"
 ],
 [
  "Wilson 95 %, results/counts_ci.json",
  "repro/length-null/expected/counts_ci.json, Wilson 95 %"
 ],
 [
  "G9a-AB complete, projects/vla-jepa-world-model/robometer/results/g9a_ab/complete.json",
  "repro/robometer-judge/expected/g9a_ab_complete.json, G9a-AB complete"
 ],
 [
  "G9a-own, .../g9a_own/g9a_own.json",
  "repro/robometer-judge/expected/g9a_own.json, G9a-own"
 ],
 [
  "G9c-3, .../judge/results/g9c3/g9c3_test_results.json",
  "repro/robometer-judge/expected/g9c3_test_results.json, G9c-3"
 ],
 [
  "G-flora, shared/gate/data/2026-10-20_g_flora/g_flora_summary.json",
  "repro/flora-input-format/expected/g_flora_summary.json, G-flora"
 ],
 [
  "G-flora-abl, .../2026-10-20_g_flora_abl/g_flora_abl_summary.json",
  "repro/flora-input-format/expected/g_flora_abl_summary.json, G-flora-abl"
 ],
 [
  "Judge tau, .../2026-10-19_judge_tau/judge_tau.json",
  "repro/six-monitors/expected/judge_tau.json, judge tau"
 ],
 [
  "W1-A, .../2026-10-19_w1_screening/w1a_summary.json",
  "repro/six-monitors/expected/w1a_summary.json, W1-A"
 ],
 [
  "REAP v2, paper-vs-hardware .../reap/expected/monitors_v2.json",
  "repro/reap/expected/monitors_v2.json, REAP v2"
 ],
 [
  "REAP v1, .../reap/expected/monitors.json",
  "repro/reap/expected/monitors.json, REAP v1"
 ]
]


def remap(anchor):
    for old, new in ANCHOR_MAP:
        anchor = anchor.replace(old, new)
    assert anchor.startswith("repro/") or "first commit" in anchor, f"anchor not mapped into the repo: {anchor}"
    return anchor


def put(k, v, anchor, fmt="{:.3f}"):
    N[k] = fmt.format(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else str(v)
    A[k] = remap(anchor)


def collect():
    L = J(R / "length-null/expected/length_armnetbench.json"); a = "WS-077 length analysis, results/length_armnetbench.json (LENGTH_PROTOCOL.md, 1a69f30)"
    put("ab_n", L["n"], a, "{:,d}"); put("ab_ok", L["n_success"], a, "{:,d}"); put("ab_fail", L["n_failure"], a, "{:,d}")
    put("len_pooled", L["a_pooled"]["auroc"], a); put("len_within", L["a_within_policy_stratified"]["auroc"], a)
    put("len_pooled_lo", L["a_pooled"]["ci95"][0], a); put("len_pooled_hi", L["a_pooled"]["ci95"][1], a)
    put("len_within_lo", L["a_within_policy_stratified"]["ci95"][0], a); put("len_within_hi", L["a_within_policy_stratified"]["ci95"][1], a)
    pp = [v["auroc"] for v in L["a_per_policy"].values() if v["auroc"] is not None]
    put("len_pol_min", min(pp), a, "{:.2f}"); put("len_pol_max", max(pp), a, "{:.2f}"); put("n_pol", len(pp), a, "{:d}")
    put("hit_fail", 100 * L["b_timeout_share"]["failures_hit"], a, "{:.1f}")
    t5 = L["b_truncated"]["0.5"]
    put("t50_within", t5["within_policy"], a); put("t50_lo", t5["within_policy_ci95"][0], a); put("t50_hi", t5["within_policy_ci95"][1], a)
    put("t50_run_fail", 100 * t5["still_running_failures"], a, "{:.0f}"); put("t50_run_ok", 100 * t5["still_running_successes"], a, "{:.0f}")
    g = J(R / "robometer-judge/expected/g9a_ab_complete.json")["complete"]
    a = "G9a-AB complete, projects/vla-jepa-world-model/robometer/results/g9a_ab/complete.json"
    put("rbm_pooled", g["pooled_auroc"], a); put("rbm_lo", g["pooled_ci95"][0], a); put("rbm_hi", g["pooled_ci95"][1], a)
    put("rbm_within", g["within_policy_mean"], a)
    o = J(R / "robometer-judge/expected/g9a_own.json")["A"]; a = "G9a-own, .../g9a_own/g9a_own.json"
    put("own_rbm", o["auroc"], a); put("own_len", o["baseline_length_auroc"], a, "{:.2f}"); put("own_n", o["n_success"] + o["n_failure"], a, "{:d}")
    put("own_rbm_pol", o["baseline_policy_identity_auroc"], a)
    c3 = J(R / "robometer-judge/expected/g9c3_test_results.json")["result"]; a = "G9c-3, .../judge/results/g9c3/g9c3_test_results.json"
    put("g9c3_acc", 100 * c3["accuracy_on_judged"], a, "{:.1f}"); put("g9c3_fp", c3["false_positives"], a, "{:d}"); put("g9c3_fn", c3["false_negatives"], a, "{:d}")
    fl = J(R / "flora-input-format/expected/g_flora_summary.json"); a = "G-flora, shared/gate/data/2026-10-20_g_flora/g_flora_summary.json"
    put("flora_f", fl["failures_flagged_at_k"], a, "{:d}"); put("flora_s", fl["successes_flagged_at_k"], a, "{:d}"); put("flora_auc", fl["auroc_score"], a, "{:.2f}")
    ab = J(R / "flora-input-format/expected/g_flora_abl_summary.json"); a = "G-flora-abl, .../2026-10-20_g_flora_abl/g_flora_abl_summary.json"
    put("q27_f", ab["qwen27b"]["failures_flagged_at_k"], a, "{:d}"); put("q27_s", ab["qwen27b"]["successes_flagged_at_k"], a, "{:d}")
    put("q9_auc", ab["qwen9b"]["auroc_score"], a, "{:.2f}"); put("gem_auc", ab["gemini38flash"]["auroc_score"], a, "{:.2f}")
    jt = J(R / "six-monitors/expected/judge_tau.json"); a = "Judge tau, .../2026-10-19_judge_tau/judge_tau.json"
    put("tau_caught", jt["caught_failed"], a, "{:d}")
    w = J(R / "six-monitors/expected/w1a_summary.json")["g16_set"]; a = "W1-A, .../2026-10-19_w1_screening/w1a_summary.json"
    put("w1_l2", w["l2"]["caught_failed"], a, "{:.0f}"); put("w1_l2_auc", w["l2"]["auroc"], a, "{:.2f}"); put("w1_cos", w["cos"]["caught_failed"], a, "{:.0f}")
    r = J(R / "reap/expected/monitors_v2.json")["primary_50"]; a = "REAP v2, paper-vs-hardware .../reap/expected/monitors_v2.json"
    put("r2_log_c", r["risk_logistic:true"]["caught"], a, "{:.0f}"); put("r2_log_fi", r["risk_logistic:true"]["fi"], a, "{:.0f}")
    put("r2_log_auc", r["risk_logistic:true"]["auroc"], a, "{:.2f}"); put("r2_sh_auc", r["risk_logistic:shuffled"]["auroc"], a, "{:.2f}")
    r1 = J(R / "reap/expected/monitors.json")["primary_50"]
    put("r1_log_auc", r1["risk_logistic"]["auroc"], "REAP v1, .../reap/expected/monitors.json", "{:.2f}")
    put("r2_mlp_c", r["risk_mlp:true"]["caught"], a, "{:.0f}"); put("r2_mlp_fi", r["risk_mlp:true"]["fi"], a, "{:.0f}")
    tr = J(R / "topreward/expected/topreward.json"); a = "WS-085 TOPReward, results/topreward.json"
    ab, ow = tr["armnetbench"], tr["own"]
    put("topr_within", ab["s_succ"]["within"], a); put("topr_lo", ab["s_succ"]["within_ci95"][0], a); put("topr_hi", ab["s_succ"]["within_ci95"][1], a)
    put("topr_pooled", ab["s_succ"]["pooled"], a)
    put("topr_d_lo", ab["delta_within_vs_length_ci95"][0], a, "{:.2f}"); put("topr_d_hi", ab["delta_within_vs_length_ci95"][1], a, "{:.2f}")
    put("topr_cap", ab["s_cap"]["within"], a)
    put("topr_own", ow["s_succ"]["auroc"], a, "{:.2f}"); put("topr_own_lo", ow["s_succ"]["ci95"][0], a, "{:.2f}"); put("topr_own_hi", ow["s_succ"]["ci95"][1], a, "{:.2f}")
    put("topr_own_n", ow["n"], a, "{:d}"); put("topr_own_len", ow["neg_len"]["auroc"], a, "{:.2f}"); put("topr_own_pol", ow["pol_rate"]["auroc"], a, "{:.2f}")
    put("topr_pooled_lo", ab["s_succ"]["pooled_ci95"][0], a); put("topr_pooled_hi", ab["s_succ"]["pooled_ci95"][1], a)
    put("topr_yn_within", ab["s_yn"]["within"], a); put("topr_yn_own", ow["s_yn"]["auroc"], a, "{:.2f}")
    put("topr_own_nt", ow["non_turbovla"]["auroc"], a, "{:.2f}"); put("topr_own_nt_n", ow["non_turbovla"]["n"], a, "{:d}")
    import csv
    lab = [r for r in csv.DictReader(open(R / "topreward/expected/own_rollout_labels.csv")) if r["outcome"] in ("success", "failure")]
    a = "repro/topreward/expected/own_rollout_labels.csv, operator labels of the 69 rollouts"
    put("own_fail", sum(r["outcome"] == "failure" for r in lab), a, "{:d}")
    put("own_turbo_fail", sum(r["outcome"] == "failure" and r["policy"].startswith("turbovla") for r in lab), a, "{:d}")
    cc = J(R / "length-null/expected/counts_ci.json"); a = "Wilson 95 %, results/counts_ci.json"
    for key, name in (("flora_s_ci", "G-flora: successes flagged"), ("w1_l2_ci", "W1-A L2 surprise: failures caught"),
                      ("r2_log_ci", "REAP v2 logistic: failures"), ("g9c3_fp_ci", "G9c-3: false positives")):
        lo, hi = cc[name]["wilson95"]; put(key, f"{100 * lo:.0f}–{100 * hi:.0f} %", a)


def figures():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(exist_ok=True); plt.rcParams.update({"font.size": 8, "figure.dpi": 150})
    L = J(R / "length-null/expected/length_armnetbench.json")
    # 1. ArmnetBench: length vs the two reward models, with 95 % CIs
    f = lambda k: float(N[k])  # noqa: E731
    rows = [("episode length, pooled", f("len_pooled"), f("len_pooled_lo"), f("len_pooled_hi"), "0.3"),
            ("episode length, within policy", f("len_within"), f("len_within_lo"), f("len_within_hi"), "0.3"),
            ("length seen up to 50 % of T, within policy", f("t50_within"), f("t50_lo"), f("t50_hi"), "0.55"),
            ("Robometer-4B zero-shot, pooled", f("rbm_pooled"), f("rbm_lo"), f("rbm_hi"), "0.85"),
            ("TOPReward (Qwen3-VL-8B), within policy", f("topr_within"), f("topr_lo"), f("topr_hi"), "0.95")]
    fig, ax = plt.subplots(figsize=(3.3, 1.75))
    ax.barh(range(5), [r[1] for r in rows], xerr=[[r[1] - r[2] for r in rows], [r[3] - r[1] for r in rows]],
            color=[r[4] for r in rows], edgecolor="black", linewidth=0.4, error_kw={"elinewidth": 0.6, "capsize": 1.5})
    ax.set_yticks(range(5)); ax.set_yticklabels([r[0] for r in rows], fontsize=6); ax.invert_yaxis(); ax.set_xlim(0.5, 1.0)
    for i, r in enumerate(rows):
        ax.text(r[3] + 0.006, i, f"{r[1]:.3f}", va="center", fontsize=6)
    ax.set_xlabel(f"failure AUROC, n = {N['ab_n']}")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "armnetbench.pdf"); fig.savefig(FIG / "armnetbench.png"); plt.close(fig)
    # 2. truncation curve
    ts = sorted(L["b_truncated"], key=float); x = [float(t) * 100 for t in ts]
    fig, ax = plt.subplots(figsize=(3.3, 1.6))
    y = [L["b_truncated"][t]["within_policy"] for t in ts]; lo = [L["b_truncated"][t]["within_policy_ci95"][0] for t in ts]
    hi = [L["b_truncated"][t]["within_policy_ci95"][1] for t in ts]
    ax.plot(x + [100], y + [float(N["len_within"])], marker="o", color="black", lw=1)
    ax.fill_between(x, lo, hi, color="0.8")
    ax.axhline(0.60, ls="--", lw=0.8, color="black"); ax.text(27, 0.615, "reading rule 0.60", fontsize=6)
    ax.set_xlabel("length seen up to (% of longest episode)"); ax.set_ylabel("AUROC within policy"); ax.set_ylim(0.5, 1.0)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "truncation.pdf"); fig.savefig(FIG / "truncation.png"); plt.close(fig)
    # 3. own rollouts: failures caught / 8 vs successes flagged / 42
    pts = [("Flora-27B", int(N["flora_f"]), int(N["flora_s"])), ("Qwen3.5-27B", int(N["q27_f"]), int(N["q27_s"])),
           ("Gemini windows", int(N["tau_caught"]), 1), ("W1 surprise", int(N["w1_l2"]), 2), ("W1 drift", int(N["w1_cos"]), 2),
           ("risk head v2", int(N["r2_log_c"]), int(N["r2_log_fi"])), ("risk MLP v2", int(N["r2_mlp_c"]), int(N["r2_mlp_fi"]))]
    fig, ax = plt.subplots(figsize=(3.3, 2.0))
    ax.add_patch(matplotlib.patches.Rectangle((-0.5, 5), 2.9, 3.6, color="0.9", zorder=0)); ax.text(0, 8.25, "monitor bar", fontsize=6)
    off = {"Gemini windows": (-4, 6), "W1 drift": (4, -9)}
    for lab, f, s in pts:
        judge = lab in ("Flora-27B", "Qwen3.5-27B")  # judges at rest, in-sample operating point: not the monitor bar
        ax.plot(s, f, "s" if judge else "o", color="black", ms=3.5 if judge else 3, mfc="white" if judge else "black")
        ax.annotate(lab, (s, f), xytext=off.get(lab, (3, -2)), textcoords="offset points", fontsize=5.5)
    ax.set_xlabel("successes flagged (of 42)"); ax.set_ylabel("failures caught (of 8)"); ax.set_xlim(-0.5, 16); ax.set_ylim(-0.5, 8.6)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    fig.tight_layout(); fig.savefig(FIG / "own_monitors.pdf"); fig.savefig(FIG / "own_monitors.png"); plt.close(fig)


def render(src, dst):
    t = (HERE / src).read_text(); missing = set(re.findall(r"\{\{(\w+)\}\}", t)) - N.keys()
    assert not missing, f"{src}: placeholders without a value: {sorted(missing)}"
    (HERE / dst).write_text(re.sub(r"\{\{(\w+)\}\}", lambda m: N[m.group(1)], t))


def main():
    collect()
    (HERE / "numbers.json").write_text(json.dumps({k: {"value": N[k], "anchor": A[k]} for k in sorted(N)}, indent=1))
    figures(); render("DRAFT_4p.src.md", "DRAFT_4p.md")
    if (HERE / "main.src.tex").exists():
        render("main.src.tex", "main.tex")
    print(f"{len(N)} numbers, 3 figures, rendered")


if __name__ == "__main__":
    main()
