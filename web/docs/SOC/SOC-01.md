# SOC-01 - Dyadic Breath Sync - Two-Person Coherence

## Overview
- Family: `SOC`
- Duration: `20m`
- ID: `SOC-01`

## Intended Use
Use `SOC-01` as a structured 20-minute session. Run in a quiet setting with headphones.

## Phase Structure
- Phase 1: `Individual` (`0s` to `300s`) - Establish individual rhythm
- Phase 2: `Alternating` (`300s` to `720s`) - Alternate breath cues L/R
- Phase 3: `Converge` (`720s` to `1200s`) - Synchronized breathing

## Audio Layers
- `noise_bed`
- `binaural`
- `dyadic_cues`

## Render
```bash
cd /Users/jdarrow/workspace/meditation/protocol-lab/tools
python3 render_protocol.py ../protocols/SOC/specs/SOC-01_20m.yaml --out_dir ../protocols/SOC/renders
```

## Narration
- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/SOC/narration/SOC-01_coaching.md`

## Safety
- Do not use while driving or operating machinery.
- Stop immediately if distress escalates.
- Use conservative volume levels.
