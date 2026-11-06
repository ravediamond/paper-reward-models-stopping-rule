#!/usr/bin/env python3
"""G9a-FT (G9A_FT_PROTOCOL.md): score the tiled ArmnetBench trajectories with the released fine-tune. Same code path as score_robometer.py (1 fps frames, last frame included, one forward pass, OOM retries); the input is the tiled trajectory.mp4 of jesbu1/armnetbench_v01_tiled_so101 and the model is the local snapshot RBM_MODEL.

Original docstring of score_robometer.py follows.

Score LeRobot v3.0 episodes with Robometer-4B (G9a-AB protocol, robometer/G9A_AB_PROTOCOL.md).

Runs inside the robometer repo's env (uv sync) on a GPU box. Per episode: frames of one camera sampled at 1 fps over
the episode's segment of the concatenated video (last frame always included), the episode's task string verbatim,
one forward pass; writes one JSON line per episode (per-frame progress and success probability) to --out, appending
and skipping episodes already there (restartable).

  python score_robometer.py --root DATASET_DIR --view top --out scores_top.jsonl [--only-rollouts] [--limit N]
      [--episodes FILE] [--max-frames N] [--fixed-frames N] [--short-edge PX]

--fixed-frames N (G9b / G9a-own input B): exactly N frames linspace over the episode, first and last included, instead
of 1 fps. --short-edge PX: resize every frame so its shortest edge is PX (G9b trains on 240 px RBM videos).

G9a-AB re-score (2026-10-16): the first run ran out of CUDA memory and never recovered (462 episodes lost). Now: after
an OOM the batch is dropped, memory freed and the episode retried at full length, then once more uniformly subsampled
to --oom-frames (last frame kept); episodes longer than --max-frames are uniformly subsampled up front. Every record
says how many frames were decoded / scored and how many attempts it took; episodes that still fail keep "error".
Set PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True before starting (remote script does).
"""
import argparse, gc, glob, json, os, queue, threading, time, traceback

import av
import numpy as np
import pandas as pd
import torch

from robometer.data.dataset_types import ProgressSample, Trajectory
from robometer.evals.eval_server import compute_batch_outputs
from robometer.utils.save import load_model_from_hf
from robometer.utils.setup_utils import setup_batch_collator

# local snapshot of robometer/Robometer-4B @ beef63bc914c5c189329d49c6d712d96d632aa34 (remote_g9a_ab.sh downloads it)
MODEL = os.environ.get("RBM_MODEL", "robometer/Robometer-4B")


def episodes(root):
    e = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f"{root}/meta/episodes/*/*.parquet"))])
    return e.sort_values("episode_index").reset_index(drop=True)


def sample_times(t0, t1, fps):
    """1 fps over [t0, t1), plus the episode's last frame."""
    last = t1 - 1.0 / fps
    ts = list(np.arange(t0, last, 1.0))
    if not ts or last - ts[-1] > 1e-6:
        ts.append(last)
    return ts


def subsample(frames, n):
    """Uniformly subsample to n frames, first and last kept."""
    if n <= 0 or len(frames) <= n:
        return frames
    return frames[np.unique(np.round(np.linspace(0, len(frames) - 1, n)).astype(int))]


def free_cuda():
    gc.collect()
    torch.cuda.empty_cache()


def fixed_times(t0, t1, fps, n):
    """Exactly n timestamps linspace over [t0, last frame], first and last included."""
    return list(np.linspace(t0, t1 - 1.0 / fps, n))


def decode_at(path, times, fps, short_edge=0):
    """Decode the frames nearest to the given timestamps (seconds); returns uint8 (T, H, W, 3)."""
    out = []
    with av.open(path) as c:
        s = c.streams.video[0]
        s.thread_type = "AUTO"
        for t in times:
            target = round(t * fps)
            c.seek(int(max(t - 0.5, 0) / s.time_base), stream=s, backward=True)
            got = None
            for fr in c.decode(s):
                k = round(float(fr.pts * s.time_base) * fps)
                if k >= target:
                    if short_edge:
                        k = short_edge / min(fr.width, fr.height)
                        fr = fr.reformat(width=round(fr.width * k / 2) * 2, height=round(fr.height * k / 2) * 2)
                    got = fr.to_ndarray(format="rgb24")
                    break
            if got is None:
                raise RuntimeError(f"frame at {t:.3f}s not found in {path}")
            out.append(got)
    return np.stack(out)


