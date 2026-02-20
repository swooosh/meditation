#!/usr/bin/env python3
"""Validate narration scripts for ordering, timing bounds, and phase coverage."""
import argparse
import re
from pathlib import Path

import yaml


TIME_PATTERNS = [
    re.compile(r"^\s*(?:[-*]\s*)?\[?(\d{1,2}):(\d{2})\]?\s*[-:]\s+", re.IGNORECASE),
    re.compile(r"^\s*(?:[-*]\s*)?t=(\d+):(\d{2})\s+", re.IGNORECASE),
]


def parse_narration_times(path: Path):
    times = []
    lines = path.read_text().splitlines()
    for idx, line in enumerate(lines, start=1):
        for pat in TIME_PATTERNS:
            m = pat.search(line)
            if m:
                mm = int(m.group(1))
                ss = int(m.group(2))
                times.append((mm * 60 + ss, idx, line.strip()))
                break
    return times


def find_narration_path(root: Path, protocol_id: str, family: str):
    candidates = [
        root / "protocols" / family / "narration" / f"{protocol_id}_coaching.md",
        root / "protocols" / family / "narration" / f"{protocol_id}_lab.md",
    ]
    # fallback glob for variants like PERF-01_12m_coaching.md or SLEEP-01_30m_lab.md
    if not any(c.exists() for c in candidates):
        matches = sorted((root / "protocols" / family / "narration").glob(f"{protocol_id}_*coaching.md"))
        if matches:
            return matches[0]
        matches = sorted((root / "protocols" / family / "narration").glob(f"{protocol_id}_*lab.md"))
        if matches:
            return matches[0]
    for c in candidates:
        if c.exists():
            return c
    return None


def validate_one(root: Path, spec_path: Path):
    spec = yaml.safe_load(spec_path.read_text())
    pid = spec["id"]
    family = spec["family"]
    phases = spec.get("phases", [])
    duration_s = int(spec.get("duration_s", 0))
    narration_path = find_narration_path(root, pid, family)

    errors = []
    warnings = []
    if narration_path is None:
        errors.append("missing narration file")
        return pid, family, errors, warnings

    times = parse_narration_times(narration_path)
    if not times:
        warnings.append("no timestamped cues detected")
        return pid, family, errors, warnings

    # order and bounds
    prev_t = -1
    for t, line_no, _line in times:
        if t < prev_t:
            errors.append(f"non-monotonic timestamps around line {line_no}")
            break
        prev_t = t
        if t > duration_s:
            errors.append(f"timestamp beyond session duration at line {line_no} ({t}s > {duration_s}s)")
            break

    # coverage checks
    first_t = times[0][0]
    last_t = times[-1][0]
    if first_t > min(120, max(30, duration_s // 10)):
        warnings.append(f"late first cue at {first_t}s")
    if duration_s - last_t > min(180, max(60, duration_s // 8)):
        warnings.append(f"no closing cue near end (last at {last_t}s)")

    # phase coverage: at least one cue in each phase
    phase_hits = [0] * len(phases)
    for t, _line_no, _line in times:
        for i, ph in enumerate(phases):
            if int(ph["start_s"]) <= t <= int(ph["end_s"]):
                phase_hits[i] += 1
                break
    for i, hits in enumerate(phase_hits, start=1):
        if hits == 0:
            warnings.append(f"phase {i} has no narration cue")

    return pid, family, errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate narration guides against protocol specs.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    specs = sorted(root.glob("protocols/*/specs/*.yaml"))

    error_count = 0
    warning_count = 0
    for spec_path in specs:
        pid, family, errors, warnings = validate_one(root, spec_path)
        for e in errors:
            print(f"ERROR {pid} ({family}): {e}")
        for w in warnings:
            print(f"WARN  {pid} ({family}): {w}")
        error_count += len(errors)
        warning_count += len(warnings)

    print(f"\nNarration validation summary: specs={len(specs)} errors={error_count} warnings={warning_count}")
    if error_count > 0:
        raise SystemExit(1)
    if args.strict and warning_count > 0:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
