# ARC-1TB: Adaptive Respiratory Cycle — Tribal Breath

Breath-driven somatic intensity protocol using tribal percussion to guide respiratory rate through controlled activation and wave cycling.

## Overview

- **Duration**: 60 minutes
- **Family**: ARC (Somatic Intensity)
- **Phases**: 5 (Ground → Activation Ramp → Boundary Softening → Wave Cycling → Reintegration)

## Quick Start

```bash
cd protocol-lab/protocols/ARC/audio
python render_arc.py --out_dir ../renders
```

## Breath Curve

The protocol follows a precise breath rate curve:
- 0-10min: 6 bpm (ground)
- 10-20min: 6→18 bpm (ramp)
- 20-35min: 18→26 bpm (plateau)
- 35-50min: Wave cycling (28↔18 bpm, 3 peaks)
- 50-60min: 18→6 bpm (descent)

## Audio Layers

- **Tribal drums**: Frame drum, low tom, wood tick, shaker
- **Sub bass**: 48-58 Hz coupled to breath rate
- **Room illusion**: Early reflections + ambience bed
- **Signature marker**: 3-tone motif (174/220/293 Hz)

## Phase 4 Contrast

Wave Cycling phase uses dynamic contrast:
- **Peaks** (28 bpm): Denser drums, brighter accents, higher sub
- **Recovers** (18 bpm): Sparser drums, cleaner texture, lower sub

## Render Commands

```bash
# Standard render
python render_arc.py

# Custom spec
python render_arc.py --spec specs/ARC-1TB_60m.yaml

# Output to custom directory
python render_arc.py --out_dir ../renders/v2
```

## Technical Details

- Sample rate: 44.1 kHz
- Deterministic (seeded RNG)
- Bus soft clipping for sub safety
- Skin-forward drum synthesis
- Breath-coupled scheduling

## Files

- `specs/ARC-1TB_60m.yaml` - Protocol specification
- `audio/render_arc.py` - Renderer
- `narration/ARC-1TB_coaching.md` - Narration script
- `renders/` - Output directory
