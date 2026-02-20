#!/usr/bin/env python3
"""Generate basic protocol docs for specs missing docs/protocols/<ID>.md."""
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs" / "protocols"


def mm(seconds):
    return int(round(int(seconds) / 60))


def gen_doc(spec):
    pid = spec["id"]
    title = str(spec.get("title", pid)).replace("—", "-")
    family = spec.get("family", "UNKNOWN")
    duration_m = mm(spec.get("duration_s", 0))
    phases = spec.get("phases", [])
    layers = [l.get("type") for l in spec.get("audio_layers", []) if isinstance(l, dict)]

    lines = [
        f"# {pid} - {title}",
        "",
        "## Overview",
        f"- Family: `{family}`",
        f"- Duration: `{duration_m}m`",
        f"- ID: `{pid}`",
        "",
        "## Intended Use",
        f"Use `{pid}` as a structured {duration_m}-minute session. Run in a quiet setting with headphones.",
        "",
        "## Phase Structure",
    ]

    if phases:
        for i, ph in enumerate(phases, 1):
            name = ph.get("name", f"Phase {i}")
            start = int(ph.get("start_s", 0))
            end = int(ph.get("end_s", start))
            intent = ph.get("intent")
            line = f"- Phase {i}: `{name}` (`{start}s` to `{end}s`)"
            if intent:
                line += f" - {intent}"
            lines.append(line)
    else:
        lines.append("- No phase metadata found in spec.")

    lines.extend(["", "## Audio Layers"])
    if layers:
        lines.extend(f"- `{layer}`" for layer in layers)
    else:
        lines.append("- No audio layer metadata found in spec.")

    lines.extend(
        [
            "",
            "## Render",
            "```bash",
            f"cd /Users/jdarrow/workspace/meditation/protocol-lab/tools",
            f"python3 render_protocol.py ../protocols/{family}/specs/{pid}_{duration_m}m.yaml --out_dir ../protocols/{family}/renders",
            "```",
            "",
            "## Narration",
            f"- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/{family}/narration/{pid}_coaching.md`",
            "",
            "## Safety",
            "- Do not use while driving or operating machinery.",
            "- Stop immediately if distress escalates.",
            "- Use conservative volume levels.",
            "",
        ]
    )
    return "\n".join(lines)


def main():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    created = 0
    for spec_path in sorted(ROOT.glob("protocols/*/specs/*.yaml")):
        with spec_path.open() as f:
            spec = yaml.safe_load(f)
        pid = spec["id"]
        out = DOCS_DIR / f"{pid}.md"
        if out.exists():
            continue
        out.write_text(gen_doc(spec))
        created += 1
        print(f"Created: {out}")
    if created == 0:
        print("No missing docs.")


if __name__ == "__main__":
    main()
