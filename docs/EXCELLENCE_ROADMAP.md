# Excellence Roadmap

This roadmap defines concrete upgrades for specs, audio rendering, and narration quality.

## 1) Spec Quality Bar

Every protocol spec should encode design intent, not only render instructions.

Required:
- Complete phase semantics: each phase must include `name`, `start_s`, `end_s`, and `intent`.
- Breath consistency: `breath_pattern` and `breath_cues` should agree.
- Identity consistency: signature tones and family tag present where appropriate.
- Deterministic render settings: `render.sr`, `render.seed`, `peak_norm`.

Validation:
- Run: `python3 /Users/jdarrow/workspace/meditation/protocol-lab/tools/validate_specs.py`
- CI recommendation: fail build on validator errors; optionally use `--strict`.

## 2) Audio Engine Upgrades

### A. Render Fidelity and Dynamics
- Add loudness targets by family (LUFS envelopes, not only peak normalization).
- Add per-phase dynamics profiles so transitions are intentionally sculpted.
- Add headroom policy per layer type to prevent cumulative masking in dense mixes.

### B. Spatial and Somatic Precision
- Introduce trajectory-based panning primitives (continuous path APIs).
- Add stateful room model with phase-dependent width/depth (not one static room setting).
- Expand low-frequency management: phase-aligned sub and anti-mud filtering.

### C. Breath and Cue Intelligence
- Add cue shaping by practice level (beginner/intermediate/advanced cue salience).
- Add adaptive cue timing options (fixed vs interval-jitter vs phase-aware density).
- Expose cue motifs as reusable presets for cross-family consistency.

### D. Quality Control Automation
- Add render QC for:
  - duration completeness
  - clipping and crest-factor bands
  - spectral balance drift by phase
  - silence ratio anomalies
- Emit machine-readable QC artifacts for website availability and release gating.

## 3) Narration Guide Upgrades

### A. Structural Standard
Each narration script should include:
- opening orientation
- phase-by-phase coaching
- contingency prompts (overactivation, dissociation, numbness, distraction)
- explicit close and integration instructions

### B. Voice and Delivery
- Define family-specific narration voice profiles (clinical, contemplative, performance, somatic).
- Add pacing marks (`pause`, `slow`, `soften`) for spoken delivery realism.
- Add optional short and long script variants per protocol.

### C. Synchronization
- Align narration checkpoints with phase transitions and cue motifs.
- Add optional narration event metadata (`time_s`, `intent`, `delivery_style`) in specs.
- Generate cue-aligned rehearsal transcripts from spec + narration metadata.

## 4) Implementation Sequence

1. Enforce spec validator in workflow (`tools/validate_specs.py`).
2. Add QC artifact generation from renderer and wire it to web render-status manifest.
3. Introduce narration schema + template and migrate all scripts.
4. Add loudness and dynamics controls to renderer.
5. Add trajectory/spatial and breath-cue preset system.

## 5) Definition of Done

A protocol is release-ready only when:
- spec passes validation
- narration passes schema checks
- render passes QC thresholds
- docs and website availability status are synced
- protocol has a complete-length master render
