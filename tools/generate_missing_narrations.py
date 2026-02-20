#!/usr/bin/env python3
"""Generate missing coaching narration files from protocol specs."""
from pathlib import Path
import argparse

import yaml

ROOT = Path(__file__).resolve().parents[1]


def mmss(seconds):
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def cue_text(phase_name, idx, total):
    if idx == 0:
        return f"Settle in. Enter {phase_name.lower()}."
    if idx == total - 1:
        return f"Complete {phase_name.lower()} and prepare to close."
    return f"Continue with {phase_name.lower()}. Stay steady."


def generate(spec):
    pid = spec["id"]
    title = str(spec.get("title", pid)).replace("—", "-")
    family = str(spec.get("family", "UNKNOWN"))
    duration_m = int(round(int(spec.get("duration_s", 0)) / 60))
    phases = spec.get("phases", [])

    lines = [
        f"# {pid}: {title} - Coaching Narration",
        "",
        "## Introduction (Record this first)",
        "",
        f"Welcome to {pid}, a {duration_m}-minute {family} protocol.",
        "",
        "**Goal:** Follow phase cues while maintaining steady breath and awareness.",
        "",
        f"**Process:** {len(phases)} phases from start to completion. Keep attention on the current cue and transition smoothly.",
        "",
        "Let's begin.",
        "",
        "---",
        "",
    ]

    for i, ph in enumerate(phases):
        name = str(ph.get("name", f"Phase {i+1}"))
        start_s = int(ph.get("start_s", 0))
        end_s = int(ph.get("end_s", start_s))
        lines.append(f"## Phase {i+1}: {name} ({mmss(start_s)}-{mmss(end_s)})")
        lines.append("")
        lines.append(f"**{mmss(start_s)}** {cue_text(name, 0, 3)}")
        mid = start_s + max(1, (end_s - start_s) // 2)
        lines.append("")
        lines.append(f"**{mmss(mid)}** {cue_text(name, 1, 3)}")
        lines.append("")
        lines.append(f"**{mmss(end_s)}** {cue_text(name, 2, 3)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate missing narration markdown files.")
    parser.add_argument("--ids", nargs="*", help="Protocol IDs to generate. If omitted, generate all missing.")
    args = parser.parse_args()

    specs = {}
    for p in ROOT.glob("protocols/*/specs/*.yaml"):
        with p.open() as f:
            spec = yaml.safe_load(f)
        specs[spec["id"]] = (p, spec)

    have_narr = set()
    for p in ROOT.glob("protocols/*/narration/*.md"):
        stem = p.name.split("_", 1)[0].split(".", 1)[0]
        have_narr.add(stem)

    target_ids = args.ids if args.ids else sorted(set(specs) - have_narr)
    if not target_ids:
        print("No missing narration files.")
        return

    for pid in target_ids:
        if pid not in specs:
            print(f"Skipping unknown id: {pid}")
            continue
        spec_path, spec = specs[pid]
        family_dir = spec_path.parents[1]
        out_dir = family_dir / "narration"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{pid}_coaching.md"
        if out_path.exists():
            print(f"Exists, skipping: {out_path}")
            continue
        out_path.write_text(generate(spec))
        print(f"Created: {out_path}")


if __name__ == "__main__":
    main()
