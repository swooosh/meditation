# FSP-01: Focused State Protocol

Gateway-inspired attentional architecture protocol for building narrow focus and controlled state shifts.

## Overview

- **Duration**: 31 minutes
- **Family**: FSP (Attentional Architecture)
- **Phases**: 5 (Downshift → Body Scan → Attentional Lock → State Shift → Reintegration)

## Quick Start

```bash
cd protocol-lab/protocols/FSP/audio
python render_fsp.py --level living --out_dir ../renders --master
```

## Levels

- **living**: Balanced, warm soundfield with moderate binaural entrainment
- **temple**: Minimal cues, deeper stillness, reduced drift
- **focus**: Brighter, more structured, stronger return cues

## Audio Layers

- Brown/pink noise beds with slow stereo drift
- Binaural beats (constant in Phase 3, ramping in Phase 4-5)
- Optional breath cues (4-6 pattern)
- Optional return cues (Phase 3)
- Optional let-go swells (Phase 4)

## Parameters

Key tunable parameters per level:
- Noise type (brown/pink)
- Drift frequency and depth
- Binaural beat frequency and carrier
- Return cue timing and level
- Let-go swell timing and level

## Render Commands

```bash
# Default living preset
python render_fsp.py

# Temple preset (minimal)
python render_fsp.py --level temple

# Focus preset (structured)
python render_fsp.py --level focus

# With master stitch
python render_fsp.py --level living --master
```

## Files

- `specs/FSP-01_31m.yaml` - Protocol specification
- `audio/render_fsp.py` - Renderer
- `narration/FSP-01_coaching.md` - Narration script
- `renders/` - Output directory
