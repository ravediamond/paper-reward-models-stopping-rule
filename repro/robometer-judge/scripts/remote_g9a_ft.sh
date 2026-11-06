#!/bin/bash
# G9a-FT (G9A_FT_PROTOCOL.md). On the vast.ai instance (uploaded as /root/wm/run_remote.sh, started by wm_train/vast/bootstrap.sh under its hard
# deadline). Installs the pinned robometer code, downloads the pinned model and only the needed camera videos
# (public data, anonymous), scores per G9A_AB_PROTOCOL.md, writes everything under /root/wm/out/.
set -uo pipefail
W=/root/wm; O=$W/out; mkdir -p $O; cd $W
RBM_COMMIT=352d160389daa964788de1ec933d1925f3a6de4f
FT_REV=b8098db5681317f48b5f286767e5fa01fd0abad5; TILED_REV=384d04fcfbe77a373b77c059853d27b4c5fef74f
AB=armnet/armnetbench_v01_lerobot_so101; AB_REV=1db69c82b589c7172ee31a6b8f7ef58d1fc2c663
K1=k1000dai/so101_self_rollout; K1_REV=657727f3326ca02fc51d22ebcad8220cc366706e
t0=$(date +%s); stamp() { echo "$1=$(( $(date +%s) - t0 ))" >> $O/timings.env; echo "$(date -Is) $1"; }
( while true; do nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader >> $O/gpu.log; sleep 30; done ) &

apt-get update -q && apt-get install -y -q --no-install-recommends git curl ca-certificates ffmpeg > /dev/null
curl -LsSf https://astral.sh/uv/install.sh | sh > /dev/null; export PATH=$HOME/.local/bin:$PATH
git clone -q https://github.com/robometer/robometer rbm && git -C rbm checkout -q $RBM_COMMIT
# torchao pinned: newer torchao needs torch > 2.8 (ScalingType import error, 2026-10-14)
# unsloth pinned to the releases current at the robometer commit (2026-08-13): 2026.10.x returns hidden_states=None
cd rbm && uv sync --extra robometer -q && uv pip install -q av "torchao==0.13.0" "unsloth==2026.8.16" "unsloth_zoo==2026.8.11" && cd $W
stamp env_ready
PY="$W/rbm/.venv/bin/python"
export HF_HUB_ENABLE_HF_TRANSFER=1 HF_HUB_DISABLE_IMPLICIT_TOKEN=1
# Hub access for the fine-tune and the tiled dataset is anonymous (public); no token on the environment
$PY - <<PYEOF
from huggingface_hub import snapshot_download
snapshot_download("jesbu1/robometer-4b-fft-armnet-tiled", revision="$FT_REV", local_dir="$W/model", token=False, allow_patterns=["config.json", "config.yaml", "model.safetensors", "README.md", "metrics.json"])
snapshot_download("jesbu1/armnetbench_v01_tiled_so101", repo_type="dataset", revision="$TILED_REV", local_dir="$W/tiled", token=False)
PYEOF
stamp data_ready; df -h /root | tail -1
export RBM_MODEL=$W/model
push() {
  [ -s $W/hf_token ] || return 0   # no write token on the instance by default: results are fetched over ssh
  HF_TOKEN_FILE=$W/hf_token $PY - "$1" <<'PUSH'
import os, sys
from huggingface_hub import HfApi
api = HfApi(token=open(os.environ["HF_TOKEN_FILE"]).read().strip())
api.create_repo("ravediamond/g9a-ab-results", repo_type="dataset", private=True, exist_ok=True)
api.upload_folder(repo_id="ravediamond/g9a-ab-results", repo_type="dataset", folder_path="/root/wm/out", path_in_repo="ft", commit_message=sys.argv[1])
PUSH
}
( while true; do sleep 1200; push "periodic $(date -u +%FT%TZ)" > /dev/null 2>&1 || true; done ) &
PUSHER=$!
cd $W/rbm
# protocol checks 1 and 2: two episodes, then stop if they did not score
$PY $W/score_robometer_tiled.py --tiled-root $W/tiled --meta-csv $W/armnetbench_episodes.csv --episodes $W/episodes_ft.txt --out $O/ft_check.jsonl --check-only 2>&1 | grep -v -i warn | tee $O/check.log
if ! grep -q '"p_succ": 0\|"p_succ": 1\|"p_succ": [0-9]' $O/check.log || grep -q '"error": "' $O/check.log; then echo "check failed" > $O/CHECK_FAILED; push "check failed"; touch $W/HF_OK; exit 1; fi
stamp checks
$PY $W/score_robometer_tiled.py --tiled-root $W/tiled --meta-csv $W/armnetbench_episodes.csv --episodes $W/episodes_ft.txt --out $O/ft_rows.jsonl 2>&1 | grep -v -i warn | tee $O/score_ft.log; stamp ft_scored
nvidia-smi --query-gpu=name --format=csv,noheader > $O/gpu_name.txt
echo ok > $O/DONE
(cd $O && find . -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > SHA256SUMS); touch $O/ANALYZED
kill $PUSHER 2>/dev/null || true
[ -s $W/hf_token ] || touch $W/HF_OK
[ -s $W/hf_token ] && push "final $(date -u +%FT%TZ)" && HF_TOKEN_FILE=$W/hf_token $PY - <<'VERIFY' && touch $W/HF_OK
import os, hashlib
from huggingface_hub import HfApi
api = HfApi(token=open(os.environ["HF_TOKEN_FILE"]).read().strip())
hub = {f.path: f for f in api.list_repo_tree("ravediamond/g9a-ab-results", repo_type="dataset", recursive=True) if hasattr(f, "size")}
bad = 0
for root, _, files in os.walk("/root/wm/out"):
    for n in files:
        p = os.path.join(root, n); k = "ft/" + os.path.relpath(p, "/root/wm/out"); f = hub.get(k)
        data = open(p, "rb").read()
        if f is None or f.size != len(data) or (f.lfs and f.lfs.sha256 != hashlib.sha256(data).hexdigest()):
            bad += 1; print("mismatch", k)
print("hub verify, mismatches:", bad); raise SystemExit(1 if bad else 0)
VERIFY
