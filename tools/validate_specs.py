#!/usr/bin/env python3
"""Validate protocol specs against structural + quality rules."""
import argparse
from pathlib import Path
import re
import sys

import yaml


def validate_spec(path: Path):
    problems = []
    warnings = []
    data = yaml.safe_load(path.read_text())

    required = ["id", "title", "family", "duration_s", "phases", "audio_layers"]
    for key in required:
        if key not in data:
            problems.append(f"missing required key: {key}")

    if data.get("id") and not path.name.startswith(f"{data['id']}_"):
        problems.append("filename does not start with id")
    if data.get("family") and path.parts[-3] != data["family"]:
        problems.append(f"family mismatch: file dir={path.parts[-3]} spec={data['family']}")

    m = re.search(r"_(\d+)m\.yaml$", path.name)
    if m and data.get("duration_s"):
        file_m = int(m.group(1))
        spec_m = int(round(float(data["duration_s"]) / 60.0))
        if file_m != spec_m:
            problems.append(f"filename duration {file_m}m != spec duration {spec_m}m")

    phases = data.get("phases") or []
    if not phases:
        problems.append("no phases defined")
    else:
        prev_end = None
        for idx, phase in enumerate(phases, start=1):
            if "start_s" not in phase or "end_s" not in phase:
                problems.append(f"phase {idx} missing start_s/end_s")
                continue
            start_s = int(phase["start_s"])
            end_s = int(phase["end_s"])
            if end_s <= start_s:
                problems.append(f"phase {idx} non-positive duration ({start_s}->{end_s})")
            if idx == 1 and start_s != 0:
                problems.append(f"phase 1 must start at 0, got {start_s}")
            if prev_end is not None and start_s != prev_end:
                problems.append(f"phase gap/overlap before phase {idx}: {prev_end}->{start_s}")
            prev_end = end_s
            if not phase.get("name"):
                problems.append(f"phase {idx} missing name")
            if not phase.get("intent"):
                warnings.append(f"phase {idx} missing intent")
        if data.get("duration_s") and prev_end != int(data["duration_s"]):
            problems.append(f"last phase ends at {prev_end}, expected {int(data['duration_s'])}")

    layers = data.get("audio_layers") or []
    if not layers:
        problems.append("no audio_layers defined")
    for idx, layer in enumerate(layers, start=1):
        if not isinstance(layer, dict) or not layer.get("type"):
            problems.append(f"audio layer {idx} missing type")

    layer_types = [layer.get("type") for layer in layers if isinstance(layer, dict)]
    has_breath_cues = "breath_cues" in layer_types
    breath_pattern = str(data.get("breath_pattern", "none")).lower()
    if breath_pattern != "none" and not has_breath_cues:
        warnings.append("breath_pattern set but no breath_cues layer")
    if has_breath_cues and breath_pattern == "none":
        warnings.append("breath_cues layer present but breath_pattern missing/none")

    if "identity" not in data:
        warnings.append("missing identity block")

    return problems, warnings


def main():
    parser = argparse.ArgumentParser(description="Validate all protocol YAML specs.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failures.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    specs = sorted(root.glob("protocols/*/specs/*.yaml"))

    total_problems = 0
    total_warnings = 0
    for spec in specs:
        problems, warnings = validate_spec(spec)
        rel = spec.relative_to(root)
        for problem in problems:
            print(f"ERROR {rel}: {problem}")
        for warning in warnings:
            print(f"WARN  {rel}: {warning}")
        total_problems += len(problems)
        total_warnings += len(warnings)

    print(f"\nSpecs checked: {len(specs)}")
    print(f"Errors: {total_problems}")
    print(f"Warnings: {total_warnings}")

    if total_problems > 0:
        sys.exit(1)
    if args.strict and total_warnings > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
