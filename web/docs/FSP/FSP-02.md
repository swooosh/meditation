# FSP-02 - Distributed Attention

## Overview
- Family: `ATTN`
- Duration: `25m`
- ID: `FSP-02`

## Intended Use
Use `FSP-02` as a structured 25-minute session. Run in a quiet setting with headphones.

## Phase Structure
- Phase 1: `Anchor` (`0s` to `300s`)
- Phase 2: `Distribute` (`300s` to `1200s`)
- Phase 3: `Integrate` (`1200s` to `1500s`)

## Audio Layers
- `noise_bed`
- `binaural`
- `spatial_sweep`
- `pulse_cues`

## Render
```bash
cd /Users/jdarrow/workspace/meditation/protocol-lab/tools
python3 render_protocol.py ../protocols/ATTN/specs/FSP-02_25m.yaml --out_dir ../protocols/ATTN/renders
```

## Narration
- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/ATTN/narration/FSP-02_coaching.md`

## Safety
- Do not use while driving or operating machinery.
- Stop immediately if distress escalates.
- Use conservative volume levels.
