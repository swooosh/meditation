# SUN Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Noise Bed]
  L1 --> M[Mix Bus]
  P --> L2[Binaural]
  L2 --> M[Mix Bus]
  P --> L3[Breath Cues]
  L3 --> M[Mix Bus]
  P --> L4[Pulse Cues]
  L4 --> M[Mix Bus]
  P --> L5[Spatial Sweep]
  L5 --> M[Mix Bus]
  P --> L6[Harmonic Pad]
  L6 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `noise_bed` | 3/3 specs |
| `binaural` | 3/3 specs |
| `breath_cues` | 3/3 specs |
| `pulse_cues` | 3/3 specs |
| `spatial_sweep` | 2/3 specs |
| `harmonic_pad` | 1/3 specs |

