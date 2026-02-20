#!/usr/bin/env python3
"""Generate standardized family diagram docs from protocol specs."""
from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).resolve().parents[1]
PROTOCOLS_DIR = ROOT / "protocols"
DOCS_DIR = ROOT / "docs"


def load_specs_by_family():
    out = defaultdict(list)
    for spec_path in sorted(PROTOCOLS_DIR.glob("*/specs/*.yaml")):
        data = yaml.safe_load(spec_path.read_text())
        family = spec_path.parts[-3]
        out[family].append(data)
    return out


def clean_id(pid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", pid)


def mmss(seconds: int) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    return f"{m:02d}:{s:02d}"


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def build_timeline_md(family: str, specs: list[dict]) -> str:
    lines = []
    lines.append(f"# {family} Phase Timelines")
    lines.append("")
    lines.append("Generated from active specs. Use these as timing-reference diagrams for narration and mix decisions.")
    lines.append("")

    for spec in sorted(specs, key=lambda s: s["id"]):
        pid = spec["id"]
        title = spec.get("title", pid)
        duration_s = int(spec.get("duration_s", 0))
        lines.append(f"## {pid} - {title}")
        lines.append("")
        lines.append(f"Duration: **{duration_s // 60}m** ({duration_s}s)")
        lines.append("")
        lines.append("```mermaid")
        lines.append("gantt")
        lines.append(f"title {pid} Phase Timeline")
        lines.append("dateFormat X")
        lines.append("axisFormat %M:%S")
        lines.append("section Session")
        phases = spec.get("phases", [])
        for ph in phases:
            name = str(ph.get("name", "Phase"))
            st = int(ph.get("start_s", 0))
            en = int(ph.get("end_s", st))
            dur = max(1, en - st)
            lines.append(f"{name} : {st}, {dur}")
        lines.append("```")
        lines.append("")
        lines.append("| Phase | Start | End | Intent |")
        lines.append("|---|---:|---:|---|")
        for ph in phases:
            name = str(ph.get("name", "Phase"))
            st = int(ph.get("start_s", 0))
            en = int(ph.get("end_s", st))
            intent = str(ph.get("intent", "")).strip() or "-"
            lines.append(f"| {name} | {mmss(st)} | {mmss(en)} | {intent} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def build_signal_chain_md(family: str, specs: list[dict]) -> str:
    layer_counts = Counter()
    for spec in specs:
        for layer in spec.get("audio_layers", []):
            ltype = layer.get("type")
            if ltype:
                layer_counts[ltype] += 1

    common = [k for k, _ in layer_counts.most_common(8)]
    if not common:
        common = ["noise_bed", "binaural"]

    lines = []
    lines.append(f"# {family} Signal Chain")
    lines.append("")
    lines.append("Family-level audio chain showing layer families, mix bus, mastering, and QC gates.")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart LR")
    lines.append("  S[Spec YAML] --> P[Phase Scheduler]")
    for idx, layer in enumerate(common, start=1):
        node = f"L{idx}"
        label = layer.replace("_", " ").title()
        lines.append(f"  P --> {node}[{label}]")
        lines.append(f"  {node} --> M[Mix Bus]")
    lines.append("  M --> A[Mastering: tilt, width, low-end management]")
    lines.append("  A --> Q[QC: amplitude + spectral by phase]")
    lines.append("  Q --> W[Master WAV]")
    lines.append("```")
    lines.append("")
    lines.append("| Layer Type | Presence |")
    lines.append("|---|---:|")
    for layer, count in layer_counts.most_common():
        lines.append(f"| `{layer}` | {count}/{len(specs)} specs |")
    lines.append("")
    return "\n".join(lines) + "\n"


def orbit_subgraph() -> list[str]:
    return [
        "  subgraph Orbit Path",
        "    LD[Lower Dantian] --> HY[Huiyin/Perineum]",
        "    HY --> SP[Up Spine]",
        "    SP --> CR[Crown]",
        "    CR --> UD[Upper Dantian]",
        "    UD --> MD[Middle Dantian]",
        "    MD --> LD",
        "  end",
    ]


def build_practice_flow_md(family: str, specs: list[dict]) -> str:
    breath_presets = Counter()
    for spec in specs:
        bp = spec.get("breath_pattern")
        if bp:
            breath_presets[str(bp)] += 1
        for layer in spec.get("audio_layers", []):
            if layer.get("type") == "breath_cues":
                preset = layer.get("params", {}).get("preset")
                if preset:
                    breath_presets[str(preset)] += 1

    top_breath = breath_presets.most_common(3)
    breath_note = ", ".join([f"{k} ({v})" for k, v in top_breath]) if top_breath else "none"

    lines = []
    lines.append(f"# {family} Practice Flow")
    lines.append("")
    lines.append("Standard facilitation flow for this family. Use alongside protocol timelines and narration scripts.")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart TD")
    lines.append("  A[Prepare Space and Intent] --> B[Settle and Baseline]")
    lines.append("  B --> C[Follow Phase Cues]")
    if breath_presets:
        lines.append("  C --> D[Breath Tracking and Cue Sync]")
        lines.append("  D --> E[Peak or Core Training Segment]")
    else:
        lines.append("  C --> E[Peak or Core Training Segment]")
    lines.append("  E --> F[Downshift and Integration]")
    lines.append("  F --> G[Closure and Post-Session Notes]")
    if family == "SUN":
        lines.extend(orbit_subgraph())
        lines.append("  D --> LD")
        lines.append("  MD --> F")
    lines.append("```")
    lines.append("")
    lines.append(f"Breath presets detected: **{breath_note}**")
    lines.append("")
    lines.append("## Protocol Coverage")
    lines.append("")
    lines.append("| Protocol | Primary Goal |")
    lines.append("|---|---|")
    for spec in sorted(specs, key=lambda s: s["id"]):
        pid = spec["id"]
        phases = spec.get("phases", [])
        goal = "-"
        if phases:
            goal = str(phases[-1].get("intent") or phases[0].get("intent") or "-")
        lines.append(f"| `{pid}` | {goal} |")
    lines.append("")
    return "\n".join(lines) + "\n"


def build_index(specs_by_family: dict[str, list[dict]]) -> str:
    lines = []
    lines.append("# Diagrams Index")
    lines.append("")
    lines.append("Standard diagram pack generated for each family:")
    lines.append("- `*_phase_timeline.md`: per-protocol phase timing")
    lines.append("- `*_signal_chain.md`: audio architecture and layer prevalence")
    lines.append("- `*_practice_flow.md`: facilitation and listener journey")
    lines.append("")
    for family in sorted(specs_by_family):
        base = f"../protocols/{family}/diagrams"
        lines.append(f"## {family}")
        lines.append(f"- [{family} phase timelines]({base}/{family}_phase_timeline.md)")
        lines.append(f"- [{family} signal chain]({base}/{family}_signal_chain.md)")
        lines.append(f"- [{family} practice flow]({base}/{family}_practice_flow.md)")
        lines.append("")
    return "\n".join(lines) + "\n"


def main():
    specs_by_family = load_specs_by_family()
    for family, specs in specs_by_family.items():
        d = PROTOCOLS_DIR / family / "diagrams"
        write_text(d / f"{family}_phase_timeline.md", build_timeline_md(family, specs))
        write_text(d / f"{family}_signal_chain.md", build_signal_chain_md(family, specs))
        write_text(d / f"{family}_practice_flow.md", build_practice_flow_md(family, specs))

    write_text(DOCS_DIR / "DIAGRAMS_INDEX.md", build_index(specs_by_family))
    print(f"Generated diagrams for {len(specs_by_family)} families")


if __name__ == "__main__":
    main()
