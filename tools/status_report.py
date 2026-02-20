#!/usr/bin/env python3
"""Generate protocol implementation status from filesystem state."""
import argparse
import json
import os
import re
import sys
import wave
from pathlib import Path

import yaml

# Add protocol-lab root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.render_protocol import SUPPORTED_LAYER_TYPES


def protocol_id_from_spec_name(name):
    match = re.match(r"([A-Z0-9-]+)_", name)
    return match.group(1) if match else None


def collect_specs(root):
    specs = {}
    for spec_path in sorted(root.glob("protocols/*/specs/*.yaml")):
        protocol_id = protocol_id_from_spec_name(spec_path.name)
        if not protocol_id:
            continue
        with spec_path.open() as f:
            spec = yaml.safe_load(f)
        specs[protocol_id] = {
            "id": protocol_id,
            "family": spec_path.parts[-3],
            "spec_path": str(spec_path),
            "duration_s": int(spec.get("duration_s", 0)),
            "spec_duration_m": int(round(spec.get("duration_s", 0) / 60)),
            "layers": [layer.get("type") for layer in spec.get("audio_layers", []) if isinstance(layer, dict)],
        }
    return specs


def collect_narrations(root):
    protocol_to_files = {}
    for narration_path in sorted(root.glob("protocols/*/narration/*.md")):
        match = re.match(r"([A-Z0-9-]+)(?:_|\.|$)", narration_path.name)
        if not match:
            continue
        protocol_id = match.group(1)
        protocol_to_files.setdefault(protocol_id, []).append(str(narration_path))
    return protocol_to_files


def collect_renders(root):
    renders = {}
    for render_path in sorted(root.glob("protocols/*/renders/*_master.wav")):
        match = re.match(r"([A-Z0-9-]+)_master\.wav$", render_path.name)
        if not match:
            continue
        protocol_id = match.group(1)
        renders[protocol_id] = str(render_path)
    return renders


def wav_duration_seconds(path):
    try:
        with wave.open(str(path), "rb") as w:
            return w.getnframes() / float(w.getframerate())
    except Exception:
        return None


def parse_index_metadata(root):
    index_path = root / "docs" / "PROTOCOL_INDEX.md"
    if not index_path.exists():
        return {}

    link_pattern = re.compile(
        r"^- \[([A-Z0-9-]+):[^\]]+\]\(([^)]+)\)\s*-\s*(\d+)m\s*-"
    )
    plain_pattern = re.compile(
        r"^- ([A-Z0-9-]+):[^-]+\s-\s*(\d+)m\s*-"
    )
    entries = {}
    for line in index_path.read_text().splitlines():
        stripped = line.strip()
        m_link = link_pattern.match(stripped)
        if m_link:
            protocol_id, rel_link, duration_m = m_link.group(1), m_link.group(2), int(m_link.group(3))
            doc_path = root / "docs" / rel_link
            entries[protocol_id] = {
                "index_link": rel_link,
                "index_duration_m": duration_m,
                "index_doc_exists": doc_path.exists(),
            }
            continue
        m_plain = plain_pattern.match(stripped)
        if m_plain:
            protocol_id, duration_m = m_plain.group(1), int(m_plain.group(2))
            entries[protocol_id] = {
                "index_link": None,
                "index_duration_m": duration_m,
                "index_doc_exists": False,
            }
    return entries


def build_status(root):
    specs = collect_specs(root)
    narrations = collect_narrations(root)
    renders = collect_renders(root)
    index = parse_index_metadata(root)

    rows = []
    for protocol_id in sorted(specs):
        spec = specs[protocol_id]
        unknown_layers = sorted(
            {layer for layer in spec["layers"] if layer and layer not in SUPPORTED_LAYER_TYPES}
        )
        narration_files = narrations.get(protocol_id, [])
        index_entry = index.get(protocol_id, {})

        row = {
            "id": protocol_id,
            "family": spec["family"],
            "spec_path": spec["spec_path"],
            "spec_exists": True,
            "narration_exists": bool(narration_files),
            "narration_count": len(narration_files),
            "render_exists": protocol_id in renders,
            "render_path": renders.get(protocol_id),
            "supported_by_renderer": len(unknown_layers) == 0,
            "unknown_layers": unknown_layers,
            "index_entry_exists": bool(index_entry),
            "index_doc_exists": index_entry.get("index_doc_exists", False),
            "index_duration_m": index_entry.get("index_duration_m"),
            "spec_duration_m": spec["spec_duration_m"],
            "duration_match_index": (
                index_entry.get("index_duration_m") == spec["spec_duration_m"]
                if index_entry
                else None
            ),
        }
        if row["render_exists"]:
            actual_dur = wav_duration_seconds(row["render_path"])
            row["render_duration_s"] = actual_dur
            expected = float(spec["duration_s"])
            row["render_complete"] = (
                actual_dur is not None and actual_dur >= expected * 0.99
            )
        else:
            row["render_duration_s"] = None
            row["render_complete"] = False

        row["fully_complete"] = (
            row["spec_exists"]
            and row["narration_exists"]
            and row["render_complete"]
            and row["supported_by_renderer"]
        )
        rows.append(row)
    return rows


def summarize(rows):
    return {
        "total_protocols": len(rows),
        "fully_complete": sum(1 for r in rows if r["fully_complete"]),
        "render_ready_no_missing_layers": sum(1 for r in rows if r["supported_by_renderer"]),
        "with_narration": sum(1 for r in rows if r["narration_exists"]),
        "with_render": sum(1 for r in rows if r["render_exists"]),
        "with_complete_render": sum(1 for r in rows if r["render_complete"]),
        "missing_complete_render": sum(1 for r in rows if not r["render_complete"]),
        "with_broken_doc_link": sum(
            1 for r in rows if r["index_entry_exists"] and not r["index_doc_exists"]
        ),
        "duration_mismatch_vs_index": sum(
            1 for r in rows if r["duration_match_index"] is False
        ),
    }


def print_human(rows):
    s = summarize(rows)
    print("Protocol Status Report")
    print("=" * 72)
    print(f"Total protocols: {s['total_protocols']}")
    print(f"Fully complete (spec+narration+render+supported): {s['fully_complete']}")
    print(f"Renderer-compatible specs: {s['render_ready_no_missing_layers']}")
    print(f"Protocols with narration: {s['with_narration']}")
    print(f"Protocols with render: {s['with_render']}")
    print(f"Protocols with complete render: {s['with_complete_render']}")
    print(f"Protocols missing complete render: {s['missing_complete_render']}")
    print(f"Broken index doc links: {s['with_broken_doc_link']}")
    print(f"Index duration mismatches: {s['duration_mismatch_vs_index']}")
    print()

    print("Protocols blocked by unsupported layers:")
    blocked = [r for r in rows if not r["supported_by_renderer"]]
    if not blocked:
        print("- none")
    else:
        for r in blocked:
            print(f"- {r['id']}: {', '.join(r['unknown_layers'])}")
    print()

    print("Protocols missing narration:")
    missing_n = [r["id"] for r in rows if not r["narration_exists"]]
    print("- none" if not missing_n else "- " + ", ".join(missing_n))
    print()

    print("Protocols missing complete render:")
    missing_r = [r["id"] for r in rows if not r["render_complete"]]
    print("- none" if not missing_r else "- " + ", ".join(missing_r))


def main():
    parser = argparse.ArgumentParser(description="Generate protocol implementation status report.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of human-readable output.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    rows = build_status(root)

    if args.json:
        print(json.dumps({"summary": summarize(rows), "protocols": rows}, indent=2))
    else:
        print_human(rows)


if __name__ == "__main__":
    main()
