#!/usr/bin/env bash
# G9a-FT on vast.ai (G9A_FT_PROTOCOL.md; fine-tune of Robometer, tiled input). Derived from vast_g9a_ab.sh; `--ft` is the default here.
# G9a-AB on vast.ai (G9A_AB_PROTOCOL.md), launched from the Jetson or the Mac. Needs the vastai CLI with the API key.
#   projects/vla-jepa-world-model/robometer/vast_g9a_ab.sh [--dry-run] [--max-min N] [--offer ID] [--debug]
#   --hours H: run cap in hours. HF_TOKEN_FILE=<file>: write token copied to the instance (600), results pushed to the
#   private dataset ravediamond/g9a-ab-results every 20 min and at the end (then immediate self-destroy).
#   --debug: remote_debug.sh (env + model + one video file, then idle for SSH work), 75 min cap
#   --rescore: remote_g9a_ab_rescore.sh (the 462 OOM episodes, top view, GPU >= 48 GB, 39 video files only)
#   --own: remote_g9a_own.sh (G9A_OWN_PROTOCOL.md; our bowls rollouts; M1_TAR=<tar of the M1 sessions> uploaded)
#   --g9b: remote_g9b.sh (G9B_PROTOCOL.md; LoRA folds; GPU >= 48 GB; g9b_*.py + g9b_folds.json uploaded)
#   --cap USD: refuse offers whose worst case (run cap + grace at the hourly price + download) exceeds USD
# Cost safety: wm_train/vast/bootstrap.sh on the instance (hard deadline max + grace, self-destroy), a local
# `vastai destroy` timer, on-demand offers only, and the instance is destroyed right after the verified fetch.
# SSH: a dedicated key (~/.ssh/id_ed25519_vast) attached to this instance only, not to the account.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd); VAST=$(dirname "$HERE")/wm_train/vast
MAX_MIN=200; GRACE=20; DRY=0; OFFER=""; REMOTE=remote_g9a_ft.sh; LABEL=g9a-ft; KEY=$HOME/.ssh/id_ed25519_vast; DISK=130
GPU_RAM=46; DOWNLOAD_GB=38; CAP=""  # 70 GB = 40 GB videos + 9 GB model + ~20 GB env
while [ $# -gt 0 ]; do case $1 in --dry-run) DRY=1; shift;; --max-min) MAX_MIN=$2; shift 2;; --offer) OFFER=$2; shift 2;; --hours) MAX_MIN=$(( $2 * 60 )); shift 2;; --debug) REMOTE=remote_debug.sh; LABEL=g9a-ab-debug; MAX_MIN=75; shift;; --rescore) REMOTE=remote_g9a_ab_rescore.sh; LABEL=g9a-ab-rescore; GPU_RAM=46; DISK=80; DOWNLOAD_GB=36; shift;; --g9b) REMOTE=remote_g9b.sh; LABEL=g9b; GPU_RAM=46; DISK=80; DOWNLOAD_GB=35; shift;; --own) REMOTE=remote_g9a_own.sh; LABEL=g9a-own; GPU_RAM=46; DISK=60; DOWNLOAD_GB=25; shift;; --cap) CAP=$2; shift 2;; *) echo "unknown $1" >&2; exit 2;; esac; done
QUERY="num_gpus=1 gpu_ram>=$GPU_RAM compute_cap>=800 cpu_ram>=32 cpu_cores_effective>=8 reliability>0.98 disk_space>=$DISK inet_down>=500 cuda_vers>=12.8 verified=true rentable=true"
read -r OFFER PRICE GPU JOBCAP <<< "$(vastai search offers "$QUERY" -d --storage $DISK -o dph_total --raw | python3 -c "
import json, sys
offers = [o for o in json.load(sys.stdin) if not o['gpu_name'].startswith('CMP') and not str(o.get('geolocation', '')).endswith('CN')]
cost = lambda o: ($MAX_MIN + $GRACE) / 60 * o['dph_total'] + $DOWNLOAD_GB * o.get('inet_down_cost', 0)
offers.sort(key=cost); want = '$OFFER'
o = next((o for o in offers if str(o['id']) == want), None) if want else (offers[0] if offers else None)
print(o['id'], round(o['dph_total'], 4), o['gpu_name'].replace(' ', '_'), round(cost(o), 3)) if o else print('none 0 none 0')")"
[ "$OFFER" != none ] || { echo "no matching offer" >&2; exit 1; }
echo "offer $OFFER: $GPU at \$$PRICE/h | <= $MAX_MIN + $GRACE min + ${DOWNLOAD_GB} GB download -> at most ~\$$JOBCAP"
if [ -n "$CAP" ] && ! python3 -c "import sys; sys.exit(0 if $JOBCAP <= $CAP else 1)"; then
  echo "worst case \$$JOBCAP is over the cap \$$CAP: not launching" >&2; exit 1; fi
[ $DRY = 1 ] && exit 0
ID=$(vastai create instance "$OFFER" --image nvidia/cuda:12.8.1-base-ubuntu24.04 --disk $DISK --ssh --direct --cancel-unavail \
  --label $LABEL --env "-e WM_MAX_MIN=$MAX_MIN -e WM_GRACE_MIN=$GRACE -e PRICE_PH=$PRICE -e CAP_USD=13" --onstart-cmd "$(cat "$VAST/bootstrap.sh")" --raw |
  python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('success'), d; print(d['new_contract'])")
echo "instance $ID (destroy by hand: vastai destroy instance $ID -y)"; echo "$ID" > "$HERE/.last_instance"
nohup bash -c "sleep $(( (MAX_MIN + GRACE + 10) * 60 )); vastai destroy instance $ID -y" > /dev/null 2>&1 &
vastai attach ssh "$ID" "$(cat "$KEY.pub")" > /dev/null
for _ in $(seq 120); do ST=$(vastai show instance "$ID" --raw | python3 -c "import json,sys; print(json.load(sys.stdin).get('actual_status'))" || true); [ "$ST" = running ] && break; sleep 10; done
[ "$ST" = running ] || { echo "not running after 20 min: destroying" >&2; vastai destroy instance "$ID" -y; exit 1; }
SSH_URL=$(vastai ssh-url "$ID"); HOST=${SSH_URL#ssh://}; PORT=${HOST##*:}; HOST=${HOST%:*}
SSHO="-i $KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=20 -p $PORT"
OK=0; for _ in $(seq 30); do ssh $SSHO "$HOST" true 2> /dev/null && { OK=1; break; }; sleep 10; done
[ $OK = 1 ] || { echo "ssh never worked: destroying" >&2; vastai destroy instance "$ID" -y; exit 1; }
scp -q -i "$KEY" -o IdentitiesOnly=yes -P "$PORT" "$HERE/score_robometer_tiled.py" "$HERE/episodes_ft.txt" "$HERE/armnetbench_episodes.csv" "$HOST:/root/wm/"
[ $REMOTE = remote_g9b.sh ] && scp -q -i "$KEY" -o IdentitiesOnly=yes -P "$PORT" "$HERE"/g9b_score.py "$HERE"/g9b_preprocess.py "$HERE"/g9b_cuts.py "$HERE"/g9b_folds.json "$HOST:/root/wm/"
[ $REMOTE = remote_g9a_own.sh ] && scp -q -i "$KEY" -o IdentitiesOnly=yes -P "$PORT" "${M1_TAR:?M1_TAR not set}" "$HOST:/root/wm/m1.tar"
[ $REMOTE = remote_g9a_ab_rescore.sh ] && scp -q -i "$KEY" -o IdentitiesOnly=yes -P "$PORT" "$HERE/rescore_episodes.txt" "$HOST:/root/wm/"
if [ -n "${HF_TOKEN_FILE:-}" ]; then ssh $SSHO "$HOST" "umask 077 && cat > /root/wm/hf_token" < "$HF_TOKEN_FILE"; fi
scp -q -i "$KEY" -o IdentitiesOnly=yes -P "$PORT" "$HERE/$REMOTE" "$HOST:/root/wm/run_remote.sh"
ssh $SSHO "$HOST" "touch /root/wm/READY"
echo "started. follow: ssh $SSHO $HOST tail -f /root/wm/run.log"
echo "$SSHO $HOST" > "$HERE/.last_ssh"
