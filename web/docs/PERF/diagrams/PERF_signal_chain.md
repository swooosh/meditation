# PERF Signal Chain

Family-level audio chain showing layer families, mix bus, mastering, and QC gates.

```mermaid
flowchart LR
  S[Spec YAML] --> P[Phase Scheduler]
  P --> L1[Noise Bed]
  L1 --> M[Mix Bus]
  P --> L2[Binaural]
  L2 --> M[Mix Bus]
  P --> L3[Pulse Cues]
  L3 --> M[Mix Bus]
  P --> L4[Breath Cues]
  L4 --> M[Mix Bus]
  P --> L5[Resolution Cues]
  L5 --> M[Mix Bus]
  M --> A[Mastering: tilt, width, low-end management]
  A --> Q[QC: amplitude + spectral by phase]
  Q --> W[Master WAV]
```

| Layer Type | Presence |
|---|---:|
| `noise_bed` | 3/3 specs |
| `binaural` | 3/3 specs |
| `pulse_cues` | 2/3 specs |
| `breath_cues` | 1/3 specs |
| `resolution_cues` | 1/3 specs |

