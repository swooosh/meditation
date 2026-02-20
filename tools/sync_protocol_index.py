#!/usr/bin/env python3
"""Sync docs/PROTOCOL_INDEX.md protocol list from YAML specs."""
from pathlib import Path
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "docs" / "PROTOCOL_INDEX.md"

FAMILY_ORDER = [
    "ATTN",
    "ARC",
    "PERF",
    "RECON",
    "SENSE",
    "SLEEP",
    "SOC",
    "META",
    "CREA",
    "BODY",
    "FLOW",
    "PAIN",
    "SUN",
]

FAMILY_HEADERS = {
    "ATTN": "### ATTN Family (Attention Architecture)",
    "ARC": "### ARC Family (Breath-Driven Intensity)",
    "PERF": "### PERF Family (Performance State)",
    "RECON": "### RECON Family (Emotional Reprocessing)",
    "SENSE": "### SENSE Family (Sensory Precision)",
    "SLEEP": "### SLEEP Family (Sleep Architecture)",
    "SOC": "### SOC Family (Social Coherence)",
    "META": "### META Family (Self-Model Exploration)",
    "CREA": "### CREA Family (Creative Emergence)",
    "BODY": "### BODY Family (Somatic Power)",
    "FLOW": "### FLOW Family (Flow State)",
    "PAIN": "### PAIN Family (Pain Modulation)",
    "SUN": "### SUN Family (Small Universe)",
}

PREFIX_TO_FAMILY = {
    "FSP": "ATTN",
    "ARC": "ARC",
    "PERF": "PERF",
    "RECON": "RECON",
    "SENSE": "SENSE",
    "SLEEP": "SLEEP",
    "SOC": "SOC",
    "META": "META",
    "CREA": "CREA",
    "BODY": "BODY",
    "FLOW": "FLOW",
    "PAIN": "PAIN",
    "SUN": "SUN",
}


def load_specs():
    entries = []
    for spec_path in sorted(ROOT.glob("protocols/*/specs/*.yaml")):
        with spec_path.open() as f:
            spec = yaml.safe_load(f)
        pid = spec["id"]
        prefix = pid.split("-")[0]
        fam = PREFIX_TO_FAMILY[prefix]
        title = str(spec.get("title", pid))
        if "—" in title:
            title = title.split("—", 1)[0].strip()
        duration_m = int(round(int(spec.get("duration_s", 0)) / 60))
        entries.append((fam, pid, title, duration_m))
    return entries


def existing_descriptions(index_text):
    desc = {}
    pattern = re.compile(r"- \[([A-Z0-9-]+): [^\]]+\]\([^)]+\) - \d+m - (.+)")
    for line in index_text.splitlines():
        m = pattern.match(line.strip())
        if m:
            desc[m.group(1)] = m.group(2).strip()
    return desc


def existing_doc_ids():
    ids = set()
    for p in ROOT.glob("docs/protocols/*.md"):
        ids.add(p.stem)
    return ids


def render_protocol_sections(specs, desc_map, doc_ids):
    grouped = {k: [] for k in FAMILY_ORDER}
    for fam, pid, title, duration_m in specs:
        grouped[fam].append((pid, title, duration_m))

    out = ["## Complete Protocol Library", ""]
    for fam in FAMILY_ORDER:
        out.append(FAMILY_HEADERS[fam])
        for pid, title, duration_m in sorted(grouped[fam]):
            detail = desc_map.get(pid, "See protocol documentation")
            if pid in doc_ids:
                label = f"[{pid}: {title}](protocols/{pid}.md)"
            else:
                label = f"{pid}: {title}"
            out.append(f"- {label} - {duration_m}m - {detail}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main():
    original = INDEX_PATH.read_text()
    desc_map = existing_descriptions(original)
    specs = load_specs()
    doc_ids = existing_doc_ids()

    start = "## Complete Protocol Library"
    end = "## Quick Selection Guide"
    if start not in original or end not in original:
        raise RuntimeError("Could not locate protocol list section boundaries.")

    before, rest = original.split(start, 1)
    _, after = rest.split(end, 1)
    rebuilt = render_protocol_sections(specs, desc_map, doc_ids)
    updated = before + rebuilt + "\n" + end + after
    INDEX_PATH.write_text(updated)
    print(f"Updated {INDEX_PATH}")


if __name__ == "__main__":
    main()
