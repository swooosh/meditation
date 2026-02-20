# PAIN-01 - Gate Control

## Overview
- Family: `PAIN`
- Duration: `15m`
- ID: `PAIN-01`

## Intended Use
Use `PAIN-01` as a structured 15-minute session. Run in a quiet setting with headphones.

## Phase Structure
- Phase 1: `Locate` (`0s` to `300s`)
- Phase 2: `Modulate` (`300s` to `720s`)
- Phase 3: `Release` (`720s` to `900s`)

## Audio Layers
- `noise_bed`
- `binaural`
- `pulse_cues`
- `sub`

## Render
```bash
cd /Users/jdarrow/workspace/meditation/protocol-lab/tools
python3 render_protocol.py ../protocols/PAIN/specs/PAIN-01_15m.yaml --out_dir ../protocols/PAIN/renders
```

## Narration
- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/PAIN/narration/PAIN-01_coaching.md`

## Safety
- Do not use while driving or operating machinery.
- Stop immediately if distress escalates.
- Use conservative volume levels.
