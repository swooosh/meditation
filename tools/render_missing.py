#!/usr/bin/env python3
"""Render protocols that are missing *_master.wav outputs."""
import argparse
import subprocess
import sys
from pathlib import Path

from status_report import build_status


def main():
    parser = argparse.ArgumentParser(description="Render missing protocol masters.")
    parser.add_argument("--max", type=int, default=0, help="Max number of protocols to render (0 = all).")
    parser.add_argument("--max-minutes", type=int, default=0, help="Only render protocols with duration <= this value.")
    parser.add_argument("--timeout", type=int, default=3600, help="Per-render timeout seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Show queue without rendering.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    renderer = root / "tools" / "render_protocol.py"
    rows = build_status(root)

    queue = [r for r in rows if not r["render_exists"]]
    queue.sort(key=lambda r: (r["spec_duration_m"], r["id"]))
    if args.max_minutes > 0:
        queue = [r for r in queue if r["spec_duration_m"] <= args.max_minutes]
    if args.max > 0:
        queue = queue[: args.max]

    print(f"Queued protocols: {len(queue)}")
    for r in queue:
        print(f"- {r['id']} ({r['spec_duration_m']}m)")

    if args.dry_run or not queue:
        return

    ok = 0
    failed = 0
    for r in queue:
        spec_path = Path(r["spec_path"])
        out_dir = spec_path.parents[1] / "renders"
        out_dir.mkdir(parents=True, exist_ok=True)
        cmd = [sys.executable, str(renderer), str(spec_path), "--out_dir", str(out_dir)]
        print(f"\nRendering {r['id']}...")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            print(f"TIMEOUT: {r['id']} after {args.timeout}s")
            failed += 1
            continue

        if proc.returncode == 0:
            ok += 1
            tail = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()][-2:]
            for ln in tail:
                print(ln)
        else:
            failed += 1
            print(f"FAILED: {r['id']}")
            if proc.stderr.strip():
                print(proc.stderr.strip().splitlines()[-1])

    print(f"\nDone. ok={ok} failed={failed}")


if __name__ == "__main__":
    main()
