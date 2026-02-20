# PERF-03 - Micro-Dose Focus

## Overview
- Family: `PERF`
- Duration: `5m`
- ID: `PERF-03`

## Intended Use
Use `PERF-03` as a structured 5-minute session. Run in a quiet setting with headphones.

## Phase Structure
- Phase 1: `Ramp` (`0s` to `180s`)
- Phase 2: `Peak` (`180s` to `300s`)

## Audio Layers
- `noise_bed`
- `binaural`
- `pulse_cues`

## Render
```bash
cd /Users/jdarrow/workspace/meditation/protocol-lab/tools
python3 render_protocol.py ../protocols/PERF/specs/PERF-03_5m.yaml --out_dir ../protocols/PERF/renders
```

## Narration
- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/PERF/narration/PERF-03_coaching.md`

## Safety
- Do not use while driving or operating machinery.
- Stop immediately if distress escalates.
- Use conservative volume levels.
