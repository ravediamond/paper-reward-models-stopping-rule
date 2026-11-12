"""Fetch the ReAP rebuild result (Stage 1 detector + Stage 2 predictor, rebuilt from the ReAP paper; WS-217) from
ravediamond/paper-register-reproducibility at a pinned commit, byte for byte, into expected/. The run itself lives in
that repository (repro/variants/reap: extract.py, reap_stage.py, PROTOCOL.md, RESULT.md); this folder only carries
its result file so the paper's numbers have an anchor here. Usage: python3 fetch.py [path to a local clone]."""
import subprocess, sys, urllib.request
from pathlib import Path

REPO = "ravediamond/paper-register-reproducibility"
COMMIT = "b41d79575265f3d4efcb8e05e0dbf43158c0765c"
FILES = ["repro/variants/reap/expected/results.json", "repro/variants/reap/RESULT.md", "repro/variants/reap/PROTOCOL.md"]
HERE = Path(__file__).resolve().parent


def get(path, clone):
    if clone:
        return subprocess.run(["git", "-C", clone, "show", f"{COMMIT}:{path}"], check=True, capture_output=True).stdout
    with urllib.request.urlopen(f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/{path}") as r:
        return r.read()


def main():
    clone = sys.argv[1] if len(sys.argv) > 1 else None
    for path in FILES:
        name = Path(path).name
        dst = HERE / ("expected" if name.endswith(".json") else "upstream") / name
        dst.parent.mkdir(exist_ok=True)
        dst.write_bytes(get(path, clone))
        print(f"{dst.relative_to(HERE)} <- {REPO}@{COMMIT[:7]}:{path}")


if __name__ == "__main__":
    main()
