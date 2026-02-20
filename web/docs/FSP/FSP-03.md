# FSP-03 - Rapid Context Switching

## Overview
- Family: `ATTN`
- Duration: `15m`
- ID: `FSP-03`

## Intended Use
Use `FSP-03` as a structured 15-minute session. Run in a quiet setting with headphones.

## Phase Structure
- Phase 1: `Baseline` (`0s` to `180s`)
- Phase 2: `Switch` (`180s` to `720s`)
- Phase 3: `Stabilize` (`720s` to `900s`)

## Audio Layers
- `noise_bed`
- `binaural`
- `switch_cues`

## Render
```bash
cd /Users/jdarrow/workspace/meditation/protocol-lab/tools
python3 render_protocol.py ../protocols/ATTN/specs/FSP-03_15m.yaml --out_dir ../protocols/ATTN/renders
```

## Narration
- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/ATTN/narration/FSP-03_coaching.md`

## Safety
- Do not use while driving or operating machinery.
- Stop immediately if distress escalates.
- Use conservative volume levels.
