# Protocol Lab

Spec-driven meditation and breathwork protocol system with deterministic audio rendering, QC tooling, narration/docs, and a static web player.

## What This Repo Contains

- `protocols/`: protocol families, YAML specs, narration, and family diagrams
- `engine/`: DSP + render core
- `tools/`: render, QC, validation, and status utilities
- `docs/`: protocol documentation and indexes
- `web/`: static web app (protocol browser/player)

## Current Library

- 14 families / 35 protocols
- Family coverage: `ATTN`, `ARC`, `BODY`, `CREA`, `FLOW`, `FSP`, `META`, `PAIN`, `PERF`, `RECON`, `SENSE`, `SLEEP`, `SOC`, `SUN`

## Quick Start

```bash
cd tools

# Render one protocol
python3 render_protocol.py ../protocols/PERF/specs/PERF-01_12m.yaml --out_dir ../protocols/PERF/renders --strict-qc

# Render missing protocols
python3 render_missing.py

# Re-render library (supports filters like --family / --max-minutes)
python3 rerender_library.py
```

## Getting Started in 5 Minutes

```bash
# 1) Enter repo
cd /Users/jdarrow/workspace/meditation/protocol-lab

# 2) GitHub auth (one-time, if needed)
gh auth login

# 3) Render one protocol with strict QC
cd tools
python3 render_protocol.py ../protocols/PERF/specs/PERF-01_12m.yaml --out_dir ../protocols/PERF/renders --strict-qc

# 4) Refresh QC/status and verify gate
python3 generate_qc_artifacts.py --overwrite
python3 update_render_status.py
python3 release_gate.py --json

# 5) Commit + push
cd ..
git add .
git commit -m "Update protocol specs/engine/docs"
git push
```

## Validation and Release Checks

```bash
cd tools

# Spec and narration validation
python3 validate_specs.py
python3 validate_narration.py

# Build QC sidecars + web status manifest
python3 generate_qc_artifacts.py --overwrite
python3 update_render_status.py

# End-to-end release gate
python3 release_gate.py --json
```

## Diagrams

- Generated family diagram packs live at:
  - `protocols/<FAMILY>/diagrams/`
- Index:
  - `docs/DIAGRAMS_INDEX.md`
- Regenerate:

```bash
cd tools
python3 generate_diagrams.py
```

## Website

Static app in `web/`:

- protocol browsing/filtering
- render-status-aware playability
- docs + narration + family diagrams in protocol detail
- guided/unguided audio toggle

See deployment notes in `web/README.md`.

## Git Notes

- Rendered audio is intentionally ignored via `.gitignore`:
  - `protocols/*/renders/*.wav`
  - `protocols/*/renders/*.mp3`
  - `tools/renders/`
  - `tools/test_renders/`
  - `web/audio/`

This keeps repository size manageable and avoids GitHub file-size limits.

## Safety

These protocols include high-intensity breathwork and deep emotional processing tracks.

- Do not use while driving or operating machinery.
- Use conservative volume with headphones.
- Respect contraindications and stop if distressed.

See protocol docs under `docs/protocols/` for protocol-specific safety guidance.
