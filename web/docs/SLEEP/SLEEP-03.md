# SLEEP-03 - Deep Delta

## Overview
- Family: `SLEEP`
- Duration: `50m`
- ID: `SLEEP-03`

## Intended Use
Use `SLEEP-03` as a structured 50-minute session. Run in a quiet setting with headphones.

## Phase Structure
- Phase 1: `Drift` (`0s` to `900s`)
- Phase 2: `Descend` (`900s` to `2100s`)
- Phase 3: `Deep` (`2100s` to `3000s`)

## Audio Layers
- `noise_bed`
- `binaural`
- `sub`
- `room_illusion`

## Render
```bash
cd /Users/jdarrow/workspace/meditation/protocol-lab/tools
python3 render_protocol.py ../protocols/SLEEP/specs/SLEEP-03_50m.yaml --out_dir ../protocols/SLEEP/renders
```

## Narration
- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/SLEEP/narration/SLEEP-03_coaching.md`

## Safety
- Do not use while driving or operating machinery.
- Stop immediately if distress escalates.
- Use conservative volume levels.
