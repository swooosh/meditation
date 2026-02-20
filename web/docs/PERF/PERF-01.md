# PERF-01 - Pre-Mission Focus - Calm Alert Coherence

## Overview
- Family: `PERF`
- Duration: `12m`
- ID: `PERF-01`

## Intended Use
Use `PERF-01` as a structured 12-minute session. Run in a quiet setting with headphones.

## Phase Structure
- Phase 1: `Ground` (`0s` to `180s`) - Establish baseline calm
- Phase 2: `Sharpen` (`180s` to `540s`) - Narrow attention, increase alertness
- Phase 3: `Lock` (`540s` to `720s`) - Stable ready state

## Audio Layers
- `noise_bed`
- `binaural`
- `pulse_cues`

## Render
```bash
cd /Users/jdarrow/workspace/meditation/protocol-lab/tools
python3 render_protocol.py ../protocols/PERF/specs/PERF-01_12m.yaml --out_dir ../protocols/PERF/renders
```

## Narration
- Coaching script: `/Users/jdarrow/workspace/meditation/protocol-lab/protocols/PERF/narration/PERF-01_coaching.md`

## Safety
- Do not use while driving or operating machinery.
- Stop immediately if distress escalates.
- Use conservative volume levels.