def video_info(path):
    with av.open(path) as c:
        st = c.streams.video[0]; fps = float(st.average_rate)
        n = st.frames or int(round(float(st.duration * st.time_base) * fps))
    return fps, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tiled-root", required=True, help="snapshot of jesbu1/armnetbench_v01_tiled_so101 (parquet + videos)")
    ap.add_argument("--meta-csv", required=True, help="armnetbench_episodes.csv: episode_index, task, policy_type, success_class, length")
    ap.add_argument("--episodes", required=True, help="file with one episode_index per line: the 2,047 policy rollouts")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--max-frames", type=int, default=0)
    ap.add_argument("--oom-frames", type=int, default=40)
    ap.add_argument("--check-only", action="store_true", help="checks 1 and 2 of the protocol on two episodes, then stop")
    a = ap.parse_args()

    idx = pd.read_parquet(glob.glob(f"{a.tiled_root}/**/train-*.parquet", recursive=True)[0])
    idx["episode_index"] = idx.frames.str.extract(r"trajectory_(\d+)")[0].astype(int)
    meta = pd.read_csv(a.meta_csv).set_index("episode_index")
    want = [int(l) for l in open(a.episodes) if l.strip()]
    e = idx[idx.episode_index.isin(want)].sort_values("episode_index").reset_index(drop=True)
    done = set()
    if os.path.exists(a.out):
        done = {json.loads(l)["episode_index"] for l in open(a.out) if l.strip()}
    e = e[~e.episode_index.isin(done)]
    if a.limit or a.check_only:
        e = e.head(a.limit or 2)
    print(f"{len(e)} episodes to score ({len(done)} already done)", flush=True)

    dev = torch.device("cuda")
    cfg, tok, proc, model = load_model_from_hf(model_path=MODEL, device=dev)
    model.eval()
    collate = setup_batch_collator(proc, tok, cfg, is_eval=True)
    lc = getattr(cfg, "loss", None)

    def forward(frames, task, idx_):
        traj = Trajectory(frames=frames, frames_shape=tuple(frames.shape), task=task, id=str(idx_),
                          metadata={"subsequence_length": int(frames.shape[0])}, video_embeddings=None)
        batch = collate([ProgressSample(trajectory=traj, sample_type="progress")])
        inp = {k: (v.to(dev) if hasattr(v, "to") else v) for k, v in batch["progress_inputs"].items()}
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):  # model is bf16, inputs float32
            res = compute_batch_outputs(model, tok, inp, sample_type="progress", is_discrete_mode=discrete, num_bins=bins)
        prog = np.asarray(res.get("progress_pred", [[]])[0], dtype=float)
        succ = np.asarray((res.get("outputs_success") or {}).get("success_probs", [[]])[0], dtype=float)
        return prog, succ

    discrete = getattr(lc, "progress_loss_type", "l2").lower() == "discrete" if lc else False
    bins = getattr(lc, "progress_discrete_bins", None) or getattr(cfg.model, "progress_discrete_bins", 10)
    q = queue.Queue(maxsize=8)

    def producer():
        for _, r in e.iterrows():
            try:
                path = f"{a.tiled_root}/{r.frames}"
                fps, nfr = video_info(path)
                ts = [k / fps for k in range(nfr)]  # deviation 2: every frame of the 64-frame tiled video
                q.put((r, decode_at(path, ts, fps), None))
            except Exception as ex:
                q.put((r, None, repr(ex)))
        q.put(None)

    threading.Thread(target=producer, daemon=True).start()
    t_start = time.time(); n = 0; n_fail = 0
    with open(a.out, "a") as f:
        while (item := q.get()) is not None:
            r, frames, err = item
            i = int(r.episode_index); m = meta.loc[i]
            rec = {"episode_index": i, "view": "tiled", "task": r.task, "length": int(m["length"]), "policy_type": m["policy_type"],
                   "success_class": m["success_class"], "quality_label": r.quality_label, "model": "jesbu1/robometer-4b-fft-armnet-tiled"}
            if err is None:
                rec["n_frames_decoded"] = int(frames.shape[0]); rec["tile_hw"] = list(frames.shape[1:3])
                frames = subsample(frames, a.max_frames)
                plan = [frames, frames, subsample(frames, a.oom_frames)]
                for attempt, fr in enumerate(plan, 1):
                    try:
                        fr8 = subsample(fr, 8)  # deviation 3: primary input = 8 frames spread uniformly (the training subsequence length)
                        prog, succ = forward(fr8, r.task, i)
                        rec.update(n_frames=int(fr8.shape[0]), frame_hw=list(fr8.shape[1:3]), attempts=attempt,
                                   progress=[round(x, 4) for x in prog.tolist()], success_prob=[round(x, 4) for x in succ.tolist()],
                                   p_succ=float(succ[-1]) if succ.size else None, last_progress=float(prog[-1]) if prog.size else None)
                        err = None
                        if i % 14 == 0:  # descriptive: all 64 frames on every 14th episode
                            try:
                                p64, s64 = forward(frames, r.task, i)
                                rec.update(n_frames_64=int(frames.shape[0]), p_succ_64=float(s64[-1]) if s64.size else None, last_progress_64=float(p64[-1]) if p64.size else None)
                            except torch.OutOfMemoryError:
                                rec["p_succ_64_error"] = "OOM"
                        break
                    except torch.OutOfMemoryError as ex:
                        err = repr(ex); print(f"OOM episode {i} attempt {attempt} ({fr.shape[0]} frames), freeing memory", flush=True)
                    except Exception as ex:
                        traceback.print_exc(); err = repr(ex)
                        break
                    finally:
                        free_cuda()
            if err is not None:
                rec["error"] = err[:500]; n_fail += 1; print(f"FAILED episode {i}: {err[:200]}", flush=True)
            f.write(json.dumps(rec) + "\n"); f.flush(); n += 1
            if a.check_only:
                print("CHECK", json.dumps({k: rec.get(k) for k in ("episode_index", "tile_hw", "n_frames_decoded", "n_frames", "p_succ", "last_progress", "error")}), flush=True)
            if n % 50 == 0 or n == 10:
                el = time.time() - t_start; print(f"{n}/{len(e)} episodes, {el / n:.2f} s/episode, eta {(len(e) - n) * el / n / 60:.1f} min", flush=True)
    print(f"done: {n} episodes in {(time.time() - t_start) / 60:.1f} min, {n_fail} failing", flush=True)


if __name__ == "__main__":
    main()
