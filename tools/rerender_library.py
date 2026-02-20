#!/usr/bin/env python3
"""Re-render protocol masters with upgraded engine + strict QC."""
import argparse
import subprocess
import sys
from pathlib import Path


def discover_specs(root: Path):
    specs = []
    for spec_path in sorted(root.glob("protocols/*/specs/*.yaml")):
        family = spec_path.parts[-3]
        name = spec_path.name
        minutes = 0
        if "_" in name and name.endswith("m.yaml"):
            try:
                minutes = int(name.rsplit("_", 1)[1].replace("m.yaml", ""))
            except Exception:
                minutes = 0
        specs.append((minutes, family, spec_path))
    specs.sort(key=lambda x: (x[0], x[1], x[2].name))
    return specs


def main():
    parser = argparse.ArgumentParser(description="Re-render protocol library with strict QC.")
    parser.add_argument("--max-minutes", type=int, default=0, help="Only render specs <= this duration in minutes.")
    parser.add_argument("--max", type=int, default=0, help="Maximum number of specs to render (0 = all).")
    parser.add_argument("--family", default="", help="Filter by family, e.g. PERF.")
    parser.add_argument("--timeout", type=int, default=7200, help="Per-render timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Print queue only.")
    parser.add_argument("--stop-on-fail", action="store_true", help="Stop immediately on first failure.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    renderer = root / "tools" / "render_protocol.py"
    tools_dir = root / "tools"
    specs = discover_specs(root)

    if args.family:
        specs = [s for s in specs if s[1] == args.family]
    if args.max_minutes > 0:
        specs = [s for s in specs if s[0] <= args.max_minutes]
    if args.max > 0:
        specs = specs[: args.max]

    print(f"Queue size: {len(specs)}")
    for minutes, family, spec_path in specs:
        print(f"- {family}/{spec_path.name} ({minutes}m)")
    if args.dry_run:
        return

    ok = 0
    failed = 0
    for minutes, family, spec_path in specs:
        out_dir = root / "protocols" / family / "renders"
        cmd = [
            sys.executable,
            str(renderer),
            str(spec_path),
            "--out_dir",
            str(out_dir),
            "--strict-qc",
        ]
        print(f"\nRendering {family}/{spec_path.name} ...")
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
        except subprocess.TimeoutExpired:
            failed += 1
            print(f"TIMEOUT after {args.timeout}s")
            if args.stop_on_fail:
                break
            continue

        if proc.returncode == 0:
            ok += 1
            lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]
            for ln in lines[-3:]:
                print(ln)
        else:
            failed += 1
            print(f"FAILED (exit {proc.returncode})")
            if proc.stdout.strip():
                print(proc.stdout.strip().splitlines()[-1])
            if proc.stderr.strip():
                print(proc.stderr.strip().splitlines()[-1])
            if args.stop_on_fail:
                break

    print(f"\nRender summary: ok={ok} failed={failed}")

    print("\nRefreshing QC artifacts + website status manifest ...")
    subprocess.run([sys.executable, str(tools_dir / "generate_qc_artifacts.py"), "--overwrite"], check=False)
    subprocess.run([sys.executable, str(tools_dir / "update_render_status.py")], check=False)
    subprocess.run([sys.executable, str(tools_dir / "release_gate.py")], check=False)


if __name__ == "__main__":
    main()
